"""Lab 02, Schritt 5: Welches Modell schafft es? – fünf feste Aufgaben zum Tool Calling.

Aufruf:  uv run lab02/modelltest.py                       (Modell aus .env, Werkzeuge Version 1)
         uv run lab02/modelltest.py --version 2           (Werkzeuge Version 2, relative Datumsangaben)
         uv run lab02/modelltest.py --modelle qwen3.5:4b,qwen3.5:9b --wiederholungen 3

Alle Aufgaben beziehen sich auf Montag, 9.11.2026 (simuliertes Datum).
"""

import argparse
import os
import statistics
import time

os.environ["HEUTE"] = "2026-11-09"  # vor dem Import setzen: alle Aufgaben gelten für diesen Tag

from dotenv import load_dotenv  # noqa: E402
from openai import OpenAI  # noqa: E402

load_dotenv()

AUFGABEN = [
    {
        "frage": "Wie spät ist es gerade?",
        "tools": ["aktuelle_uhrzeit"],          # diese Tools müssen aufgerufen werden
        "keine_tools": False,
        "woerter": [],                          # diese Wörter müssen in der Antwort stehen
    },
    {
        "frage": "Fällt am 10.11.2026 bei der 7a etwas aus?",
        "tools": ["vertretungsplan"],
        "keine_tools": False,
        "woerter": ["Deutsch"],
    },
    {
        "frage": "Was ist morgen bei der 10a los?",
        "tools": ["vertretungsplan"],
        "keine_tools": False,
        "woerter": ["IN2"],
    },
    {
        "frage": "Wie viel ist 12 mal 12?",
        "tools": [],
        "keine_tools": True,                    # hier soll das Modell KEIN Tool aufrufen
        "woerter": ["144"],
    },
    {
        "frage": "Gibt es am 11.11.2026 bei der 8b und der 9c Änderungen?",
        "tools": ["vertretungsplan"],
        "keine_tools": False,
        "woerter": ["Sport", "Mathematik"],
    },
]


def bewerte(aufgabe: dict, ergebnis: dict) -> tuple[bool, str]:
    """Prüft Tool-Aufrufe und Antwort. Gibt (bestanden, Begründung) zurück."""
    aufgerufen = [p["name"] for p in ergebnis["protokoll"]]
    if aufgabe["keine_tools"] and aufgerufen:
        return False, f"unnötiger Tool-Aufruf: {aufgerufen}"
    for name in aufgabe["tools"]:
        if name not in aufgerufen:
            return False, f"Tool '{name}' nicht aufgerufen"
    fehler = [p for p in ergebnis["protokoll"] if "fehler" in p["ergebnis"]]
    if fehler:
        return False, f"Tool-Fehler: {fehler[0]['ergebnis']['fehler'][:60]}"
    antwort = ergebnis["antwort"].lower()
    for wort in aufgabe["woerter"]:
        if wort.lower() not in antwort:
            return False, f"'{wort}' fehlt in der Antwort"
    return True, "ok"


def main() -> None:
    parser = argparse.ArgumentParser(description="Tool-Calling-Test für Sprachmodelle")
    parser.add_argument("--version", type=int, choices=[1, 2], default=1, help="Werkzeuge aus tool_calling.py (1) oder tool_calling_v2.py (2)")
    parser.add_argument("--modelle", default=os.environ["LLM_MODEL"], help="kommagetrennte Modellnamen (gleicher Server)")
    parser.add_argument("--wiederholungen", type=int, default=1, help="wie oft jede Aufgabe gestellt wird")
    args = parser.parse_args()

    if args.version == 1:
        import tool_calling as werkzeuge
    else:
        import tool_calling_v2 as werkzeuge

    client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
    extra = {"reasoning_effort": os.environ["LLM_REASONING_EFFORT"]} if os.environ.get("LLM_REASONING_EFFORT") else {}

    print(f"Server: {os.environ['LLM_BASE_URL']} | Werkzeuge: Version {args.version} | "
          f"Wiederholungen: {args.wiederholungen}\n")
    zusammenfassung = []
    for modell in [m.strip() for m in args.modelle.split(",") if m.strip()]:
        print(f"=== {modell}")
        bestanden_gesamt, zeiten, geantwortet = 0, [], set()
        for nummer, aufgabe in enumerate(AUFGABEN, 1):
            treffer = 0
            for _ in range(args.wiederholungen):
                start = time.perf_counter()
                try:
                    ergebnis = werkzeuge.frage_stellen(client, modell, aufgabe["frage"], extra, ausgabe=False)
                    ok, grund = bewerte(aufgabe, ergebnis)
                    geantwortet |= ergebnis["modelle"]
                except Exception as fehler:  # z. B. Ratenlimit oder Modell ohne Tool-Unterstützung
                    ok, grund = False, f"Fehler: {type(fehler).__name__}"
                zeiten.append(time.perf_counter() - start)
                treffer += ok
            bestanden_gesamt += treffer
            zeichen = "✔" if treffer == args.wiederholungen else ("✘" if treffer == 0 else "~")
            print(f"  {zeichen} {nummer}. {aufgabe['frage']:<58} {treffer}/{args.wiederholungen}  {'' if ok else grund}")
        gesamt = len(AUFGABEN) * args.wiederholungen
        print(f"  → {bestanden_gesamt}/{gesamt} bestanden, Ø {statistics.mean(zeiten):.1f} s pro Aufgabe")
        if len(geantwortet) > 1 or (geantwortet and modell not in geantwortet):
            print(f"  → tatsächlich geantwortet haben: {', '.join(sorted(geantwortet))}")
        print()
        zusammenfassung.append((modell, bestanden_gesamt, gesamt, statistics.mean(zeiten)))

    print("Zusammenfassung")
    print(f"{'Modell':<40} {'bestanden':>10} {'Ø Zeit':>8}")
    for modell, bestanden, gesamt, zeit in zusammenfassung:
        print(f"{modell:<40} {bestanden:>4}/{gesamt:<5} {zeit:>6.1f} s")


if __name__ == "__main__":
    main()
