"""Load and validate config.toml."""

import tomllib
from pathlib import Path

# Repo root: parent of src/
REPO_ROOT = Path(__file__).resolve().parent.parent


def _find_config() -> Path:
    """Find config.toml at the repo root."""
    candidate = REPO_ROOT / "config.toml"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"config.toml not found at {REPO_ROOT}"
    )


def load_config(path: Path | None = None) -> dict:
    """Parse config.toml and return as dict."""
    path = path or _find_config()
    with open(path, "rb") as f:
        return tomllib.load(f)


def validate_config(config: dict) -> bool:
    """Check that required keys are present and non-placeholder."""
    key = config.get("anthropic", {}).get("api_key", "")
    if not key or key == "YOUR_API_KEY_HERE":
        raise ValueError(
            "Set your Anthropic API key in config.toml "
            "([anthropic] api_key = \"sk-ant-...\")"
        )
    return True
