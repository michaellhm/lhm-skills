---
name: website-kickoff
description: "Kick off a new website build (WordPress or Astro) — intake, state file, BasicOps scaffold with backwards-scheduled milestones, client kickoff email, and handoff to the WordPress hub. Use this when the user says 'website kickoff', 'kick off the website', 'start the website project', 'new website for [client]', or 'begin the site build process'. Follows references/kickoff-pattern.md. Delivery work itself belongs to lhm-wordpress-hub:website-build-orchestrator, never this skill."
---

# Website Kickoff

Turn a newly-sold or newly-scoped website project into a running process: a state file the rest of the agency can read, a BasicOps scaffold with real dates, and a drafted client email. Follows `references/kickoff-pattern.md`'s 5-step shape exactly. This skill never touches sitemap, copy, design, or build work itself — that's `lhm-wordpress-hub`'s job, starting the moment Step 5 hands off.

## Step 1: Intake

Read `references/kickoff-pattern.md` first if you haven't already this session — its 5-step shape is what this skill implements. Ask these questions **one at a time, never batched**:

1. **Platform** — Astro or WordPress?
2. **New build or rebuild?** (rebuild of an existing live site vs. greenfield)
3. **What is the go-live / launch deadline?** (required by the pattern — this is what backwards scheduling in Step 3 works from)
4. **Who supplies content** — us (LHM writes copy) or the client (client supplies copy)?
5. **Domain/hosting access status** — do we already have DNS and hosting access, or is that still outstanding?

If this kickoff follows directly from `sales-handover` or `client-onboarding`, check the client folder first — platform may already be recorded in `client_profile.md`'s YAML frontmatter, and the deadline may already be in the handover doc. Confirm rather than re-asking anything already on file, but still ask anything genuinely missing.

## Step 2: State

Locate or create the client folder per `references/folder-convention.md`. **Do not write `project-management/website.md` directly** — create it by invoking `lhm-project-hub:wp-project-manager` in its Mode 1 (Create), passing along what Step 1 gathered (platform, deadline, content ownership). That skill owns the file's structure (Astro vs. legacy WordPress template) and keeps the Continuation Prompt in sync; writing it by hand here would fork the format.

Once the state file exists, add or update the Website block in `current-projects.md` using the format from `references/folder-convention.md`:

```markdown
## Website — Status: active
- Phase: Phase 1 — Kickoff & Scheduling
- Owner: Krystalyn
- Next action: Confirm kickoff brief and book approval holds
- Detail: project-management/website.md
- Updated: YYYY-MM-DD
```

## Step 3: Scaffold

Create the BasicOps scaffold on the `*Client Flow` board (project ID `68655`) — the same board every project-hub skill uses for client work. Find the client's card with `list_tasks_in_project` (`projectId: 68655`, `filter_title` set to the client's short name); create subtasks under it with `parentTaskId` set to the card's id, matching the established client-card pattern.

**Backwards-scheduled milestones.** Start from the go-live deadline gathered in Step 1 and work backwards, assigning each preceding phase milestone a due date that leaves enough runway for the one after it (Project Planning SOP method — this is the point of asking for the deadline first). Use the wordpress-hub build phases as the milestone set:

| Milestone (working backwards from deadline) | Typical lead time before the next milestone |
|---|---|
| QA & Launch complete | = deadline |
| WordPress/Astro build complete | 1–2 weeks before launch |
| Design (prototype approved) complete | 1 week before build deadline |
| Copy (all pages copy-locked) complete | 1 week before design deadline |
| SEO/IA (sitemap approved) complete | 1 week before copy deadline |
| Intake (kickoff brief confirmed) complete | today, or 2–3 days out |

Adjust the lead times to fit the actual gap between today and the deadline — if the runway is short, compress evenly across phases rather than leaving QA squeezed at the end (QA is never compressed, per the wp-project-manager Astro template's scheduling rule). Assign owners from `references/team-roster.md`: Krystalyn (PM/copy), Jaimee (SEO/QA), Aiya (build/launch), Michael (strategy/sign-off).

Create one BasicOps subtask per milestone with its computed due date and owner. Report the BasicOps card link once created.

## Step 4: Comms

Draft the client kickoff email using the **Website** section of `references/templates/kickoff-emails.md`. Fill `[Client]`, `[First name]`, and `[milestone date]` (use the SEO/IA or Design milestone from Step 3 — whichever the template's "sitemap and design concepts ready for your review" language matches). Present the draft in chat. **Draft only — never send.**

## Step 5: Handoff

Report to the user:

- State file created (path, confirm it was created via `wp-project-manager`, not hand-written)
- BasicOps card link and the milestone subtasks created
- Client kickoff email drafted (Step 4)
- Next action: the first milestone's owner and task

Then hand off explicitly: "Kickoff complete. Next: run `lhm-wordpress-hub:website-build-orchestrator` — it reads the platform answer from `client_profile.md` and routes to the WordPress or Astro build flow accordingly." Either invoke that agent directly if the user wants to continue now, or leave the pointer for them to run it themselves.

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- This skill never does delivery work itself — sitemap, copy, design, and build all belong to `lhm-wordpress-hub`.
