"""Lab 03: Ein kleiner MCP-Server zum Untersuchen des Protokolls.

Er bietet von jeder Sorte ein Beispiel:
  Tool      addiere(a, b)               – das Modell entscheidet, ob es aufgerufen wird
  Tool      wuerfle(seiten)             – liefert eine Zufallszahl
  Resource  schule://hausordnung        – die Anwendung entscheidet, ob sie den Text einbindet
  Prompt    elternbrief(anlass)         – der Mensch wählt eine Vorlage aus

Start (spricht JSON-RPC über stdin/stdout):  uv run lab03/mini_server.py
"""

import random
from pathlib import Path

from mcp.server import MCPServer

DATEN = Path(__file__).resolve().parent.parent / "daten"

mcp = MCPServer("Musterschule-Mini", instructions="Kleiner Beispielserver der Staatlichen Musterschule.")


@mcp.tool()
def addiere(a: int, b: int) -> int:
    """Addiert zwei ganze Zahlen."""
    return a + b


@mcp.tool()
def wuerfle(seiten: int = 6) -> int:
    """Würfelt mit einem Würfel mit der angegebenen Seitenzahl (Standard: 6)."""
    return random.randint(1, seiten)


@mcp.resource("schule://hausordnung", mime_type="text/markdown")
def hausordnung() -> str:
    """Die Hausordnung der Staatlichen Musterschule."""
    return (DATEN / "hausordnung.md").read_text(encoding="utf-8")


@mcp.prompt()
def elternbrief(anlass: str) -> str:
    """Vorlage für einen kurzen, freundlichen Elternbrief."""
    return (
        f"Schreibe einen kurzen, freundlichen Elternbrief der Staatlichen Musterschule zum Anlass: {anlass}. "
        "Höchstens 120 Wörter, sachlich, ohne Namen von Schülerinnen und Schülern."
    )


if __name__ == "__main__":
    mcp.run()  # Standard: Transport stdio
