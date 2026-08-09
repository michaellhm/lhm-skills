---
name: lhm-conversation-capture
description: Review a date range of Michael's local Claude Code and Hermes conversations for Local Health Marketing ideas, decisions, external-resource reviews, unresolved questions, wins, lessons and strategic changes, then update the LHM Obsidian vault without dumping transcripts. Use for the Monday AI conversation review, weekly LHM knowledge capture, recurrence or contradiction detection, or when asked to mine recent AI chats into Ideas, the Attention Queue, Inbox, projects, marketing notes, SOPs or durable knowledge.
---

# LHM Conversation Capture

Turn useful thinking from recent Claude Code conversations into structured LHM business memory. Treat the conversations as source material; the Obsidian vault remains the curated knowledge base.

## Scope and limitations

- Read local Claude Code history from `~/.claude/projects/**/*.jsonl` and Hermes history from `~/.hermes/state.db`.
- Do not claim to cover Claude.ai web or mobile chats unless their contents have been exported or otherwise made locally accessible.
- Default to the previous Monday 00:00 through the current Monday 00:00 in `Australia/Melbourne` when run on Monday. On another day, use the last seven complete days unless the user specifies a range.
- Exclude subagent histories, tool traffic, command output, system reminders and implementation chatter unless they contain a durable business decision.
- Never copy credentials, tokens, private keys, authentication output or unnecessary client-sensitive material into the vault.

## Prepare

1. Locate the vault directory containing `.obsidian`; prefer `/Users/michaelcolman/Documents/Obsidian/Local Health Marketing/Local Health Marketing`.
2. Read `_System/Vault Conventions.md` and `_System/Multi-Agent Memory Contract.md` completely.
3. Read `_System/AI Conversation Capture State.md`. If only the legacy `_System/Claude Conversation Capture State.md` exists, migrate its coverage without losing processed session IDs.
4. Read the relevant indexes and canonical notes before writing: `05 Weekly`, `10 Goals`, `25 Marketing`, `30 Projects`, `40 Ideas`, `60 Knowledge`, and the Attention Queue.
5. Search for existing notes about each candidate topic so updates go to the canonical note rather than a duplicate.

## Extract conversations

Run both bundled extractors with the same explicit dates:

```bash
python3 scripts/extract_claude_conversations.py --start YYYY-MM-DD --end YYYY-MM-DD
python3 scripts/extract_hermes_conversations.py --start YYYY-MM-DD --end YYYY-MM-DD \
  --ssh-host root@178.104.126.159 \
  --remote-db /home/hermes/.hermes/state.db
```

The end date is exclusive. Resolve `scripts/` relative to this `SKILL.md`. The extractors return human-authored prompts plus text-only assistant replies grouped by session. The Hermes extractor runs a read-only query over SSH, redacts common credential patterns, and never mutates the remote database. It relies on the Mac's existing SSH key access; do not embed passwords or private keys. Use `--output <temporary-path>` when results are too large for direct inspection. Delete temporary extracts after the review.

If the script cannot access the history directory, report the limitation and do not fabricate a review. Do not alter source conversation files.

Merge the sources conceptually during analysis, not by concatenating transcripts into the vault. Deduplicate the same idea or decision when it appears in multiple assistants, while preserving every supporting source ID.

## Detect recurrence and contradiction

Before assigning a disposition:

1. Search prior conversation captures and canonical notes for the concept, close variants and linked topics.
2. Mark a **recurrence** when materially the same lesson appears in at least two independent sessions or weeks. Record the occurrence count and sources. Do not count repeated messages within one conversation as independent evidence.
3. Mark a **contradiction** when a new claim conflicts with a current canonical decision, metric, owner, status, scope or definition.
4. Distinguish a later explicit decision from an unresolved disagreement. Update the canonical note when Michael clearly superseded the old position; otherwise use `Needs Michael` and preserve both positions with dates.
5. Promote a recurring lesson only when it is durable and cross-project. Repetition alone does not prove correctness.

