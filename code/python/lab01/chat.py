"""Lab 01, Schritt 3: Ein Chat mit Verlauf und Systemprompt.

Aufruf:  uv run lab01/chat.py

Befehle im Chat:
  /verlauf   zeigt die Nachrichtenliste, die an das Modell geschickt wird
  /neu       löscht den Verlauf (der Systemprompt bleibt)
  /ende      beendet das Programm
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
modell = os.environ["LLM_MODEL"]
extra = {"reasoning_effort": os.environ["LLM_REASONING_EFFORT"]} if os.environ.get("LLM_REASONING_EFFORT") else {}

SYSTEMPROMPT = (
    "Du bist der freundliche Schul-Assistent der Staatlichen Musterschule. "
    "Du antwortest kurz, sachlich und auf Deutsch. "
    "Wenn du etwas nicht sicher weißt, sagst du das ehrlich."
)

# Der Verlauf ist eine ganz normale Liste. Das Modell selbst merkt sich NICHTS –
# bei jeder Anfrage schicken wir die komplette Liste erneut mit.
verlauf = [{"role": "system", "content": SYSTEMPROMPT}]

print("Schul-Assistent – Befehle: /verlauf, /neu, /ende\n")
while True:
    eingabe = input("Sie: ").strip()
    if not eingabe:
        continue
    if eingabe == "/ende":
        break
    if eingabe == "/neu":
        verlauf = verlauf[:1]
        print("(Verlauf gelöscht)\n")
        continue
    if eingabe == "/verlauf":
        print(json.dumps(verlauf, indent=2, ensure_ascii=False), "\n")
        continue

    verlauf.append({"role": "user", "content": eingabe})
    antwort = client.chat.completions.create(model=modell, messages=verlauf, **extra)
    text = antwort.choices[0].message.content

    # Die Antwort des Modells gehört ebenfalls in den Verlauf (Rolle "assistant").
    verlauf.append({"role": "assistant", "content": text})
    print(f"Assistent: {text}")
    print(f"           [{antwort.model}, {antwort.usage.prompt_tokens} Tokens hinein]\n")
