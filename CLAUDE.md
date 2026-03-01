# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Vision

An experimental literary site (amianai.com) that tests whether AI can generate compelling poetry. Visitors read poems — some AI-generated, some human-authored — and vote on whether each was written by an AI. The name is the question.

The AI poems are found poems: assembled from journalistic prose, guided by Buddhist Lojong mind-training slogans, using the methodology of Victoria Adukwei Bulley's "The Ultra-Black Fish."

## Three Tracks

### Track 1: Content Pipeline

Automate the generation of new poems.

- News search (Brave Search API) using slogan search seeds from `SLOGANS.md`
- Resonance scoring (LLM) — filters stories by structural fit, not surface topic match
- Assembly (LLM) — arranges found language into poem structure, applies 1-2 interventions, proposes closing gestures
- Human review — editor selects/writes closing gesture, approves final poem
- Output — structured poem files with metadata (slogan, source, date, intervention notes)

Prompts: `prompts/resonance_scoring.md`, `prompts/assembly.md`
Slogan data: `data/SLOGANS.md` (all 59 annotated)
Target: one poem per slogan, mix of AI-assembled and human-authored

### Track 2: Site Features

**Phase 1 — live:**
- Poem display with intervention markup (strikethrough via remark-gfm + remark-breaks)
- Source attribution footer
- About page explaining the game
- Deployed to Vercel, amianai.com

**Phase 2 — core interaction:**
- "Was this written by an AI?" voting button on each poem (yes/no)
- Aggregate results displayed after voting ("73% thought this was human")
- No reveal until after vote

**Phase 3 — corpus and comparison:**
- Upload human-authored poems alongside AI poems (same format, no label)
- Reader cannot tell from presentation which is which
- Results dashboard: per-poem AI detection rates, trends across corpus

**Phase 4 — community:**
- User accounts (Auth.js v5 + Turso)
- Feedback throughout the experience (authenticated, eventually verified users)
- Submission form for human poets to contribute
- Optional: process notes (show the pipeline, interventions, slogan)

### Track 3: Pipeline Automation

- `src/search.py` — query Brave Search API using slogan search seeds
- `src/resonance.py` — score story/slogan pairs, route by score+risk
- `src/assembler.py` — run assembly prompt, return structured output for human review
- `src/cli.py` — end-to-end: pick slogan → find stories → score → assemble → review → publish
- Human stays in loop for: closing gesture, final approval, intervention review

## Structure

- `data/SLOGANS.md` — 59 annotated Lojong slogans (7 Points). Each has: gloss, core tension, themes, search seeds, notes.
- `data/poems/` — Generated poems (shared between pipeline and web app)
- `src/` — Python pipeline modules
- `prompts/` — Prompt templates for LLM calls
- `config.toml` — API keys and settings (not committed; see .gitignore)
- `web/` — Next.js app (App Router, Tailwind v4) for amianai.com

## Tech Stack

- **Frontend**: Next.js (App Router), Tailwind v4, Vercel
- **Pipeline**: Python, Anthropic API (claude-sonnet-4-6), Brave Search API
- **Poem rendering**: unified (remark-parse → remark-gfm → remark-breaks → remark-rehype → rehype-react)
- **Database** (future): Turso (libSQL/SQLite) via Drizzle ORM
- **Auth** (future): Auth.js v5 (Google OAuth + magic links)
- **Deploy**: Vercel (root dir = `web/`, deploys via git push only — no CLI deploys)

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

## Poem Format

- Metadata at the bottom of each `.md` file (bold markdown keys after `---`), not YAML frontmatter
- `~~word~~ replacement` for strikethrough interventions
- Single newlines within stanzas are line breaks (rendered via remark-breaks)
- Blank lines separate stanzas

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
