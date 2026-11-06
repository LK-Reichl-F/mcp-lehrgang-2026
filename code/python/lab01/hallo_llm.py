"""Lab 01, Schritt 2: Die erste Anfrage an ein Sprachmodell aus Python.

Aufruf:  uv run lab01/hallo_llm.py
         uv run lab01/hallo_llm.py "Ihre eigene Frage"
"""

import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

# 1. Konfiguration aus der Datei .env lesen
load_dotenv()
client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],  # wohin geht die Anfrage? (Ollama, OpenRouter, …)
    api_key=os.environ["LLM_API_KEY"],  # Schlüssel (Ollama: beliebiger Text)
)
modell = os.environ["LLM_MODEL"]

# Denkmodus abschalten, falls in .env gewünscht (LLM_REASONING_EFFORT=none)
extra = {}
if os.environ.get("LLM_REASONING_EFFORT"):
    extra["reasoning_effort"] = os.environ["LLM_REASONING_EFFORT"]

# 2. Die Frage: aus der Kommandozeile oder ein Beispiel
frage = sys.argv[1] if len(sys.argv) > 1 else "Erkläre in zwei Sätzen, was ein Sprachmodell ist."

# 3. Anfrage schicken: eine Liste von Nachrichten mit Rolle und Inhalt
start = time.perf_counter()
antwort = client.chat.completions.create(
    model=modell,
    messages=[{"role": "user", "content": frage}],
    **extra,
)
dauer = time.perf_counter() - start

# 4. Antwort auswerten
print(antwort.choices[0].message.content)
print()
print(f"--- Modell: {antwort.model} | {dauer:.1f} s | "
      f"Tokens: {antwort.usage.prompt_tokens} hinein, {antwort.usage.completion_tokens} heraus")
