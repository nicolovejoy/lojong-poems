# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lojong Found Poetry — a found-poetry generator that pairs Buddhist Lojong slogans with news stories to create poems composed primarily from journalistic prose, with minimal editorial intervention. Inspired by Victoria Adukwei Bulley's "The Ultra-Black Fish."

## Pipeline

1. **Resonance scoring** — LLM evaluates structural fit between a news story and a slogan's core tension
2. **Extraction** — Pull resonant passages from the story
3. **Composition** — Arrange found language into a poem

## Structure

- `data/SLOGANS.md` — 59 annotated Lojong slogans (7 Points). Each has: gloss, core tension, themes, search seeds, notes.
- `data/poems/` — Generated poems
- `src/` — Pipeline modules
- `prompts/` — Prompt templates for LLM calls
- `config.toml` — API keys and settings (not committed; see .gitignore)

## Key Concepts

- **Structural resonance**: Matching the _shape_ of a news story to the _shape_ of a teaching — not surface-level topic overlap.
- **Core tension**: The paradox or reversal at a slogan's heart. This drives poem generation.
- **Search seeds**: Keywords for finding structurally fitting stories.

## Reference: Bulley Methodology

"The Ultra-Black Fish" by Victoria Adukwei Bulley (from _Quiet_, 2022) is the formal model:

- Composed almost entirely from journalistic prose (multiple news sources, not the academic paper)
- Two deliberate interventions: strikethroughs replacing official language with truer language ("discovered" → "captured", "made the discovery" → "came across them by accident")
- One original closing sentence that surfaces latent subtext without stating it
- Operates on two registers simultaneously (scientific discovery + racial perception)

## Target Poem Structure

1. **Scene-setting** — concrete, imagistic journalistic language establishing the situation
2. **Discovery/event** — the thing that happened, in the story's own words
3. **Dual explanation** — what the story says it means vs. what it might actually mean
4. **What was not said** — the gap, the absence, the thing the journalist didn't name
5. **Original closing gesture** — 1-2 sentences, not found language, surfacing the slogan's teaching without stating it

## Intervention Types

- **Strikethrough + substitution**: `~~discovered~~ came across by accident` — replaces official/sanitized language with more honest language
- **Silence**: what the poem chooses not to include is as important as what it includes
- **The closing line**: always original, always earned, never explanatory
