---
name: weekly-skill-review
description: "Run the weekly cross-team skill review over everyone's synced observations and open a pull request with proposed skill updates. Use when the user says 'weekly skill review', 'run the skill review', 'review the observations', invokes /weekly-skill-review, or when the weekly routine runs this skill. Reads observations/*/ in the lhm-skills repo, applies approved learnings to plugin skills on a branch, bumps versions, and opens a PR — it never merges."
---

# Weekly Skill Review

Aggregate every team member's synced Task Observer observations, decide which ones should change a skill, apply those changes on a branch, and open a pull request. The PR is the deliverable — **this skill never merges and never pushes to main.** Michael's review of the PR is the release gate.

Runs unattended as a weekly routine, or on demand via `/weekly-skill-review`.

## Setup

- **Repo:** `git@github.com:michaellhm/lhm-skills.git`, local clone as per sync-observations (prefer `~/Documents/lhm-skills-v3`, else `~/.claude/lhm-skill-ops/repo/`).
- Requires `gh` authenticated (`gh auth status`). If not, stop and tell the user — do not fall back to pushing main.
- Start from fresh `main`: fetch, checkout, `pull --ff-only`. Then create a branch `skill-review/<YYYY-MM-DD>`.

## Workflow

### Step 1 — Gather observations

Read every `observations/*/*/log.md` (and any `cross-cutting-principles.md`). Collect observations whose status is `OPEN`. If there are none, report "no open observations this week" and stop — no PR.

### Step 2 — Deduplicate and weigh

Group observations that describe the same underlying issue, even when worded differently or logged by different people. **An observation reported independently by 2+ people is a strong signal — prioritise it.** Keep the attribution list (who logged it, which workspace) for the PR body.

### Step 3 — Cross-check against skills

Inventory the skills in `plugins/*/skills/*/SKILL.md`. Evaluate every open observation against every skill — not just the skill named in its header; a WordPress lesson may also improve an Astro checklist. Classify each observation:

- **APPLY** — clear, generalisable, maps to a specific skill section.
- **SKIP (needs human)** — ambiguous, contradicts an existing rule, changes strategy or tone, or touches compliance (AHPRA etc.). List these in the PR body; never guess.
- **NOT ACTIONABLE** — one-off, client-specific (belongs in client_profile.md, note it), or already covered.

### Step 4 — Apply on the branch

For each APPLY item, edit the live skill file on the branch following the same editing discipline as Task Observer's `references/skill-authoring.md`:

- Integrate the insight into the section where it logically lives — never append an "observations" list at the bottom.
- Preserve the skill's structure, voice, and frontmatter description behaviour.
- Prefer the smallest edit that captures the rule; if a LEARNED.md exists in that skill, put raw gotchas there and reserve SKILL.md edits for workflow-level changes.

### Step 5 — Bump versions

For every plugin whose files changed: bump its patch version in **both** its `.claude-plugin/plugin.json` and its entry in `.claude-plugin/marketplace.json`. Bump the marketplace `metadata.version` patch once per review. This is what makes installs pick the update up.

### Step 6 — Mark observations actioned

In the synced logs on the branch (`observations/…/log.md`), update each applied observation's status to `ACTIONED (YYYY-MM-DD) — applied to <skill-name> (weekly review PR)`. Leave SKIP items `OPEN` with a one-line note. (Local machine logs are untouched; the next sync is fidelity-preserving in the other direction only — see rule below.)

### Step 7 — Open the PR

Commit per plugin (`fix(<plugin>): <summary> (weekly skill review)`), push the branch, and open a PR titled `Weekly skill review — <date>` with body:

```
## Applied (<N> observations)
- **<skill>** — <change summary> (logged by <person(s)>, obs #…)

## Skipped — needs your call
- <observation> — <why it needs a human>

## Not actionable
- <count and one-line reasons>
```

End the PR body with the standard Claude Code attribution line.

### Step 8 — Report

Summarise in chat / routine output: PR URL, counts applied/skipped, and any skills that changed. If the routine ran unattended, this summary is what Michael reads Monday morning.

## Rules

- **PR only. Never merge, never commit to main.** If branch push fails, report — never force.
- **Sync-vs-actioned conflict:** a later `sync-observations` run may overwrite an ACTIONED status with the local OPEN copy. That's acceptable — Step 2's dedup must therefore also check merged PR history (`git log --grep "weekly skill review"` on the skill) before re-applying something that looks new.
- Do not edit `observations/` content beyond status lines.
- One PR per run. If a review is already open and unmerged from a previous week, add to it rather than opening a second (checkout its branch, rebase on main).
