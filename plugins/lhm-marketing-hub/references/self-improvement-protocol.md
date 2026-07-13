---
title: Self-Improvement Protocol
description: End-of-session learning capture. Run after every skill execution and agent session.
---

# Self-Improvement Protocol

Run this at the end of every agent session and after every skill execution. The goal is to make the plugin smarter with every use.

## Trigger 1 — During the session: push back on skipped tasks

When the user wants to skip a checklist task without explanation:
- Do not silently comply
- Say: "Before we skip this — can you tell me why? I want to make sure we're not missing something important."
- If the justification reveals something genuinely new about the client, their market, or how the skill should work: trigger all four checks below immediately, not just at the end of the session.

## Trigger 2 — End of session: four checks

Run all four in order. Each is a separate prompt to the user — do not batch them.

### Check 1 — Client-level learning

"Did we learn anything in this session that would save time or prevent mistakes next time we work on [client name]'s [discipline] account?"

If yes: read `${CLAUDE_PLUGIN_ROOT}/skills/[skill-name]/LEARNED.md`, add a dated entry in the format:
```
- (YYYY-MM-DD) Specific observation. Not vague advice.
```
Cap at 50 entries. If at 50, consolidate before adding.

### Check 2 — Skill improvement

"Did anything in this session suggest the skill itself should work differently — not just for this client, but for all clients?"

If yes: "Want me to update [skill-name]/SKILL.md with this improvement?"
Wait for confirmation, then make the edit.

### Check 3 — New skill

"Did this session surface a repeatable task that has no existing skill?"

If yes: "Want me to create a new skill for this?"
If yes: follow the plugin's skill creation process (frontmatter, SKILL.md, LEARNED.md).

### Check 4 — Agency learning

"Was there a meaningful win or loss in this session worth sharing across all clients?"

If yes: "Want me to add this to agency learnings for [discipline]?"
If yes: append to `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/[discipline].md` in this format:
```
- (YYYY-MM-DD) [Niche tag if applicable] Specific, dated, actionable observation.
```

## What NOT to record

- Session-specific context (client name, task details, file paths for this run)
- Information already in SKILL.md, client_profile.md, or reference files
- Speculation from a single observation (wait for a pattern)
- Anything the user explicitly asked not to remember
