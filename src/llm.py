"""Shared Claude client and prompt utilities."""

from pathlib import Path

import anthropic

from .config import REPO_ROOT


def load_prompt(name: str) -> str:
    """Read a prompt template file, resolved relative to repo root."""
    return (REPO_ROOT / name).read_text()


def call_claude(system: str, user_msg: str, config: dict) -> str:
    """Single Anthropic API call. Returns the text response."""
    api_key = config["anthropic"]["api_key"]
    model = config["anthropic"].get("model", "claude-sonnet-4-6")

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
    except anthropic.APIError as e:
        raise RuntimeError(f"Anthropic API error: {e}") from e
    return response.content[0].text
