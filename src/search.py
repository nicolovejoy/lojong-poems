"""Article input — manual paste now, Brave Search API later."""

from dataclasses import dataclass

from rich.console import Console
from rich.prompt import Prompt


@dataclass
class Article:
    headline: str
    source: str
    date: str
    url: str
    text: str


def input_manual(console: Console) -> Article:
    """Interactively collect article details. Body text terminated by a line containing only '---'."""
    console.print("\n[bold]Enter article details[/bold]\n")

    headline = Prompt.ask("Headline")
    source = Prompt.ask("Source (publication)")
    date = Prompt.ask("Date")
    url = Prompt.ask("URL")

    console.print("\nPaste article text below. Enter [bold]END[/bold] on its own line when done.\n")

    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)

    text = "\n".join(lines).strip()
    if not text:
        console.print("[red]No article text entered.[/red]")
        raise SystemExit(1)

    return Article(
        headline=headline,
        source=source,
        date=date,
        url=url,
        text=text,
    )


def search_brave(query: str, config: dict) -> None:
    """Stub — Brave Search API integration for later."""
    key = config.get("news", {}).get("api_key", "")
    if not key:
        raise NotImplementedError(
            "Brave Search API key not configured in config.toml [news] api_key"
        )
