---
name: lhm-vault-thinking
description: Think across Local Health Marketing's Obsidian vault using evidence, note history and the link graph. Use when Michael asks for context, to trace how thinking evolved, connect two topics, challenge assumptions or contradictions, surface emerging ideas, generate vault-grounded ideas, or graduate a developed idea into a standalone note.
---

# LHM Vault Thinking

Use the LHM vault as a thinking partner. Distinguish evidence in the vault from inference, and preserve the boundary between Michael's reflections and agent-generated analysis.

## Load the vault safely

1. Locate the directory containing `.obsidian`; prefer `/Users/michaelcolman/Documents/Obsidian/Local Health Marketing/Local Health Marketing`.
2. Read `_System/Vault Conventions.md` and `_System/Multi-Agent Memory Contract.md` completely.
3. Detect the official Obsidian CLI with `command -v obsidian`. If unavailable, check `/Applications/Obsidian.app/Contents/MacOS/obsidian-cli` on macOS.
4. Prefer CLI reads when it responds. Target the vault explicitly as the first parameter: `obsidian vault="Local Health Marketing" <command>`.
5. If the CLI reports that Obsidian is not running or cannot be found, continue with `rg`, `rg --files` and direct Markdown reads. Do not launch a GUI or register the CLI without permission.

## Select one mode

Infer the mode from Michael's request. If two modes are requested, run both but keep their results distinct.

### Context

Summarise current goals, active projects, recent weekly context, open Attention Queue decisions and relevant recent notes. Do not load or reproduce the entire vault. Prioritise active and recently updated material.

### Trace

Track one topic through time:

1. Search exact terms, close variants and relevant links.
2. Read every materially relevant note, including dates and status.
3. Use `backlinks`, `links` and `search:context` when the CLI is available.
4. Produce a dated arc: first appearance, changes, current position and unresolved tensions.

### Connect

Find an evidence-backed relationship between two topics:

1. Search each topic independently.
2. Inspect shared backlinks, linked goals, projects, meetings and ideas.
3. Explain direct connections before inferred connections.
4. State when no meaningful connection is supported.

### Challenge

Pressure-test a position using the vault:

1. State the current position in Michael's own terms.
2. Identify contradictions, stale assumptions, missing evidence and execution risk.
3. Separate a genuine contradiction from a strategy that changed over time.
4. End with the smallest set of decisions or experiments needed.
5. Add an Attention Queue item only when Michael's decision or approval is genuinely required and the user asked to save the result.

### Ideas and emerge

Surface opportunities grounded in repeated themes, goals, constraints and active capabilities. Rank ideas by evidence, strategic fit, effort and next test. Do not create generic brainstorm filler or automatically convert an idea into a project.

### Graduate

Promote a sufficiently developed idea into `40 Ideas` only when the user asks to save or graduate it:

1. Search for an existing idea note first.
2. Use `80 Templates/Idea Template.md`.
3. Preserve the original wording and link its source notes.
4. Label agent synthesis as analysis; do not present it as Michael-written reflection.
5. Leave uncertain or undeveloped captures in `01 Inbox`.

## Authorship boundary

- Treat first-person reflections, beliefs and journal-like material as Michael-authored only when Michael supplied or approved the wording.
- Label agent-created interpretations as `Agent analysis` or place them in an explicitly analytical section.
- Never silently rewrite Michael's reflections to fit a cleaner narrative.
- Operational notes, indexes, project summaries and extracted decisions may be agent-maintained when grounded in sources.

## Output and writes

- Answer with the useful conclusion first, followed by supporting note links.
- Cite internal evidence with Obsidian links or clickable absolute file links.
- Make no vault changes for a request that only asks to answer, analyse or review.
- When asked to save, update the canonical note instead of duplicating facts.
- Verify YAML, internal links and new filenames after every write.
