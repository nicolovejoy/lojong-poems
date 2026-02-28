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

- **Structural resonance**: Matching the *shape* of a news story to the *shape* of a teaching — not surface-level topic overlap.
- **Core tension**: The paradox or reversal at a slogan's heart. This drives poem generation.
- **Search seeds**: Keywords for finding structurally fitting stories.
