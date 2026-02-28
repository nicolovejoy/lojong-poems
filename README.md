# Lojong Found Poetry

A found-poetry generator that pairs Buddhist Lojong slogans with news stories to create found-language poems.

Inspired by Victoria Adukwei Bulley's "The Ultra-Black Fish" — a poem composed almost entirely from journalistic prose about a scientific discovery, with deliberate editorial interventions (strikethroughs/substitutions) and a single original closing line.

## How It Works

1. **Resonance scoring** — An LLM evaluates whether a news story's *structure* mirrors a slogan's core tension (not surface-level topic matching)
2. **Extraction** — Resonant passages are pulled from the story
3. **Composition** — Found language is arranged into a poem with minimal editorial intervention

## Project Structure

- `data/SLOGANS.md` — 59 annotated Lojong slogans (7 Points of Chekawa Yeshe Dorje)
- `data/poems/` — Generated poems
- `src/` — Pipeline modules
- `prompts/` — Prompt templates for LLM calls
- `config.toml` — API keys and settings (not committed)
