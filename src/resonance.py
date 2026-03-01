"""Resonance scoring — evaluate story/slogan structural fit via Claude."""

import re
from dataclasses import dataclass, field

from .llm import call_claude, load_prompt
from .search import Article
from .slogans import Slogan


@dataclass
class ResonanceResult:
    score: str  # none | weak | strong | extraordinary
    structural_fit: str = ""
    surface_fit: str = ""
    latent_register: str = ""
    candidate_passages: list[str] = field(default_factory=list)
    risk: str = ""
    raw: str = ""


def score_story(slogan: Slogan, article: Article, config: dict) -> ResonanceResult:
    """Format inputs per prompt spec, call Claude, parse the response."""
    system = load_prompt("prompts/resonance_scoring.md")
    user_msg = _format_input(slogan, article)
    raw = call_claude(system, user_msg, config)
    return _parse_response(raw)


def routing_decision(result: ResonanceResult) -> str:
    """Suggest routing based on score + risk. Returns: proceed / flag / skip."""
    if result.score in ("none", "weak"):
        return "skip"
    if result.score == "extraordinary":
        return "flag"
    # strong
    risk_lower = result.risk.lower()
    if any(w in risk_lower for w in ("high", "significant", "serious", "forced")):
        return "flag"
    return "proceed"


def _format_input(slogan: Slogan, article: Article) -> str:
    """Build the user message matching the prompt's input format."""
    themes = ", ".join(slogan.themes)
    seeds = ", ".join(f'"{s}"' for s in slogan.search_seeds)

    return f"""### Slogan

**Text:** {slogan.text}
**Gloss:** {slogan.gloss}
**Core tension:** {slogan.core_tension}
**Themes:** {themes}
**Search seeds:** {seeds}

### Story

**Headline:** {article.headline}
**Source:** {article.source}
**Date:** {article.date}
**URL:** {article.url}
**Text:** {article.text}"""


def _parse_response(raw: str) -> ResonanceResult:
    """Parse the structured output. Falls back to raw on failure."""
    result = ResonanceResult(score="unknown", raw=raw)

    # Strip code fences if present
    text = raw.strip()
    text = re.sub(r"^```\w*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)

    # Parse field: value pairs (value may span multiple lines until next field)
    # Allow blank lines between fields in the lookahead
    fields = ("score", "structural_fit", "surface_fit", "latent_register",
              "candidate_passages", "risk")
    pattern = re.compile(
        r"^(" + "|".join(fields) + r"):\s*(.+?)(?=\n\s*(?:" + "|".join(fields) + r"):\s|$)",
        re.MULTILINE | re.DOTALL,
    )

    for match in pattern.finditer(text):
        name = match.group(1)
        value = match.group(2).strip()

        if name == "score":
            result.score = value.lower()
        elif name == "structural_fit":
            result.structural_fit = value
        elif name == "surface_fit":
            result.surface_fit = value
        elif name == "latent_register":
            result.latent_register = value
        elif name == "candidate_passages":
            result.candidate_passages = [
                line.strip() for line in value.splitlines()
                if line.strip() and not line.strip().startswith("[")
            ]
        elif name == "risk":
            result.risk = value

    return result
