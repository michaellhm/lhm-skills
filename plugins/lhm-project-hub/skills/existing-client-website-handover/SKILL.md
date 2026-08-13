---
name: existing-client-website-handover
description: "Capture and transfer a new website project for an existing LHM client from Michael to Kristalyn. Use when Michael says an existing client needs a website, website rebuild, website handover, project handover to KP, or asks to start the website flow without repeating client onboarding. Interviews Michael one question at a time, prepares a canonical Obsidian handover for confirmation, routes it to Kristalyn for acceptance, then hands the accepted project to website-kickoff."
---

# Existing Client Website Handover

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the handover-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Transfer an existing client's newly scoped website project from Michael to Kristalyn without running sales handover or client onboarding again.

Read `references/handover-template.md` before drafting.

## 1. Resolve existing context

Locate `20 Clients/<Client>/` and read:

1. `<Client>.md`
2. `Current Projects.md`
3. `Goals.md`
4. `project-management/Website Rebuild.md` or `website.md`, when present
5. The latest linked meeting or Fathom evidence relevant to the website, when authorised and available

If no existing client folder exists, stop and route to `sales-handover` or `client-onboarding`. If a website record already exists, preserve and enrich it; never create a parallel project.

## 2. Interview Michael

State the confirmed context first, then ask only what is genuinely missing. Ask one question at a time in this order:

1. Why is the website project happening now, and what business result should it create?
2. What is included and explicitly excluded?
3. Is the platform Astro or WordPress, and is this a rebuild, migration or new build?
4. Who supplies the copy, and what existing content must be retained or migrated?
5. What design direction, references or constraints matter?
6. What has Michael already promised the client?
7. Who decides and approves on the client side?
8. What deadline or commercial constraint applies?
9. What known access gaps, dependencies, sensitivities or unresolved decisions remain?
10. What decisions does Michael retain after handover?

Do not re-ask a fact already evidenced in the client record. Present uncertain or conflicting facts for confirmation instead.

## 3. Prepare Michael's review bundle

Prepare but do not save:

- the complete handover note using the reference template
- the proposed changes to the existing website project record
- the proposed `Current Projects.md` website block
- the first three Kristalyn actions
- the single immediate BasicOps handoff, using the LHM title and discussion convention from `website-project-cockpit`

Show the critical summary: outcome, scope, exclusions, platform, deadline, client approval path, promises, blockers, retained Michael decisions and first three actions.

Ask Michael to approve or correct the bundle. A vague “looks fine” after the full bundle counts as approval; approval never grants client communication, task assignment to Kristalyn, merge, deployment or launch.

## 4. Save the approved handover

After Michael approves:

1. Create `project-management/Website Handover YYYY-MM-DD.md`.
2. Merge confirmed facts, owners and gaps into the existing website project record. Do not mark work complete without evidence.
3. Update the website block in `Current Projects.md` with:
   - overall owner: Kristalyn
   - immediate owner: Kristalyn — handover acceptance
   - phase: handover awaiting acceptance
   - next action: Kristalyn reviews and accepts or raises one consolidated set of questions
4. Record Michael's approval source and date in the handover.

Do not create BasicOps tasks yet. The approved handover is ready for Kristalyn, not accepted by her.

## 5. Kristalyn acceptance

When Kristalyn asks to review a pending website handover:

1. Resolve her operating identity from the Slack session; do not infer it from display text alone.
2. Read the approved handover and the website project record.
3. Present a short acceptance view:
   - outcome and scope
   - deadline
   - her first three actions
   - blockers and decisions still owned by Michael
   - the exact first BasicOps task payload
4. Ask her to either:
   - `Accept handover and create the task`, or
   - provide one consolidated set of questions for Michael.

On acceptance, record the source/date in the handover and update `Current Projects.md` to the real next phase. Then create only the exact approved BasicOps task through `website-project-cockpit`, with deduplication and read-back verification.

## 6. Start the website flow

After acceptance, invoke `lhm-project-hub:website-kickoff` with all answered intake fields. It must reuse the existing website state file and must not repeat general client onboarding.

`website-kickoff` may ask only for still-missing required kickoff inputs, one at a time. BasicOps remains prepare-only for team tasks during the pilot.

Finish with:

- handover note link
- website project link
- acceptance state
- verified BasicOps link if one was approved and created
- immediate next action and owner

## Boundaries

- Existing clients only; do not restart commercial onboarding.
- Draft and record internal handover only; do not send client communications.
- Do not invent scope, price, deadline, access or promises.
- Do not expose secrets or private founder context unrelated to the project.
- Do not merge, deploy, publish, launch or mark client approval.
- One project outcome per BasicOps task; detailed context stays in Obsidian and Hermes explains it on request.
