"""Interactive pipeline: slogan → article → resonance → assembly → poem."""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from .assembler import (
    AssemblyResult,
    assemble_poem,
    format_poem_file,
    output_filename,
    save_poem,
)
from .config import REPO_ROOT, load_config, validate_config
from .resonance import ResonanceResult, routing_decision, score_story
from .search import Article, input_manual
from .slogans import Slogan, load_slogans

console = Console()


def main():
    console.print(Panel("Lojong Found Poetry Pipeline", style="bold cyan"))

    # --- Setup ---
    try:
        config = load_config()
        validate_config(config)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    slogans = load_slogans()
    existing = _existing_poems()

    # --- Step 1: Select slogan ---
    slogan = step_select_slogan(slogans, existing)

    # --- Step 2: Get article ---
    article = step_get_article()

    # --- Step 3: Score resonance ---
    resonance = step_score_resonance(slogan, article, config)
    if resonance is None:
        return

    # --- Step 4: Closing gestures + banned words ---
    gestures, banned = step_closing_input(slogan)

    # --- Step 5: Assemble ---
    assembly = step_assemble(slogan, resonance, gestures, banned, config)

    # --- Step 6: Select closing gesture ---
    closing = step_select_gesture(assembly, gestures)

    # --- Step 7: Review interventions ---
    poem_body, interventions = step_review_interventions(assembly)

    # --- Step 8: Preview & save ---
    step_preview_and_save(slogan, article, poem_body, closing, interventions, config)


# ---- Step implementations ----


def step_select_slogan(
    slogans: dict[int, Slogan], existing: set[int]
) -> Slogan:
    """Display slogans by tier, let user pick one."""
    console.print("\n[bold]Step 1: Select a slogan[/bold]\n")

    # Show tier 1 first
    tier1 = [s for s in slogans.values() if s.tier == 1]
    tier2 = [s for s in slogans.values() if s.tier == 2]
    tier3 = [s for s in slogans.values() if s.tier == 3]

    if tier1:
        console.print("[cyan]Tier 1 — Strong structural resonance potential:[/cyan]")
        for s in sorted(tier1, key=lambda x: x.number):
            done = " [green](done)[/green]" if s.number in existing else ""
            console.print(f"  {s.number:2d}. {s.text}{done}")

    if tier2:
        console.print("\n[dim]Tier 2 — Good potential, needs right story:[/dim]")
        for s in sorted(tier2, key=lambda x: x.number):
            done = " [green](done)[/green]" if s.number in existing else ""
            console.print(f"  {s.number:2d}. {s.text}{done}")

    if tier3:
        console.print("\n[dim]Tier 3 — Harder to operationalize:[/dim]")
        for s in sorted(tier3, key=lambda x: x.number):
            done = " [green](done)[/green]" if s.number in existing else ""
            console.print(f"  {s.number:2d}. {s.text}{done}")

    untiered = [s for s in slogans.values() if s.tier is None]
    if untiered:
        console.print(f"\n[dim]{len(untiered)} other slogans available (enter any number 1-59)[/dim]")

    while True:
        choice = Prompt.ask("\nSlogan number")
        try:
            num = int(choice)
            if num in slogans:
                slogan = slogans[num]
                console.print(f"\n[bold]{slogan.number}. {slogan.text}[/bold]")
                console.print(f"[dim]{slogan.core_tension}[/dim]\n")
                return slogan
        except ValueError:
            pass
        console.print("[red]Enter a valid slogan number (1-59)[/red]")


def step_get_article() -> Article:
    """Collect article via manual input."""
    console.print("[bold]Step 2: Enter article[/bold]")
    return input_manual(console)


def step_score_resonance(
    slogan: Slogan, article: Article, config: dict
) -> ResonanceResult | None:
    """Score resonance and confirm routing."""
    console.print("\n[bold]Step 3: Scoring resonance...[/bold]\n")

    with console.status("Calling Claude for resonance scoring..."):
        result = score_story(slogan, article, config)

    # Display results
    score_color = {
        "extraordinary": "bold magenta",
        "strong": "bold green",
        "weak": "yellow",
        "none": "red",
    }.get(result.score, "white")

    console.print(f"Score: [{score_color}]{result.score}[/{score_color}]")
    console.print(f"\n[bold]Structural fit:[/bold] {result.structural_fit}")
    console.print(f"[bold]Surface fit:[/bold] {result.surface_fit}")
    console.print(f"[bold]Latent register:[/bold] {result.latent_register}")

    if result.candidate_passages:
        console.print(f"\n[bold]Candidate passages[/bold] ({len(result.candidate_passages)}):")
        for p in result.candidate_passages:
            console.print(f"  [dim]>[/dim] {p}")

    if result.risk:
        console.print(f"\n[bold]Risk:[/bold] {result.risk}")

    # Routing
    route = routing_decision(result)
    console.print(f"\nRouting suggestion: [bold]{route}[/bold]")

    if route == "skip":
        if not Confirm.ask("Score is low. Proceed anyway?", default=False):
            console.print("[dim]Skipping this pairing.[/dim]")
            return None
    elif route == "flag":
        console.print("[yellow]Flagged for review — check risk assessment above.[/yellow]")
        if not Confirm.ask("Proceed with assembly?", default=True):
            return None
    else:
        if not Confirm.ask("Proceed with assembly?", default=True):
            return None

    return result


