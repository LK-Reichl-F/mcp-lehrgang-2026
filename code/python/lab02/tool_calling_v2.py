"""Lab 02, Schritt 4: Version 2 – das Werkzeug rechnet das Datum selbst aus.

Unterschied zu tool_calling.py: vertretungsplan() versteht auch "heute", "morgen", "übermorgen"
und Wochentage. Das Modell muss kein Datum mehr berechnen – eine typische Fehlerquelle fällt weg.

Aufruf:  uv run lab02/tool_calling_v2.py "Fällt morgen bei der 7a etwas aus?"

Optional in .env oder vor dem Aufruf:
  HEUTE=2026-11-09   simuliert ein Datum (die Beispieldaten gelten für 9.–13.11.2026)
"""

import csv
import datetime
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
DATEN = Path(__file__).resolve().parent.parent / "daten"
WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MAX_RUNDEN = 5  # Schutz vor Endlosschleifen


# ---------------------------------------------------------------------------
# 1. Die Werkzeuge: ganz normale Python-Funktionen
# ---------------------------------------------------------------------------

def jetzt() -> datetime.datetime:
    """Aktuelle Zeit – oder das simulierte Datum aus der Umgebungsvariable HEUTE."""
    echt = datetime.datetime.now()
    if os.environ.get("HEUTE"):
        tag = datetime.date.fromisoformat(os.environ["HEUTE"])
        return datetime.datetime.combine(tag, echt.time())
    return echt


def aktuelle_uhrzeit() -> dict:
    """Liefert Datum, Wochentag und Uhrzeit."""
    t = jetzt()
    return {"datum": t.date().isoformat(), "wochentag": WOCHENTAGE[t.weekday()], "uhrzeit": t.strftime("%H:%M")}


def datum_aufloesen(angabe: str) -> datetime.date:
    """'heute', 'morgen', 'übermorgen', 'Donnerstag' oder 'JJJJ-MM-TT' → konkretes Datum."""
    heute = jetzt().date()
    angabe = angabe.strip().lower()
    relativ = {"heute": 0, "morgen": 1, "übermorgen": 2, "uebermorgen": 2}
    if angabe in relativ:
        return heute + datetime.timedelta(days=relativ[angabe])
    for nummer, tag in enumerate(WOCHENTAGE):
        if angabe == tag.lower():  # nächster solcher Wochentag (heute zählt nicht)
            return heute + datetime.timedelta(days=(nummer - heute.weekday() - 1) % 7 + 1)
    return datetime.date.fromisoformat(angabe)  # wirft ValueError bei Unsinn


def vertretungsplan(klasse: str, datum: str) -> dict:
    """Liefert Vertretungen, Entfälle und Raumänderungen einer Klasse an einem Tag."""
    try:
        tag = datum_aufloesen(datum)
    except ValueError:
        return {"fehler": f"Unbekanntes Datum '{datum}'. Erlaubt: heute, morgen, übermorgen, Wochentag oder JJJJ-MM-TT."}
    klasse = klasse.strip().lower()
    with open(DATEN / "vertretungsplan.csv", encoding="utf-8") as datei:
        eintraege = [z for z in csv.DictReader(datei) if z["klasse"].lower() == klasse and z["datum"] == tag.isoformat()]
    ergebnis = {"klasse": klasse, "datum": tag.isoformat(), "wochentag": WOCHENTAGE[tag.weekday()], "eintraege": eintraege}
    if not eintraege:
        ergebnis["hinweis"] = "Keine Änderungen – Unterricht nach Plan."
    return ergebnis


# ---------------------------------------------------------------------------
# 2. Die Beschreibung der Werkzeuge für das Sprachmodell (JSON-Schema)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "aktuelle_uhrzeit",
            "description": "Liefert das heutige Datum, den Wochentag und die Uhrzeit. "
                           "Nutze das Tool, wenn die Frage 'heute', 'morgen' oder einen Wochentag enthält.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "vertretungsplan",
            "description": "Liefert Vertretungen, Entfälle und Raumänderungen einer Klasse an einem Tag. "
                           "Das Datum darf auch relativ angegeben werden – das Werkzeug rechnet es selbst aus.",
            "parameters": {
                "type": "object",
                "properties": {
                    "klasse": {"type": "string", "description": "Name der Klasse, z. B. 7a oder 10a"},
                    "datum": {"type": "string",
                              "description": "'heute', 'morgen', 'übermorgen', ein Wochentag (z. B. 'Donnerstag') "
                                             "oder ein Datum im Format JJJJ-MM-TT"},
                },
                "required": ["klasse", "datum"],
            },
        },
    },
]

