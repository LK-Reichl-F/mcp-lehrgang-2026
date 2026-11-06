"""Lab 01, Schritt 4: Strukturierte Ausgabe – einen Termin aus Freitext als JSON gewinnen.

Aufruf:  uv run lab01/termin_extrahieren.py text      (nur im Prompt um JSON bitten)
         uv run lab01/termin_extrahieren.py json      (JSON-Modus)
         uv run lab01/termin_extrahieren.py schema    (JSON-Schema vorgeben)

Optional als zweites Argument ein eigener Text:
         uv run lab01/termin_extrahieren.py json "Morgen um 8 Uhr Wandertag, Treffpunkt Bahnhof"
"""

import datetime
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
modell = os.environ["LLM_MODEL"]
extra = {"reasoning_effort": os.environ["LLM_REASONING_EFFORT"]} if os.environ.get("LLM_REASONING_EFFORT") else {}

modus = sys.argv[1] if len(sys.argv) > 1 else "json"
text = sys.argv[2] if len(sys.argv) > 2 else (
    "Am kommenden Donnerstag um 15 Uhr treffen wir uns zur Fachsitzung Informatik im Raum IN1."
)

# Das Modell kennt das heutige Datum nicht – wir geben es im Systemprompt mit.
heute = datetime.date.today()
wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
systemprompt = f"Heute ist {wochentage[heute.weekday()]}, der {heute.isoformat()}."

# Das JSON-Schema beschreibt, welche Felder wir erwarten.
SCHEMA = {
    "type": "object",
    "properties": {
        "datum": {"type": "string", "description": "Datum im Format JJJJ-MM-TT"},
        "uhrzeit": {"type": "string", "description": "Uhrzeit im Format HH:MM"},
        "titel": {"type": "string"},
        "ort": {"type": "string"},
    },
    "required": ["datum", "uhrzeit", "titel", "ort"],
}
FORMAT_HINWEIS = "Antworte nur mit JSON mit den Feldern datum (JJJJ-MM-TT), uhrzeit (HH:MM), titel und ort."

nachrichten = [{"role": "system", "content": systemprompt}]
if modus == "text":
    nachrichten.append({"role": "user", "content": f"Extrahiere den Termin. {FORMAT_HINWEIS}\n\n{text}"})
    format_option = {}
elif modus == "json":
    nachrichten.append({"role": "user", "content": f"Extrahiere den Termin. {FORMAT_HINWEIS}\n\n{text}"})
    format_option = {"response_format": {"type": "json_object"}}
elif modus == "schema":
    nachrichten.append({"role": "user", "content": f"Extrahiere den Termin.\n\n{text}"})
    format_option = {"response_format": {"type": "json_schema", "json_schema": {"name": "termin", "schema": SCHEMA}}}
else:
    sys.exit("Modus muss 'text', 'json' oder 'schema' sein.")

antwort = client.chat.completions.create(model=modell, messages=nachrichten, **format_option, **extra)
roh = antwort.choices[0].message.content
print(f"Modus: {modus} | Modell: {antwort.model}")
print(f"Rohe Antwort:\n{roh}\n")

# 1. Prüfung: Ist es überhaupt JSON?
try:
    termin = json.loads(roh)
except json.JSONDecodeError as fehler:
    sys.exit(f"KEIN gültiges JSON: {fehler}")
print("[ok] gültiges JSON")

# 2. Prüfung: Sind alle Felder da?
fehlend = [feld for feld in SCHEMA["required"] if feld not in termin]
if fehlend:
    sys.exit(f"Es fehlen Felder: {fehlend}")
print("[ok] alle Felder vorhanden")

# 3. Prüfung: Ist der Inhalt plausibel? (Das Schema garantiert nur die Form, nicht die Richtigkeit!)
try:
    datum = datetime.date.fromisoformat(termin["datum"])
    datetime.time.fromisoformat(termin["uhrzeit"])
except ValueError as fehler:
    sys.exit(f"Inhalt nicht plausibel: {fehler}")
print(f"[ok] Datum und Uhrzeit lesbar: {wochentage[datum.weekday()]}, {datum:%d.%m.%Y}, {termin['uhrzeit']} Uhr")
print(f"     {termin['titel']} – {termin['ort']}")

# 4. Prüfung: Passt der Wochentag im Text zum berechneten Datum?
#    Sprachmodelle verrechnen sich bei Datumsangaben erstaunlich oft.
genannt = [tag for tag in wochentage if tag.lower() in text.lower()]
if genannt and genannt[0] != wochentage[datum.weekday()]:
    print(f"[WARNUNG] Im Text steht „{genannt[0]}“, der {datum:%d.%m.%Y} ist aber ein {wochentage[datum.weekday()]}!")
elif genannt:
    print(f"[ok] Wochentag passt ({genannt[0]})")