def step_closing_input(slogan: Slogan) -> tuple[list[str], list[str]]:
    """Get closing gestures and banned words from the human editor."""
    console.print("\n[bold]Step 4: Closing gestures & banned words[/bold]\n")

    console.print(
        "Enter one or more closing gestures (the original line(s) that will end the poem).\n"
        "These should be original language, not found from the article.\n"
        "Enter each on its own line. Empty line when done.\n"
    )

    gestures: list[str] = []
    while True:
        line = Prompt.ask(f"Gesture {len(gestures) + 1} (or empty to finish)")
        if not line:
            break
        gestures.append(line)

    if not gestures:
        console.print("[yellow]No gestures entered — Claude will only propose alternatives.[/yellow]")
        gestures = ["(none provided — propose alternatives only)"]

    # Banned words
    default_banned = ", ".join(slogan.themes[:5]) if slogan.themes else ""
    banned_input = Prompt.ask(
        "Banned words for closing gesture",
        default=default_banned,
    )
    banned = [w.strip() for w in banned_input.split(",") if w.strip()]

    return gestures, banned


def step_assemble(
    slogan: Slogan,
    resonance: ResonanceResult,
    gestures: list[str],
    banned: list[str],
    config: dict,
) -> AssemblyResult:
    """Call Claude for poem assembly."""
    console.print("\n[bold]Step 5: Assembling poem...[/bold]\n")

    with console.status("Calling Claude for assembly..."):
        result = assemble_poem(slogan, resonance, gestures, banned, config)

    # Display poem
    console.print(Panel(result.poem_body or result.raw, title="Arranged Poem", border_style="green"))

    # Display evaluations
    if result.gesture_evaluations:
        console.print("\n[bold]Gesture evaluations:[/bold]")
        for ev in result.gesture_evaluations:
            rating_style = {
                "earned": "bold green",
                "close": "yellow",
                "not yet": "red",
            }.get(ev.rating, "white")
            console.print(f'  "{ev.gesture}" — [{rating_style}]{ev.rating}[/{rating_style}]')
            if ev.reason:
                console.print(f"    {ev.reason}")

    # Display alternatives
    if result.alternative_gestures:
        console.print("\n[bold]Alternative closing gestures:[/bold]")
        for i, alt in enumerate(result.alternative_gestures, 1):
            console.print(f"  {i}. {alt}")

    return result


def step_select_gesture(
    assembly: AssemblyResult, original_gestures: list[str]
) -> str:
    """Let the human pick a closing gesture."""
    console.print("\n[bold]Step 6: Select closing gesture[/bold]\n")

    options: list[str] = []

    # Original gestures
    for g in original_gestures:
        if g != "(none provided — propose alternatives only)":
            options.append(g)

    # Alternatives from Claude
    for alt in assembly.alternative_gestures:
        options.append(alt)

    if not options:
        console.print("[yellow]No gestures available.[/yellow]")
        return Prompt.ask("Write a closing gesture")

    for i, opt in enumerate(options, 1):
        console.print(f"  {i}. {opt}")
    console.print(f"  {len(options) + 1}. Write a new one")

    while True:
        choice = Prompt.ask("Choice")
        try:
            idx = int(choice)
            if 1 <= idx <= len(options):
                selected = options[idx - 1]
                console.print(f"\n[green]Selected:[/green] {selected}")
                return selected
            elif idx == len(options) + 1:
                return Prompt.ask("Write your closing gesture")
        except ValueError:
            pass
        console.print("[red]Enter a valid number[/red]")


def step_review_interventions(assembly: AssemblyResult) -> tuple[str, list[str]]:
    """Review and optionally modify interventions."""
    console.print("\n[bold]Step 7: Review interventions[/bold]\n")

    poem_body = assembly.poem_body

    if assembly.interventions:
        console.print("Interventions found in poem:")
        for i, interv in enumerate(assembly.interventions, 1):
            console.print(f"  {i}. {interv}")

        kept = []
        if not Confirm.ask("\nKeep all interventions?", default=True):
            for interv in assembly.interventions:
                if Confirm.ask(f"  Keep {interv}?", default=True):
                    kept.append(interv)
        else:
            kept = list(assembly.interventions)
        return poem_body, kept
    else:
        console.print("[dim]No interventions found in the assembled poem.[/dim]")
        return poem_body, []


def step_preview_and_save(
    slogan: Slogan,
    article: Article,
    poem_body: str,
    closing_gesture: str,
    interventions: list[str],
    config: dict,
) -> None:
    """Show final poem, get approval, save to disk."""
    console.print("\n[bold]Step 8: Preview & save[/bold]\n")

    poems_dir_rel = config.get("output", {}).get("poems_dir", "data/poems")
    poems_dir = REPO_ROOT / poems_dir_rel
    filename = output_filename(slogan, article)

    content = format_poem_file(slogan, article, poem_body, closing_gesture, interventions)

    console.print(Panel(content, title=filename, border_style="cyan"))

    if not Confirm.ask("Save this poem?", default=True):
        console.print("[dim]Poem not saved.[/dim]")
        return

    path = save_poem(content, filename, poems_dir)
    console.print(f"\n[bold green]Saved:[/bold green] {path}")


# ---- Helpers ----


def _existing_poems() -> set[int]:
    """Return slogan numbers that already have poems in data/poems/."""
    poems_dir = REPO_ROOT / "data" / "poems"
    if not poems_dir.exists():
        return set()
    numbers = set()
    for f in poems_dir.glob("*.md"):
        # Filenames like 034-berkeley-air-pollution.md
        parts = f.stem.split("-", 1)
        if parts[0].isdigit():
            numbers.add(int(parts[0]))
    return numbers


if __name__ == "__main__":
    main()
