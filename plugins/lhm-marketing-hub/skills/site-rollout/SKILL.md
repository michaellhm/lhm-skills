---
name: site-rollout
description: Run the phased page rollout for a client site from its sitemap plan. Two modes - build (write the next batch of pages on a branch and open a PR) and check (read Search Console, update the status table, email only on problems). Use for the LHM monthly/3-weekly page build and the weekly indexing check, or any client with a docs/rollout/config.md.
---

# Site rollout

Reusable for any client. Everything client-specific lives in `docs/rollout/config.md`; state lives in `docs/rollout/rollout-state.md`; the plan lives at the path named in the config (`sitemap.json`). Never hardcode client details in a routine prompt: the prompt only says "run site-rollout in <build|check> mode".

## 0. Preflight (both modes, always first)

Confirm all of these. If any fails, email the owner what is missing and STOP. Do not guess, do not fall back to a different copy of a file.
- Repo path from config exists and `git status` is readable.
- `docs/rollout/config.md`, `docs/rollout/rollout-state.md` and the plan file are readable.
- Check mode only: Search Console access works for the configured property.
- Build mode only: the pipeline skills listed in the config are available.

## 1. Read state

Read `rollout-state.md`. It is the only memory between runs. Compare `git log` on main since the tracker's last checkpoint; reconcile any pages that landed outside the routine (chat sessions, Hermes/Codex) before doing anything else.

## 2. Check mode (weekly)

1. Inspect index status in Search Console for every page with status `published`, `stalled` or `fixed`.
2. Update the status table: `indexed`, `stalled` (discovered or crawled, not indexed after 2 runs), `fixed`.
3. For a stalled page, diagnose against source (internal links, sitemap, canonical, content depth) before calling it a defect.
4. Indexing is a SIGNAL, never a gate. Report it; it only blocks the next batch when a defect is diagnosed (not on the label "stalled" alone). If a whole cluster stalls, flag a likely systemic cause.
5. Email the owner only if a page is stalled, a defect is found, or a decision is needed. Silence on a clean week.
6. No GSC writes (sitemap submit/delete, indexing requests) unless the config allows it.

## 3. Build mode (every 3 weeks)

1. Pick the next batch: the next unbuilt cluster in plan order. No page cap; size by cluster (e.g. all "who we work with" Google Ads pages). One cluster per batch. Clear any carried-over stalled pages from the previous batch as part of this batch.
2. Run the full pipeline per page, in order, using the skills named in the config: personas -> keyword research -> brief -> full copy -> client-review-release. No skipping stages.
3. Pages in a cluster must differ in substance, not just the profession/location name. Check for near-duplicate copy before committing.
4. Never invent: pricing, case studies, testimonials, results, credentials. Apply the config's defaults (e.g. pricing "on call"), write the page complete without the proof, and list the gap.
5. Create branch `rollout/<cluster>-<YYYY-MM-DD>`, commit, push, open a PR. NEVER push or merge to main. Merging the PR is what publishes.
6. PR description: pages, target keywords, internal links added/updated, a "Decisions made by default" list, and a "Gaps needing the owner" list.
7. Update `rollout-state.md` (page rows -> `in PR`, next step). Email the owner: batch, keywords, PR link, decisions/gaps.

## 4. Rules that apply every run

- Read the config's `compliance` section before writing or judging any page. Do not raise a compliance blocker the config says does not apply.
- Keep `rollout-state.md` short: current phase, status table, open decisions, last 3 run entries. Move older run history to `docs/rollout/archive/`.
- Report outcomes honestly: if something could not be checked, say so; do not mark it done.