# Welcher Name gehört zu welcher Funktion?
FUNKTIONEN = {"aktuelle_uhrzeit": aktuelle_uhrzeit, "vertretungsplan": vertretungsplan}

SYSTEMPROMPT = (
    "Du bist der Schul-Assistent der Staatlichen Musterschule. Antworte kurz und auf Deutsch. "
    "Nutze die Werkzeuge, um Fragen zu Datum und Vertretungsplan zu beantworten. Erfinde keine Daten."
)


# ---------------------------------------------------------------------------
# 3. Ein Werkzeug ausführen – mit Fehlerbehandlung
# ---------------------------------------------------------------------------

def fuehre_aus(name: str, argumente_json: str) -> dict:
    """Führt den gewünschten Tool-Aufruf aus. Fehler gehen als Ergebnis zurück an das Modell."""
    if name not in FUNKTIONEN:
        return {"fehler": f"Unbekanntes Werkzeug '{name}'."}
    try:
        argumente = json.loads(argumente_json or "{}")
    except json.JSONDecodeError:
        return {"fehler": f"Argumente sind kein gültiges JSON: {argumente_json!r}"}
    try:
        return FUNKTIONEN[name](**argumente)
    except TypeError as fehler:
        return {"fehler": f"Falsche Argumente für '{name}': {fehler}"}


# ---------------------------------------------------------------------------
# 4. Die Agentenschleife
# ---------------------------------------------------------------------------

def frage_stellen(client: OpenAI, modell: str, frage: str, extra: dict, ausgabe: bool = True) -> dict:
    """Fragt das Modell so lange, bis es ohne Tool-Aufruf antwortet. Gibt Antwort und Protokoll zurück."""
    nachrichten = [{"role": "system", "content": SYSTEMPROMPT}, {"role": "user", "content": frage}]
    protokoll = []  # alle Tool-Aufrufe, für Auswertung und Modelltest
    modelle = set()

    for runde in range(1, MAX_RUNDEN + 1):
        antwort = client.chat.completions.create(model=modell, messages=nachrichten, tools=TOOLS, **extra)
        modelle.add(antwort.model)
        nachricht = antwort.choices[0].message

        # Fall A: keine Tool-Aufrufe → das ist die Endantwort
        if not nachricht.tool_calls:
            return {"antwort": nachricht.content or "", "protokoll": protokoll, "modelle": modelle, "runden": runde}

        # Fall B: Das Modell möchte Werkzeuge nutzen. Seine Nachricht kommt in den Verlauf …
        nachrichten.append({
            "role": "assistant",
            "content": nachricht.content or "",
            "tool_calls": [
                {"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}}
                for t in nachricht.tool_calls
            ],
        })
        # … und WIR führen jedes gewünschte Werkzeug aus und hängen das Ergebnis an.
        for aufruf in nachricht.tool_calls:
            ergebnis = fuehre_aus(aufruf.function.name, aufruf.function.arguments)
            protokoll.append({"name": aufruf.function.name, "argumente": aufruf.function.arguments, "ergebnis": ergebnis})
            if ausgabe:
                print(f"  [Runde {runde}] Modell möchte: {aufruf.function.name}({aufruf.function.arguments})")
                print(f"             Ergebnis: {json.dumps(ergebnis, ensure_ascii=False)[:200]}")
            nachrichten.append({
                "role": "tool",
                "tool_call_id": aufruf.id,
                "content": json.dumps(ergebnis, ensure_ascii=False),
            })

    return {"antwort": "(Abbruch: zu viele Runden)", "protokoll": protokoll, "modelle": modelle, "runden": MAX_RUNDEN}


def main() -> None:
    client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
    modell = os.environ["LLM_MODEL"]
    extra = {"reasoning_effort": os.environ["LLM_REASONING_EFFORT"]} if os.environ.get("LLM_REASONING_EFFORT") else {}
    if os.environ.get("HEUTE"):
        print(f"(Simuliertes Datum: {os.environ['HEUTE']})")

    fragen = sys.argv[1:]
    interaktiv = not fragen
    if interaktiv:
        print("Schul-Assistent mit Werkzeugen – Beenden mit /ende\n")
    while True:
        frage = fragen.pop(0) if fragen else (input("Sie: ").strip() if interaktiv else None)
        if not frage or frage == "/ende":
            break
        if not interaktiv:
            print(f"Sie: {frage}")
        ergebnis = frage_stellen(client, modell, frage, extra)
        print(f"Assistent: {ergebnis['antwort']}")
        print(f"           [{', '.join(sorted(ergebnis['modelle']))}, {ergebnis['runden']} Runde(n)]\n")


if __name__ == "__main__":
    main()
