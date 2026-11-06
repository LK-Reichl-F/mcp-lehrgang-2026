"""Restguthaben des eigenen OpenRouter-Schlüssels anzeigen.

Aufruf:  uv run guthaben.py

Liest LLM_BASE_URL und LLM_API_KEY aus der Datei .env.
Funktioniert nur mit OpenRouter (bei Ollama gibt es kein Guthaben).
"""

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()

basis = os.environ.get("LLM_BASE_URL", "").rstrip("/")
schluessel = os.environ.get("LLM_API_KEY", "")

if "openrouter.ai" not in basis:
    raise SystemExit(f"LLM_BASE_URL zeigt nicht auf OpenRouter ({basis or 'nicht gesetzt'}) – lokal gibt es kein Guthaben.")

anfrage = urllib.request.Request(f"{basis}/key", headers={"Authorization": f"Bearer {schluessel}"})
try:
    with urllib.request.urlopen(anfrage, timeout=15) as antwort:
        daten = json.load(antwort)["data"]
except urllib.error.HTTPError as fehler:
    raise SystemExit(f"Fehler {fehler.code}: Schlüssel ungültig, abgelaufen oder abgeschaltet?")


def dollar(wert):
    return "unbegrenzt" if wert is None else f"{wert:.4f} $"


print(f"Schlüssel:      {daten.get('label', '?')}")
print(f"Limit:          {dollar(daten.get('limit'))}")
print(f"Verbraucht:     {dollar(daten.get('usage'))}")
print(f"Restguthaben:   {dollar(daten.get('limit_remaining'))}")
gratis = daten.get("free_model_daily_requests") or {}
if gratis:
    print(f"Gratis-Modelle heute: {gratis.get('used', '?')} von {gratis.get('limit', '?')} Anfragen genutzt")
