---
name: sync-observations
description: "Sync this machine's Task Observer observation logs into the shared lhm-skills repo so the weekly team review can see them. Use when the user says 'sync observations', 'push my observations', 'sync my skill logs', invokes /sync-observations, or when a scheduled routine runs this skill. Collects skill-observations/log.md files from local workspaces, commits them under observations/<person>/ in the lhm-skills repo, and pushes."
---

# Sync Observations

Collect every Task Observer observation log on this machine and push them to the shared `lhm-skills` repo, namespaced per person and per workspace. This is the feeder for the weekly team skill review — logs that aren't synced are invisible to it.

Designed to run unattended as a weekly local routine, or on demand via `/sync-observations`.

## Configuration

Resolve these once per run:

- **Repo:** `git@github.com:michaellhm/lhm-skills.git`. Preferred local clone: `~/Documents/lhm-skills-v3` if it exists and its `origin` matches; otherwise clone fresh to `~/.claude/lhm-skill-ops/repo/`.
- **Person slug:** the local part of `git config user.email` (e.g. `michael@…` → `michael`), lowercased, non-alphanumerics replaced with `-`. If git email is unset, use the macOS username.
- **Search roots** for observation logs (glob each for `**/skill-observations/log.md`, max depth 4):
  - `~/Documents`
  - `~/Library/CloudStorage/GoogleDrive-*/Shared drives/Claude Workspace`
  - `~/.claude`

## Workflow

### Step 1 — Find logs

Glob the search roots for `skill-observations/log.md`. Also pick up a sibling `cross-cutting-principles.md` where present. Skip any path containing `/.claude/worktrees/` or `node_modules`. If nothing is found, report "no observation logs on this machine yet" and stop — do not commit an empty sync.

### Step 2 — Prepare the repo

In the local clone: `git fetch origin && git checkout main && git pull --ff-only`. If the preferred clone has uncommitted changes unrelated to `observations/`, leave them alone — only ever stage paths under `observations/`.

### Step 3 — Copy logs in

For each found log, derive a **workspace slug** from its parent workspace folder name (e.g. `Alpha Sports Med` → `alpha-sports-med`) and copy:

```
observations/<person>/<workspace-slug>/log.md
observations/<person>/<workspace-slug>/cross-cutting-principles.md   (if present)
```

Copy the file contents verbatim — never rewrite, dedupe, or summarise during sync. The weekly review owns interpretation; sync owns fidelity.

### Step 4 — Commit and push

Stage only `observations/<person>/`. If `git diff --cached` is empty, report "already up to date" and stop. Otherwise commit:

```
chore(observations): sync <person> logs — <N> workspace(s)
```

and `git push origin main`. If push is rejected (non-fast-forward), pull --rebase and retry once; if it still fails, report the error rather than forcing.

### Step 5 — Report

One line: how many logs synced, from which workspaces, and whether anything was new. In unattended runs this becomes the routine's log output.

## Rules

- **Never touch files outside `observations/<person>/`.** Sync must not be able to change a skill, another person's logs, or the marketplace.
- **Never mutate the source logs** on the local machine — Task Observer owns those, including their ACTIONED/OPEN statuses.
- Logs may contain client names — the repo is private and the team already has access, so this is acceptable; but never copy logs into any other repo.