## Decide what is relevant

Keep material that affects Local Health Marketing's:

- positioning, offers, pricing, lead generation or sales;
- website, SEO, Google Ads, content or campaign strategy;
- delivery model, operating system, roles, capacity or client experience;
- active goals, projects, experiments or measurable outcomes;
- evaluation of an app, GitHub repository, YouTube video, framework or external idea;
- unresolved strategic question that genuinely requires Michael's judgment;
- reusable lesson, win, loss or changed assumption.

Ignore unrelated personal material, other businesses, routine coding detail and ideas with no plausible LHM relevance.

## Classify before writing

Use the smallest appropriate destination:

- **Canonical marketing, goal or project note:** a confirmed decision, changed strategy, result or milestone.
- **`40 Ideas`:** a genuine opportunity worth evaluating. Use the Idea template and state the smallest next test.
- **Attention Queue:** only a decision, approval or intervention that must come from Michael. Never add ordinary tasks.
- **`01 Inbox`:** unresolved information whose correct destination or meaning is still unclear.
- **`60 Knowledge`:** a durable external-resource review or reusable principle. Link the original URL and distinguish the source's claims from agent analysis.
- **Weekly capture note:** provenance, low-confidence observations, items not promoted elsewhere and a concise audit trail of the run.

Do not silently convert a question into a decision, an idea into a project, or an assistant suggestion into Michael's stated belief.

## Close the lesson loop

Give every material lesson exactly one disposition:

- **Applied:** update the relevant project, goal or marketing note because the lesson has already changed current work.
- **Promote to Knowledge:** create or update a note in `60 Knowledge` only when the lesson is durable, reusable across projects and supported by evidence or repeated experience.
- **Update SOP:** update the relevant procedure in `70 SOPs` when the lesson changes repeatable execution.
- **Needs Michael:** add an Attention Queue item only when Michael must decide, approve, reconnect, authorize or intervene.
- **Observe again:** retain the lesson in the weekly capture when it is plausible but unproven or requires another occurrence.

Do not create a standalone Knowledge note for a one-off project fact. Record the disposition and destination in the weekly capture. Mark unresolved knowledge candidates for Weekly Flow; do not promote them merely because an assistant proposed them.

## Write the weekly capture

Create or update `05 Weekly/YYYY-Www — AI Conversation Capture.md` with:

```markdown
---
type: weekly-capture
status: complete
week: YYYY-Www
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# AI Conversation Capture — YYYY-Www

## Summary
## Decisions and strategy changes
## Ideas surfaced
## External resources reviewed
## Questions needing attention
## Wins and lessons
## Knowledge and SOP candidates
## Recurrences and contradictions
## Updates made
## Not promoted
## Sources
```

Summarise; do not paste raw transcripts. For every material lesson, record its disposition and destination. Under `Knowledge and SOP candidates`, list candidates that Weekly Flow should confirm, including `Observe again` items. Under `Recurrences and contradictions`, record the evidence count, dated sources, canonical note affected and whether the conflict was resolved or needs Michael. In `Sources`, include the source platform, session ID, date and local source path, plus any original external URL. Label interpretations as `Agent analysis`.

## Maintain the checkpoint

After all vault edits verify successfully, create or update `_System/AI Conversation Capture State.md` with:

- `last_successful_run` timestamp;
- the covered start and exclusive end dates;
- the weekly capture note link;
- source platform and session IDs processed in that run.

Do not advance the checkpoint after a partial or failed run. A rerun of the same period should update the existing weekly capture and canonical notes idempotently, not create duplicates.

## Verify and report

1. Validate YAML and internal links in every changed note.
2. Confirm no raw transcript, credentials or duplicate notes were introduced.
3. Confirm every Attention Queue addition requires Michael specifically.
4. Report the date window, sessions reviewed, notes created or updated, items deliberately left unpromoted and the Claude.ai coverage limitation.
