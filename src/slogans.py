"""Parse data/SLOGANS.md into structured Slogan objects."""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Slogan:
    number: int
    text: str
    gloss: str = ""
    core_tension: str = ""
    themes: list[str] = field(default_factory=list)
    search_seeds: list[str] = field(default_factory=list)
    notes: str = ""
    tier: int | None = None


def load_slogans(path: str | Path | None = None) -> dict[int, Slogan]:
    """Parse SLOGANS.md and return dict keyed by slogan number."""
    if path is None:
        from .config import REPO_ROOT
        path = REPO_ROOT / "data" / "SLOGANS.md"
    text = Path(path).read_text()

    slogans: dict[int, Slogan] = {}

    # Split into slogan blocks on ### headings
    heading_pattern = re.compile(r"^### (\d+)\.\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(text))

    for i, match in enumerate(matches):
        number = int(match.group(1))
        slogan_text = match.group(2).strip()

        # Extract the block between this heading and the next (or end)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]

        slogan = Slogan(number=number, text=slogan_text)
        slogan.gloss = _extract_field(block, "Gloss")
        slogan.core_tension = _extract_field(block, "Core tension")
        slogan.themes = _extract_list(block, "Themes")
        slogan.search_seeds = _extract_seeds(block, "Search seeds")
        slogan.notes = _extract_field(block, "Notes")

        slogans[number] = slogan

    # Parse appendix for tier assignments
    _parse_tiers(text, slogans)

    return slogans


def _extract_field(block: str, name: str) -> str:
    """Extract a **Name:** value field from a block of text."""
    pattern = re.compile(
        rf"\*\*{re.escape(name)}:\*\*\s*(.+?)(?=\n\n|\n\*\*|\Z)",
        re.DOTALL,
    )
    match = pattern.search(block)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_list(block: str, name: str) -> list[str]:
    """Extract a comma-separated field into a list."""
    raw = _extract_field(block, name)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _extract_seeds(block: str, name: str) -> list[str]:
    """Extract quoted search seeds."""
    raw = _extract_field(block, name)
    if not raw:
        return []
    # Seeds are quoted: "word" "phrase" ...
    return re.findall(r'"([^"]+)"', raw)


def _parse_tiers(text: str, slogans: dict[int, Slogan]) -> None:
    """Parse the appendix section for tier assignments."""
    appendix = text.split("## Appendix")[1] if "## Appendix" in text else ""
    if not appendix:
        return

    current_tier = None
    for line in appendix.splitlines():
        tier_match = re.match(r"\*\*Tier (\d+)", line)
        if tier_match:
            current_tier = int(tier_match.group(1))
            continue
        if current_tier is not None:
            # Lines like: - **7** (Sending and taking / breath) — ...
            num_match = re.match(r"- \*\*(\d+)\*\*", line)
            if num_match:
                num = int(num_match.group(1))
                if num in slogans:
                    slogans[num].tier = current_tier
