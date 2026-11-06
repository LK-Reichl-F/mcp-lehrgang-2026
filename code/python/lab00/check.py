"""Prüft, ob die Arbeitsumgebung für den Lehrgang bereit ist.

Aufruf (im Ordner code/python):  uv run lab00/check.py
"""

import importlib.metadata
import os
import sys
import time
from pathlib import Path

OK = "  [ok]    "
FEHLER = "  [FEHLER]"
HINWEIS = "  [Hinweis]"

print("Prüfe die Arbeitsumgebung …\n")

# 1. Python-Version
v = sys.version_info
print(f"{OK if v >= (3, 12) else FEHLER} Python {v.major}.{v.minor}.{v.micro}")

# 2. Bibliotheken
for paket in ["openai", "mcp", "python-dotenv"]:
    try:
        print(f"{OK} {paket} {importlib.metadata.version(paket)}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{FEHLER} {paket} fehlt – bitte im Ordner code/python 'uv sync' ausführen")

# 3. Konfiguration
env_datei = Path(__file__).resolve().parent.parent / ".env"
if not env_datei.exists():
    sys.exit(f"{FEHLER} Datei .env fehlt – bitte '.env.example' nach '.env' kopieren (siehe Lab 00, Schritt 4)")

from dotenv import load_dotenv  # noqa: E402  (erst nach der Paketprüfung importieren)

load_dotenv(env_datei)
basis = os.environ.get("LLM_BASE_URL", "")
modell = os.environ.get("LLM_MODEL", "")
print(f"{OK} .env gefunden: LLM_BASE_URL={basis}  LLM_MODEL={modell}")

# 4. Sprachmodell erreichbar?
from openai import APIConnectionError, APIStatusError, OpenAI  # noqa: E402

client = OpenAI(base_url=basis, api_key=os.environ.get("LLM_API_KEY", "leer"))
try:
    verfuegbar = [m.id for m in client.models.list()]
    print(f"{OK} Server erreichbar, {len(verfuegbar)} Modell(e) verfügbar")
    if "localhost" in basis and modell not in verfuegbar:
        sys.exit(f"{FEHLER} Modell '{modell}' ist nicht geladen – bitte 'ollama pull {modell}' ausführen")
except APIConnectionError:
    if "localhost" in basis:
        sys.exit(f"{FEHLER} Keine Verbindung zu {basis} – läuft Ollama? (Ollama-App starten oder 'ollama serve')")
    sys.exit(f"{FEHLER} Keine Verbindung zu {basis} – Internetverbindung prüfen")
except APIStatusError as fehler:
    sys.exit(f"{FEHLER} Server antwortet mit Fehler {fehler.status_code} – Schlüssel (LLM_API_KEY) prüfen")

# 5. Eine kurze Anfrage
extra = {}
if os.environ.get("LLM_REASONING_EFFORT"):
    extra["reasoning_effort"] = os.environ["LLM_REASONING_EFFORT"]

print("\nSchicke eine kurze Testanfrage (beim ersten Mal lädt Ollama das Modell, das kann dauern) …")
start = time.perf_counter()
try:
    antwort = client.chat.completions.create(
        model=modell,
        messages=[{"role": "user", "content": "Antworte nur mit dem Wort: Bereit"}],
        **extra,
    )
except APIStatusError as fehler:
    sys.exit(f"{FEHLER} Anfrage abgelehnt ({fehler.status_code}): {fehler.message}")
dauer = time.perf_counter() - start

text = (antwort.choices[0].message.content or "").strip()
print(f"{OK} Antwort nach {dauer:.1f} s: {text!r}")
print(f"{OK} Geantwortet hat: {antwort.model}")
if dauer > 30:
    print(f"{HINWEIS} Das war langsam. Falls es so bleibt: auf den Kursschlüssel (OpenRouter) umsteigen.")
print("\nAlles bereit!")
