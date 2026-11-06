# Sprachmodelle programmieren – Tool Calling & MCP

Dateien zum Lehrgang der ALP Dillingen, 9.–11.11.2026: Programme, die Sprachmodelle (LLMs) ansprechen, Tools bereitstellen
und das **Model Context Protocol (MCP)** nutzen. Die Sprachmodelle laufen lokal mit **Ollama**; als Ausweichlösung dient
**OpenRouter**.

> **Begleitkurs auf der ByCS-Lernplattform:** Arbeitsaufträge, Folien, Forum, Austauschverzeichnis und Musterlösungen
> finden Sie im Selbstlernkurs auf [lernplattform.bycs.de](https://lernplattform.bycs.de) – direkt erreichbar über
> **[bycs.link/reichl](https://bycs.link/reichl)** (ab 9.11.2026). Den Einschreibeschlüssel erhalten Sie im Lehrgang.
>
> Dieses Repository enthält nur die Dateien, die Sie auf Ihren Rechner herunterladen und dort bearbeiten.

## Herunterladen

- **Ohne git:** oben auf **Code → Download ZIP** klicken und das Archiv entpacken.
- **Mit git:**

  ```bash
  git clone https://github.com/LK-Reichl-F/mcp-lehrgang-2026.git
  ```

## Einrichten

Voraussetzung ist [uv](https://docs.astral.sh/uv/). Die Installation von uv, Ollama und den übrigen Werkzeugen
beschreibt der Reiter **🛠 Vorbereitung** im [Begleitkurs](https://bycs.link/reichl).

```bash
cd mcp-lehrgang-2026/code/python
uv sync                       # Python-Bibliotheken installieren
cp .env.example .env          # Konfiguration anlegen
uv run lab00/check.py         # Arbeitsumgebung prüfen
```

Unter Windows (PowerShell) statt `cp`:

```powershell
Copy-Item .env.example .env
```

In der Datei `.env` lassen Sie genau einen Block aktiv: lokal mit Ollama (Standard) oder OpenRouter mit Ihrem
Kursschlüssel.

> **Wichtig:** Die Datei `.env` enthält Ihren API-Schlüssel. Geben Sie sie nicht weiter und laden Sie sie nirgends hoch.

## Inhalt

| Ordner / Datei | Inhalt |
|---|---|
| `code/python/` | uv-Projekt mit allen Python-Programmen des Lehrgangs, je Lab ein Ordner (`lab00/`, `lab01/`, …) |
| `code/python/daten/` | frei erfundene Daten der „Staatlichen Musterschule“ (Vertretungsplan, Räume, Termine, Stundenplan, Hausordnung) |
| `code/python/.env.example` | Vorlage für die Konfiguration (Ollama oder OpenRouter) |
| `code/python/guthaben.py` | zeigt Restguthaben und Limits Ihres OpenRouter-Schlüssels |
| `code/andere_sprachen/` | dieselben Ideen in anderen Programmiersprachen (z. B. Java, JavaScript, TypeScript, Rust) |

Jedes Programm ist für sich allein lauffähig – Sie können einzelne Dateien in Ihren Unterricht übernehmen. Gestartet
wird immer aus `code/python/`, z. B. `uv run lab01/hallo_llm.py`.

Musterlösungen stehen nach dem jeweiligen Abschnitt zuerst im Begleitkurs und kommen danach auch hierher.

## Lizenz

- **Programmcode** (z. B. `*.py`, `*.ts`, `*.java`, `*.rs`, Konfigurationsdateien): MIT-Lizenz, siehe [LICENSE](LICENSE)
- **Texte und Daten** (z. B. diese README, `code/python/daten/`): CC BY 4.0, siehe [LICENSE-TEXTE.md](LICENSE-TEXTE.md)

Erstellt von Florian Reichl, Akademie für Lehrerfortbildung und Personalführung (ALP) Dillingen, 11/2026.
