---
name: lhm-knowledge-system-review
description: Audit the previous month of Local Health Marketing's Obsidian knowledge system, including AI conversation captures, lesson dispositions, recurring lessons, contradictions, Attention Queue outcomes, Ideas, Knowledge and SOP promotions, stale notes and capture quality. Use for the monthly knowledge-system review, after four weeks of conversation captures, or when Michael asks whether the LHM vault and AI memory workflow are producing useful, trustworthy context.
---

# LHM Knowledge System Review

Assess whether the knowledge workflow is improving decisions and continuity rather than merely creating notes.

## Load the review period

1. Locate the LHM vault and read `_System/Vault Conventions.md` and `_System/Multi-Agent Memory Contract.md` completely.
2. Use the previous calendar month unless Michael specifies another period. Use Australia/Melbourne dates.
3. Read every AI conversation-capture and weekly-review note in the period, including legacy Claude-named captures, plus `_System/AI Conversation Capture State.md`.
4. Read the Attention Queue, Ideas index, Knowledge index, SOP index and every canonical note changed by the captures.
5. Search for dispositions, contradictions, recurrences, unresolved checkboxes, stale statuses and duplicate topics. Do not infer performance from filenames alone.

## Measure the system

Report supported counts with links:

- Expected and completed weekly capture runs
- Sessions reviewed by source platform
- Material lessons by disposition
- Knowledge and SOP promotions
- `Needs Michael` items opened, resolved, waiting and still open
- `Observe again` lessons that recurred
- Contradictions found, resolved and unresolved
- Ideas created, advanced, parked or untouched
- Notes created but never linked or referenced
- Duplicate, stale or unsupported canonical claims discovered

Use `not tracked` when the vault lacks evidence. Never invent a zero.

## Judge quality

Assess:

- **Signal:** Did capture surface decisions, blockers or ideas that would otherwise have been lost?
- **Precision:** Were irrelevant chats and low-value implementation details excluded?
- **Promotion quality:** Did durable knowledge reach the correct canonical note without overpromotion?
- **Closure:** Were Michael-level blockers resolved or deliberately deferred?
- **Trust:** Are claims sourced, dated, attributable and free of unresolved contradictions?
- **Use:** Were captured notes referenced by Weekly Flow, projects or later decisions?

Label interpretation as `Agent analysis` and cite the underlying notes.

## Create the monthly review

Create or update `05 Weekly/YYYY-MM — Knowledge System Review.md` from `80 Templates/Knowledge System Review Template.md`. Keep one note per month and make reruns idempotent.

End with no more than three system improvements for the next month. Prefer small tests over new infrastructure. Add an Attention Queue item only when Michael must decide or intervene. Do not edit skills, install tools, delete notes or restructure the vault during an automated review.

## Verify

Validate YAML and links, confirm each metric has evidence, and report what worked, what degraded, the three improvements and anything requiring Michael.
