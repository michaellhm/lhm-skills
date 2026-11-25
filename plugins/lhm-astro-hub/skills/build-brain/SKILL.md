---
name: build-brain
description: "Fill the client's brain notes from their Fathom calls, the approved prototype copy and the brand style guide, with every fact sourced and every unknown left as a gap. Use this when the user says 'build the brain', 'fill the brain', 'brain draft', 'populate brain notes', 'extract client info from calls', or when the prototype is approved and the client repo needs its knowledge notes written before page copy rounds begin."
---
# Build Brain

The brain is the client repo's `brain/` folder: ten markdown notes that hold what we know about the business, written once from real sources and then kept current by the content rounds. This skill writes the first version. Everything in it must come from a source; what is not known stays a gap.

## Before Starting

1. **Client context** - read and follow [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve the client's internal vault folder and the client repo.
2. **Client repo** - `brain/` must exist with all ten notes, made by `client-repo-setup`. If not, stop and run that skill first.
3. **Brand** - `brain/Brand.md` is written by `astro-prototype` before this skill runs. Read it. Do not overwrite it. The only change allowed is appending to its `sources`.
4. **Writing rules** - read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`. Australian English, no em or en dashes, no invented facts, prices, staff or results, AHPRA rules where they apply.
5. **Own learnings** - read `LEARNED.md` in this skill folder and apply any entries.

## Step 1: Gather sources

Read, in this order:

1. **The client's Fathom calls.** Use the Fathom connector, read-only: `search_meetings` or `list_meetings` to find the client's calls, `get_meeting_summary` to orient, then `get_meeting_transcript` for every fact you will write. Never state what was said on a call from memory or from a summary alone. Facts come from transcripts only. If the connector is unavailable, say so and stop; do not substitute recollection.
2. **The approved prototype copy**, from the client repo's prototype folder.
3. **`brain/Brand.md`.**
4. **The internal vault overview** for the client (from the routing contract), for context and links only. Do not copy private notes, pricing, credentials or staff-private material into the client repo.

Record each source as you go: call title and date, "prototype copy", "Brand.md".

## Step 2: Draft the notes

Fill the notes as mapped in [extraction categories](references/extraction-categories.md): Profile (mission, vision, values, founder story, positioning), Services, Staff, What We Do, Who We Serve and Content Rules (voice notes). Rules:

- Write only what a source states. Quote the client's own words where wording matters (voice, values).
- Each note lists its sources in `sources`, as an inline list (`sources: [a, b]`) or a block list. Update `updated` to today.
- Where nothing was said, keep the `> gap: not yet captured` line under that heading. Several gaps are expected and are better than a guess.
- A note that has facts must have at least one source. `check_brain` fails otherwise.
- Add a "brain created" entry to `Change Log.md` under Entries with today's date and the sources used. Leave the `<!-- last-processed: ... -->` marker as it is.
- Leave `Project.md` alone. `client-review-release` rewrites it.
- Leave `Overview.md` as it is unless a note name changed.

## Step 3: Approval stop

Show the draft to the operator: each note, its facts with sources, and every gap. Ask: "This is the brain draft. Approve it, or tell me what to change?" Do not run `check_brain`, commit or push before an explicit yes. Apply changes they ask for and show again.

## Step 4: Check, commit, push

After approval:

```sh
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-brain/scripts/check_brain.py CLIENT_REPO/brain
```

It exits 1 and names each problem as `Note.md: reason`. Fix them and rerun until it prints `brain ok`. Then commit the `brain/` changes and push to `main` (staging uses one branch; no review branches). Read the push result back and report the actual commit; if the push failed, say so.

## Step 5: Link from the internal vault

Add a link to the client's brain (the repo's `brain/Overview.md`) in the client overview in the internal vault. Link only. Do not copy brain facts into the vault, so there is one source of truth. Read the overview back to confirm the link is there.

## Self-review before finishing

- [ ] Every fact traces to a transcript, the prototype copy or Brand.md.
- [ ] No gap filled by assumption.
- [ ] Brand.md and Project.md untouched apart from `sources`.
- [ ] `check_brain` printed `brain ok` after approval.
