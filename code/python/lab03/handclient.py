"""Lab 03: Hand-Client – JSON-RPC-Nachrichten an einen MCP-Server schicken und die Antworten lesen.

Startet den Server als Unterprozess (Transport stdio) und zeigt jede Nachricht roh und formatiert.

Aufruf:  uv run lab03/handclient.py                       (Server: lab03/mini_server.py)
         uv run lab03/handclient.py lab04/schulserver.py  (anderer Server)

Eingaben:  Nummer   → Nachricht aus lab03/nachrichten.txt schicken
           j        → eigene JSON-Zeile eingeben
           l        → Liste der Nachrichten anzeigen
           q        → beenden
"""

import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

HIER = Path(__file__).resolve().parent
SERVER = Path(sys.argv[1]) if len(sys.argv) > 1 else HIER / "mini_server.py"


def lade_nachrichten() -> list[tuple[str, str]]:
    """Liest (Beschreibung, JSON-Zeile) aus nachrichten.txt."""
    eintraege, titel = [], ""
    for zeile in (HIER / "nachrichten.txt").read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if zeile.startswith("#"):
            titel = zeile.lstrip("# ").strip()
        elif zeile:
            eintraege.append((titel, zeile))
    return eintraege


def lies_ausgabe(strom, ziel: queue.Queue) -> None:
    for zeile in strom:
        ziel.put(zeile)


def main() -> None:
    prozess = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, encoding="utf-8", bufsize=1,
    )
    antworten: queue.Queue = queue.Queue()
    threading.Thread(target=lies_ausgabe, args=(prozess.stdout, antworten), daemon=True).start()
    nachrichten = lade_nachrichten()

    def liste() -> None:
        for nummer, (titel, text) in enumerate(nachrichten, 1):
            methode = json.loads(text).get("method", "?")
            print(f"  {nummer:>2}  {methode:<28} {titel}")

    print(f"Server gestartet: {SERVER.name} (stdio)\n")
    liste()
    while True:
        eingabe = input("\nNummer, j(son), l(iste) oder q: ").strip().lower()
        if eingabe in ("q", "quit", "exit"):
            break
        if eingabe == "l":
            liste()
            continue
        if eingabe == "j":
            text = input("JSON: ").strip()
        elif eingabe.isdigit() and 1 <= int(eingabe) <= len(nachrichten):
            text = nachrichten[int(eingabe) - 1][1]
        else:
            continue
        try:
            json.loads(text)
        except json.JSONDecodeError as fehler:
            print(f"Kein gültiges JSON: {fehler}")
            continue

        print(f"\n→ gesendet:\n{text}")
        prozess.stdin.write(text + "\n")
        prozess.stdin.flush()

        if "id" not in json.loads(text):
            print("(Benachrichtigung ohne id – der Server antwortet nicht)")
            continue
        try:
            roh = antworten.get(timeout=15)
        except queue.Empty:
            print("(keine Antwort nach 15 s)")
            continue
        print(f"\n← empfangen (roh):\n{roh.strip()[:300]}{' …' if len(roh) > 300 else ''}")
        print(f"\n← empfangen (formatiert):\n{json.dumps(json.loads(roh), indent=2, ensure_ascii=False)}")

    prozess.terminate()


if __name__ == "__main__":
    main()
