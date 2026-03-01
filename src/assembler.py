"""Poem assembly — arrange found language via Claude, format output files."""

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .llm import call_claude, load_prompt
from .resonance import ResonanceResult
from .search import Article
from .slogans import Slogan


@dataclass
class GestureEval:
    gesture: str
    rating: str  # earned / close / not yet
    reason: str = ""


@dataclass
class AssemblyResult:
    poem_body: str = ""
    interventions: list[str] = field(default_factory=list)
    gesture_evaluations: list[GestureEval] = field(default_factory=list)
    alternative_gestures: list[str] = field(default_factory=list)
    raw: str = ""


def assemble_poem(
    slogan: Slogan,
    resonance: ResonanceResult,
    closing_gestures: list[str],
    banned_words: list[str],
    config: dict,
) -> AssemblyResult:
    """Format input per prompt spec, call Claude, parse the response."""
    system = load_prompt("prompts/assembly.md")
    user_msg = _format_input(slogan, resonance, closing_gestures, banned_words)
    raw = call_claude(system, user_msg, config)
    return _parse_response(raw)


def format_poem_file(
    slogan: Slogan,
    article: Article,
    poem_body: str,
    closing_gesture: str,
    interventions: list[str],
) -> str:
    """Render the final .md file matching the existing poem format."""
    # Title = slogan text
    title = slogan.text.capitalize() if slogan.text[0].islower() else slogan.text

    # Subtitle
    subtitle = f"Slogan {slogan.number} — after {article.source}"

    # Combine poem body and closing gesture
    full_poem = poem_body.rstrip()
    if closing_gesture:
        full_poem += "\n\n" + closing_gesture

    # Build intervention line for metadata
    intervention_meta = "; ".join(interventions) if interventions else "none"

    # Source line: headline, publication, date
    source_line = f'"{article.headline}," {article.source}, {article.date}'

    lines = [
        f"# {title}",
        "",
        f"*{subtitle}*",
        "",
        full_poem,
        "",
        "---",
        "",
        f"**Source:** {source_line}",
        f"**Slogan:** {slogan.number} — {slogan.text}",
        f"**Intervention:** {intervention_meta}",
        "",
    ]
    return "\n".join(lines)


def output_filename(slogan: Slogan, article: Article) -> str:
    """Generate filename like 007-ventilator-care.md."""
    # Slug from headline: lowercase, alphanumeric + hyphens, max 40 chars
    slug = re.sub(r"[^a-z0-9]+", "-", article.headline.lower()).strip("-")
    if len(slug) > 40:
        slug = slug[:40].rsplit("-", 1)[0]
    return f"{slogan.number:03d}-{slug}.md"


def save_poem(content: str, filename: str, poems_dir: str | Path | None = None) -> Path:
    """Write poem file to disk."""
    if poems_dir is None:
        from .config import REPO_ROOT
        poems_dir = REPO_ROOT / "data" / "poems"
    path = Path(poems_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


# --- Input formatting ---

def _format_input(
    slogan: Slogan,
    resonance: ResonanceResult,
    closing_gestures: list[str],
    banned_words: list[str],
) -> str:
    passages = "\n".join(resonance.candidate_passages)
    banned = ", ".join(banned_words) if banned_words else "(none specified)"

    gestures_text = ""
    for i, g in enumerate(closing_gestures, 1):
        gestures_text += f"{i}. {g}\n"

    return f"""### Slogan

**Text:** {slogan.text}
**Gloss:** {slogan.gloss}
**Core tension:** {slogan.core_tension}

### Resonance Scoring

**Structural fit:** {resonance.structural_fit}
**Latent register:** {resonance.latent_register}
**Candidate passages:**
{passages}

### Banned words

{banned}

### Human closing gesture(s)

{gestures_text}"""


# --- Output parsing ---

def _parse_response(raw: str) -> AssemblyResult:
    """Parse the assembly prompt output. Falls back to raw on failure."""
    result = AssemblyResult(raw=raw)

    # Split on ### headings
    sections = re.split(r"^### ", raw, flags=re.MULTILINE)

    for section in sections:
        lower = section.lower()

        if lower.startswith("arranged poem") or lower.startswith("poem"):
            # Strip the heading line and any --- separator
            body = re.sub(r"^.+?\n", "", section).strip()
            body = re.sub(r"\n---\s*$", "", body).strip()
            result.poem_body = body
            # Extract interventions (~~original~~ replacement)
            result.interventions = re.findall(
                r"~~(.+?)~~\s+(.+?)(?:\n|$)", body
            )
            result.interventions = [
                f'"{orig}" → "{repl}"'
                for orig, repl in result.interventions
            ]

        elif lower.startswith("evaluation"):
            _parse_evaluations(section, result)

        elif lower.startswith("alternative"):
            _parse_alternatives(section, result)

    return result


def _parse_evaluations(section: str, result: AssemblyResult) -> None:
    """Parse gesture evaluations from the section text."""
    # Look for patterns like: **Gesture N:** "..." \n Rating: earned/close/not yet
    gesture_blocks = re.split(r"\*\*Gesture \d+:\*\*", section)
    for block in gesture_blocks[1:]:  # skip text before first gesture
        quote_match = re.search(r'"([^"]+)"', block)
        rating_match = re.search(r"Rating:\s*\*?\*?(\w[\w\s]*\w)\*?\*?", block, re.IGNORECASE)
        # Reason is the line after rating
        reason = ""
        if rating_match:
            after_rating = block[rating_match.end():].strip()
            reason = after_rating.split("\n")[0].strip()

        result.gesture_evaluations.append(GestureEval(
            gesture=quote_match.group(1) if quote_match else "(unparsed)",
            rating=rating_match.group(1).strip().lower() if rating_match else "unknown",
            reason=reason,
        ))


def _parse_alternatives(section: str, result: AssemblyResult) -> None:
    """Parse numbered alternative closing gestures."""
    # Match numbered items: 1. ... 2. ... 3. ...
    items = re.findall(r"\d+\.\s+(.+?)(?=\n\d+\.|\Z)", section, re.DOTALL)
    result.alternative_gestures = [item.strip() for item in items]
