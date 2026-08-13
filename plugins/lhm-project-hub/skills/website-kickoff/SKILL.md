---
name: website-kickoff
description: "Kick off a new website build (WordPress or Astro) — intake, state file, BasicOps scaffold with backwards-scheduled milestones, client kickoff email, and handoff to the WordPress hub. Use this when the user says 'website kickoff', 'kick off the website', 'start the website project', 'new website for [client]', or 'begin the site build process'. Follows references/kickoff-pattern.md. Delivery work itself belongs to lhm-wordpress-hub:website-build-orchestrator, never this skill."
---

# Website Kickoff

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the website-kickoff payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Turn a newly-sold or newly-scoped website project into a running process: a state file the rest of the agency can read, a BasicOps scaffold with real dates, and a drafted client email. Follows `references/kickoff-pattern.md`'s 5-step shape exactly. This skill never touches sitemap, copy, design, or build work itself — that's `lhm-wordpress-hub`'s job, starting the moment Step 5 hands off.

## Step 1: Intake

Read `references/kickoff-pattern.md` first if you haven't already this session — its 5-step shape is what this skill implements. Ask these questions **one at a time, never batched**:

1. **Platform** — Astro or WordPress?
2. **New build or rebuild?** (rebuild of an existing live site vs. greenfield)
3. **What is the go-live / launch deadline?** (required by the pattern — this is what backwards scheduling in Step 3 works from)
4. **Who supplies content** — us (LHM writes copy) or the client (client supplies copy)?
5. **Domain/hosting access status** — do we already have DNS and hosting access, or is that still outstanding?

If this kickoff follows directly from `sales-handover`, `client-onboarding` or `existing-client-website-handover`, check the client folder first — platform may already be recorded in the client profile or handover, and the deadline may already be in the handover doc. Confirm rather than re-asking anything already on file, but still ask anything genuinely missing.

For an accepted existing-client website handover, reuse and enrich the existing website state file and `Current Projects.md` block. Never restart general client onboarding or create a parallel website project.

## Step 2: State

Locate or create the client folder per `references/folder-convention.md`. **Do not write `project-management/website.md` directly** — create it by invoking `lhm-project-hub:wp-project-manager` in its Mode 1 (Create), passing along what Step 1 gathered (platform, deadline, content ownership). That skill owns the file's structure (Astro vs. legacy WordPress template) and keeps the Continuation Prompt in sync; writing it by hand here would fork the format.

Once the state file exists, add or update the Website block in `current-projects.md` using the format from `references/folder-convention.md`:

```markdown
## Website — Status: active
- Phase: <as reported by the wp-project-manager state file, e.g. "Phase 0 — Kickoff & Scheduling" for Astro, or "Phase 1 — Client Onboarding & Strategy" for WordPress>
- Owner: Kristalyn
- Next action: Confirm kickoff brief and book approval holds
- Detail: project-management/website.md
- Updated: YYYY-MM-DD
```

Don't hardcode a phase label here — the Astro and legacy WordPress templates in `wp-project-manager` name their opening phase differently, so always copy the `Current Phase` value straight out of the state file `wp-project-manager` just created rather than assuming one.

## Step 3: Scaffold

Create the BasicOps scaffold on the `*Client Flow` board (project ID `68655`) — the same board every project-hub skill uses for client work. Find the client's card with `list_tasks_in_project` (`projectId: 68655`, `filter_title` set to the client's short name); create subtasks under it with `parentTaskId` set to the card's id, matching the established client-card pattern.

**Backwards-scheduled milestones.** Start from the go-live deadline gathered in Step 1 and work backwards, assigning each preceding phase milestone a due date that leaves enough runway for the one after it (Project Planning SOP method — this is the point of asking for the deadline first).

For WordPress, use this milestone set:

| Milestone (working backwards from deadline) | Typical lead time before the next milestone |
|---|---|
| QA & Launch complete | = deadline |
| WordPress/Astro build complete | 1–2 weeks before launch |
| Design (prototype approved) complete | 1 week before build deadline |
| Copy (all pages copy-locked) complete | 1 week before design deadline |
| SEO/IA (sitemap approved) complete | 1 week before copy deadline |
| Intake (kickoff brief confirmed) complete | today, or 2–3 days out |

For Astro, use the canonical Decap/CMS learning workflow from `wp-project-manager`:

| Milestone (working backwards from deadline) | Accountable owner |
|---|---|
| QA and launch complete | Jaimee + Aiya |
| Final client Decap approval complete | Kristalyn |
| Team WhatsApp staging review closed | Kristalyn, with Aiya resolving issues |
| Remaining-page rollout built/reviewed in Astro | Kristalyn + Aiya |
| Copy Learning Guide approved in Obsidian | Kristalyn |
| Five-template Decap batch client-approved | Kristalyn |
| Five-template Markdown batch internally approved and built | Kristalyn + Michael + Aiya |
| Homepage HTML prototype client-approved | Kristalyn + Aiya |
| Homepage copy approved | Kristalyn + Michael |
| Sitemap approved and five template-validation pages selected | Jaimee + Michael |
| Strategy documents approved | Kristalyn |
| Intake and kickoff scheduling complete | Kristalyn |

For Astro, do not schedule all copy as locked before design. Homepage approval precedes the HTML prototype; prototype approval precedes the five-template Markdown/CMS learning batch; the client-approved Copy Learning Guide precedes scaled remaining-page production.

Adjust the lead times to fit the actual gap between today and the deadline — if the runway is short, compress evenly across phases rather than leaving QA squeezed at the end (QA is never compressed, per the wp-project-manager Astro template's scheduling rule). Assign owners from `references/team-roster.md`: Kristalyn (PM/copy), Jaimee (SEO/QA), Aiya (build/launch), Michael (strategy/sign-off).

Prepare one BasicOps subtask per milestone with its computed due date and owner. Create and report the BasicOps card link only after the applicable authority check below passes.

**Astro BasicOps authority:** default to `prepare-only`. Present the exact proposed task, owner, context, dependency, due date and acceptance test to Kristalyn before creating or assigning it. Create automatically only when the canonical project record contains Michael's explicit graduation of routine task creation for this workflow. That graduation never covers scope, strategy, client commitments, publishing, merge, deployment or launch.

## Step 4: Comms

Draft the client kickoff email using the **Website** section of `references/templates/kickoff-emails.md`. Fill `[Client]`, `[First name]`, and `[milestone date]` (use the SEO/IA or Design milestone from Step 3 — whichever the template's "sitemap and design concepts ready for your review" language matches). Present the draft in chat. **Draft only — never send.**

## Step 5: Handoff

Report to the user:

- State file created (path, confirm it was created via `wp-project-manager`, not hand-written)
- BasicOps card link and the milestone subtasks created
- Client kickoff email drafted (Step 4)
- Next action: the first milestone's owner and task

Then hand off explicitly: "Kickoff complete. Next: run `lhm-wordpress-hub:website-build-orchestrator` — it reads the platform answer from `client_profile.md` and routes to the WordPress or Astro build flow accordingly." Either invoke that agent directly if the user wants to continue now, or leave the pointer for them to run it themselves.

For Astro, include this handoff context: the standard delivery path uses a homepage HTML prototype, Decap CMS, a Michael-selected five-page template-validation batch, a client-specific `Copy Learning Guide.md`, flexible Kristalyn-owned remaining-copy batches, a required team WhatsApp staging review and a separate formal SEO/launch QA gate.

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- This skill never does delivery work itself — sitemap, copy, design, and build all belong to `lhm-wordpress-hub`.
