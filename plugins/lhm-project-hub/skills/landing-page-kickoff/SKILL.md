---
name: landing-page-kickoff
description: "Kick off a new PPC landing page campaign — intake, state file, BasicOps scaffold with backwards-scheduled milestones, client kickoff email, and handoff to the WordPress hub. Use this when the user says 'landing page kickoff', 'kick off the LP campaign', 'start landing pages', or 'new PPC landing pages'. Follows references/kickoff-pattern.md. Delivery work itself belongs to lhm-wordpress-hub:landing-page-orchestrator, never this skill."
---

# Landing Page Kickoff

Turn a newly-sold or newly-scoped landing page campaign into a running process: a state file, a BasicOps scaffold with real dates, and a drafted client email. Follows `references/kickoff-pattern.md`'s 5-step shape exactly. This skill never touches copy, prototype, subsite, or deploy work itself — that's `lhm-wordpress-hub`'s job, starting the moment Step 5 hands off.

## Step 1: Intake

Read `references/kickoff-pattern.md` first if you haven't already this session — its 5-step shape is what this skill implements. Ask these questions **one at a time, never batched**:

1. **Which campaign / ad groups?** (the Google Ads campaign name, and the ad groups that need dedicated landing pages — a CSV export can answer this if the user has one)
2. **What is the go-live / launch deadline?** (required by the pattern — this is what backwards scheduling in Step 3 works from)
3. **Copy source** — existing copy to adapt, or written from scratch?
4. **Subsite or standalone?** — does this campaign land on a new LeadScalePro multisite subsite, or an existing one?

If this kickoff follows directly from `sales-handover` or `client-onboarding`, check the client folder first for anything already on file (campaign details from the sales call, deadline from the handover doc) and confirm rather than re-asking, but still ask anything genuinely missing.

## Step 2: State

Locate or create the client folder per `references/folder-convention.md`. **Do not write `project-management/landing-pages.md` directly** — create it by invoking `lhm-project-hub:lp-project-manager`, passing along what Step 1 gathered (campaign/ad groups, deadline, copy source, subsite status). That skill owns the file's structure and its Google Ads CSV import handling; writing it by hand here would fork the format.

Once the state file exists, add or update the Landing Pages block in `current-projects.md` using the format from `references/folder-convention.md`:

```markdown
## Landing Pages — Status: active
- Phase: Phase 1 — Copy & Content
- Owner: Kristalyn
- Next action: Import Google Ads CSV and confirm copy source
- Detail: project-management/landing-pages.md
- Updated: YYYY-MM-DD
```

## Step 3: Scaffold

Create the BasicOps scaffold on the `*Client Flow` board (project ID `68655`) — the same board every project-hub skill uses for client work. Find the client's card with `list_tasks_in_project` (`projectId: 68655`, `filter_title` set to the client's short name); create subtasks under it with `parentTaskId` set to the card's id, matching the established client-card pattern.

**Backwards-scheduled milestones.** Start from the go-live deadline gathered in Step 1 and work backwards, assigning each preceding phase milestone a due date that leaves enough runway for the one after it (Project Planning SOP method — this is the point of asking for the deadline first). Use the `lp-project-manager` phase set as the milestone backbone:

| Milestone (working backwards from deadline) | Typical lead time before the next milestone |
|---|---|
| QA & Go-Live complete | = deadline |
| Remaining ad-group pages deployed (Phase 7) | 3–4 days before launch |
| Gutenberg conversion + HTML deploy complete (Phases 5–6) | 1 week before deadline |
| Subsite setup complete (Phase 4) | 3–4 days before deploy deadline |
| Prototype approved by client (Phase 3) | 1 week before subsite deadline |
| Master copy approved by client (Phase 1) | 1 week before prototype deadline |

Adjust the lead times to fit the actual gap between today and the deadline — if the runway is short, compress evenly across phases rather than squeezing QA at the end. Assign owners from `references/team-roster.md`: Kristalyn (PM/copy/client comms), Aiya (subsite, prototype, deploy), Jaimee (QA/compliance).

Create one BasicOps subtask per milestone with its computed due date and owner. Report the BasicOps card link once created.

## Step 4: Comms

Draft the client kickoff email using the **Landing Pages** section of `references/templates/kickoff-emails.md`. Fill `[Client]`, `[First name]`, and `[milestone date]` (use the master-copy or prototype milestone from Step 3 — whichever matches the template's "first landing page draft ready for review" language). Present the draft in chat. **Draft only — never send.**

## Step 5: Handoff

Report to the user:

- State file created (path, confirm it was created via `lp-project-manager`, not hand-written)
- BasicOps card link and the milestone subtasks created
- Client kickoff email drafted (Step 4)
- Next action: the first milestone's owner and task

Then hand off explicitly: "Kickoff complete. Next: run `lhm-wordpress-hub:landing-page-orchestrator` — it picks up from the state file and manages the campaign build." Either invoke that agent directly if the user wants to continue now, or leave the pointer for them to run it themselves.

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- This skill never does delivery work itself — copy, prototype, subsite, and deploy all belong to `lhm-wordpress-hub`.
