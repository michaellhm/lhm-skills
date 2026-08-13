---
name: gmb-kickoff
description: "Kick off a new GMB/local SEO optimisation cycle — intake, state file, BasicOps scaffold with backwards-scheduled milestones, client kickoff email, and handoff to the GMB hub. Use this when the user says 'GMB kickoff', 'kick off GMB', 'start GMB optimisation', 'Google Business Profile kickoff', or 'local SEO kickoff'. Follows references/kickoff-pattern.md. Delivery work itself belongs to lhm-gmb-hub:gmb-orchestrator, never this skill."
---

# GMB Kickoff

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the GMB-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Turn a newly-sold or newly-scoped GMB/local SEO engagement into a running process: a state file the rest of the agency can read, a BasicOps scaffold with real dates, and a drafted client email. Follows `references/kickoff-pattern.md`'s 5-step shape exactly. This skill never touches diagnostics, GBP optimisation, or content work itself — that's `lhm-gmb-hub`'s job, starting the moment Step 5 hands off.

## Step 1: Intake

Read `references/kickoff-pattern.md` first if you haven't already this session — its 5-step shape is what this skill implements. Ask these questions **one at a time, never batched**:

1. **Locations count** — how many locations need GBP optimisation?
2. **GBP access confirmed?** — has Google Business Profile Owner access already been verified (onboarding Phase 2 — Platform Access), or is that still outstanding?
3. **Review baseline** — do we have a starting review count/rating to track improvement against?
4. **What is the go-live / launch deadline?** (required by the pattern — this is what backwards scheduling in Step 3 works from; for GMB this is the Month 0 exit-criteria target)

If this kickoff follows directly from `sales-handover` or `client-onboarding`, check the client folder first — locations and GBP access status may already be recorded in `client_profile.md` or `project-management/onboarding.md`. Confirm rather than re-asking anything already on file, but still ask anything genuinely missing.

## Step 2: State

Locate or create the client folder per `references/folder-convention.md`. **Do not write `project-management/gmb.md` directly** — create it by invoking `lhm-project-hub:gmb-project-manager`, passing along what Step 1 gathered (locations count, GBP access status, review baseline, deadline). That skill owns the file's structure (3-month cycle template, Month 0–3 phases, ranking history table); writing it by hand here would fork the format.

Once the state file exists, add or update the GMB block in `current-projects.md` using the format from `references/folder-convention.md`:

```markdown
## GMB — Status: active
- Phase: <as reported by the gmb-project-manager state file, e.g. "Month 0 — Onboarding">
- Owner: Jaimee
- Next action: Run baseline diagnostic and competitor audit
- Detail: project-management/gmb.md
- Updated: YYYY-MM-DD
```

Don't hardcode a phase label here — always copy the `Current Phase` value straight out of the `gmb.md` state file that `gmb-project-manager` just created rather than assuming "Month 0" (the same deference pattern `website-kickoff` uses for its Phase field).

## Step 3: Scaffold

Create the BasicOps scaffold on the `*Client Flow` board (project ID `68655`) — the same board every project-hub skill uses for client work. Find the client's card with `list_tasks_in_project` (`projectId: 68655`, `filter_title` set to the client's short name); create subtasks under it with `parentTaskId` set to the card's id, matching the established client-card pattern.

**Backwards-scheduled milestones.** Start from the go-live deadline gathered in Step 1 and work backwards, assigning each preceding milestone a due date that leaves enough runway for the one after it (Project Planning SOP method — this is the point of asking for the deadline first). Use the Month 0 onboarding tasks from the gmb-hub cycle (per `gmb-project-manager`'s template) as the milestone set:

| Milestone (working backwards from deadline) | Typical lead time before the next milestone |
|---|---|
| Month 0 exit criteria met | = deadline |
| Blog content schedule + 13 weekly GBP posts generated | 3–4 days before exit criteria |
| Citation audit, entity mapping, site architecture mapped | 1 week before content milestone |
| GBP profile fully optimised (categories, services, description, all fields) | 1 week before that |
| Baseline diagnostic + competitor audit complete | today, or 2–3 days out |

Adjust the lead times to fit the actual gap between today and the deadline — if the runway is short, compress evenly across milestones rather than leaving the content milestone squeezed at the end. Assign owners from `references/team-roster.md`: Jaimee (diagnostic, competitor audit, GBP optimisation, citations, entity mapping — SEO specialist), Kristalyn (GBP access coordination, client comms).

Create one BasicOps subtask per milestone with its computed due date and owner. Report the BasicOps card link once created.

## Step 4: Comms

Draft the client kickoff email using the **GMB (Google Business Profile)** section of `references/templates/kickoff-emails.md`. Fill `[Client]`, `[First name]`, and `[milestone date]` (use the "profile optimisation complete by" milestone from Step 3 — this maps to the GBP profile fully optimised milestone). Present the draft in chat. **Draft only — never send.**

## Step 5: Handoff

Report to the user:

- State file created (path, confirm it was created via `gmb-project-manager`, not hand-written)
- BasicOps card link and the milestone subtasks created
- Client kickoff email drafted (Step 4)
- Next action: the first milestone's owner and task

Then hand off explicitly: "Kickoff complete. Next: run `lhm-gmb-hub:gmb-orchestrator` — it detects the current phase from the `gmb.md` state file and routes to the right Month 0–3 phase agent." Either invoke that agent directly if the user wants to continue now, or leave the pointer for them to run it themselves.

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- This skill never does delivery work itself — diagnostics, GBP optimisation, content, and link building all belong to `lhm-gmb-hub`.
