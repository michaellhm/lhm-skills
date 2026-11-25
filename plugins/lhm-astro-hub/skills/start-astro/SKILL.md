---
name: start-astro
description: "Canonical entry for Astro website delivery: detects which stage a client's site is at and routes to the right skill. Use this when the user says 'start astro', 'continue the build', 'where are we at with the site', 'what stage is the site at', 'what's next for the website', or begins any Astro website work for a client."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Knowledge records live in the shared LHM Knowledge vault; deliverables go under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples.

# Start Astro

Detect the stage, report it, then hand to the right skill. The orchestration lives in `${CLAUDE_PLUGIN_ROOT}/agents/astro-lead.md`; this skill is the entry and the stage detector.

## Steps

1. **Resolve the client and the repo.** Confirm the client name and the client repo path. Read the internal project file (`20 Clients/<client>/project-management/` and `Current Projects.md` in LHM Knowledge) and `brain/Project.md`.
2. **Detect the stage.** Run:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/start-astro/scripts/detect_stage.py <repo>
   ```
   It prints the repo facts and `next_stage` as JSON. No repo yet means `repo-setup`.
3. **Check the sitemap first.** The sitemap is a work-folder artefact tracked by the internal project file, not the repo. Before `repo-setup`, confirm the file records an approved sitemap; if not, the stage is `sitemap`.
4. **Report** the stage, what is done and what is next. If the internal file and the repo disagree, flag both and ask. Do not pick one.
5. **Route** to the stage's skill, after the user confirms.

| Stage | Skill |
|---|---|
| sitemap | `astro-sitemap` |
| repo-setup | `client-repo-setup` |
| prototype | `astro-prototype` |
| astro-build | `astro-build` |
| build-brain | `build-brain` |
| content-round | `content-rollout` |
| client-review | wait for the client; remind via `client-update-email` |
| update-content-brain | `update-content-brain` |

6. **Update the internal project file** after each stage: what was done, what is next, blockers.

## Stage rules

`next_stage` returns the first true condition in this order: no `brain/Overview.md` gives `repo-setup`; `Brand.md` with `> gap:` lines gives `prototype`; no `site/package.json` gives `astro-build`; a brain that fails `check_brain` or has gaps in `Profile.md` gives `build-brain`; unprocessed commits from the client's recorded identity give `update-content-brain`; pages awaiting review give `client-review`; otherwise `content-round`. With no client identity recorded, the brain-update check is skipped.

## Approval stops

Stop for an explicit yes at the sitemap, prototype, production deploy, brain draft, each round's page list and template (plus the mock-up or batch choice), each client email before sending, and each brain update proposal. All writing goes to `${CLAUDE_PLUGIN_ROOT}/agents/content.md`.
