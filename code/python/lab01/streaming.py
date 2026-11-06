"""Lab 01, Ausbau: Die Antwort Stück für Stück anzeigen (Streaming).

Aufruf:  uv run lab01/streaming.py
         uv run lab01/streaming.py "Ihre eigene Frage"
"""

import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
modell = os.environ["LLM_MODEL"]
extra = {"reasoning_effort": os.environ["LLM_REASONING_EFFORT"]} if os.environ.get("LLM_REASONING_EFFORT") else {}

frage = sys.argv[1] if len(sys.argv) > 1 else "Schreibe ein kurzes Gedicht über einen Computerraum."

start = time.perf_counter()
erstes_stueck = None
# stream=True: Der Server schickt die Antwort in vielen kleinen Stücken ("chunks").
stream = client.chat.completions.create(
    model=modell, messages=[{"role": "user", "content": frage}], stream=True, **extra
)
for stueck in stream:
    if not stueck.choices:
        continue
    text = stueck.choices[0].delta.content or ""
    if text and erstes_stueck is None:
        erstes_stueck = time.perf_counter() - start
    print(text, end="", flush=True)

gesamt = time.perf_counter() - start
print(f"\n\n--- erstes Stück nach {erstes_stueck or 0:.1f} s, fertig nach {gesamt:.1f} s")
