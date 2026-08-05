---
name: seo-kickoff
description: "Kick off a new SEO engagement — intake, state file, BasicOps scaffold with backwards-scheduled milestones, client kickoff email, and handoff to the SEO specialist. Use this when the user says 'SEO kickoff', 'kick off SEO', 'start SEO for [client]', or 'SEO engagement start'. Follows references/kickoff-pattern.md. Delivery work itself belongs to the lhm-marketing-hub seo agent, never this skill."
---

# SEO Kickoff

Turn a newly-sold or newly-scoped SEO engagement into a running process: a state file the rest of the agency can read, a BasicOps scaffold with real dates, and a drafted client email. Follows `references/kickoff-pattern.md`'s 5-step shape exactly. This skill never touches audits, keyword research, or content work itself — that's the `lhm-marketing-hub` `seo` agent's job, starting the moment Step 5 hands off.

## Step 1: Intake

Read `references/kickoff-pattern.md` first if you haven't already this session — its 5-step shape is what this skill implements. Ask these questions **one at a time, never batched**:

1. **Target locations/services** — which locations and which services should the SEO work prioritise?
2. **Existing rankings baseline available?** — do we already have a rankings/traffic baseline (GSC, Local Falcon, prior audit), or does one need to be pulled fresh?
3. **Who writes the content** — us (LHM writes) or the client supplies copy for on-site changes?
4. **What is the deadline for first deliverables?** (required by the pattern — this is what backwards scheduling in Step 3 works from)

If this kickoff follows directly from `sales-handover` or `client-onboarding`, check the client folder first — target locations/services may already be recorded in `client_profile.md`, and the deadline may already be in the handover doc. Confirm rather than re-asking anything already on file, but still ask anything genuinely missing.

## Step 2: State

Locate or create the client folder per `references/folder-convention.md`. Create `project-management/seo.md` directly (no PM sub-skill owns this file) with this skeleton:

```markdown
# SEO — <Client>
Started: YYYY-MM-DD · Status: active
## Milestones
- [ ] Baseline audit complete
- [ ] Keyword research complete
- [ ] Quick wins implemented
- [ ] Content plan delivered
## Log
- YYYY-MM-DD: Kickoff. <target locations/services, baseline status, content ownership from Step 1>.
```

Fill `<Client>` and `Started` (today's date) from `current-projects.md` / the handover doc.

Once the state file exists, add or update the SEO block in `current-projects.md` using the format from `references/folder-convention.md`:

```markdown
## SEO — Status: active
- Phase: Kickoff — baseline audit in progress
- Owner: Jaimee
- Next action: Run baseline audit and keyword research
- Detail: project-management/seo.md
- Updated: YYYY-MM-DD
```

## Step 3: Scaffold

Create the BasicOps scaffold on the `*Client Flow` board (project ID `68655`) — the same board every project-hub skill uses for client work. Find the client's card with `list_tasks_in_project` (`projectId: 68655`, `filter_title` set to the client's short name); create subtasks under it with `parentTaskId` set to the card's id, matching the established client-card pattern.

**Backwards-scheduled milestones.** Start from the first-deliverables deadline gathered in Step 1 and work backwards, assigning each preceding milestone a due date that leaves enough runway for the one after it (Project Planning SOP method — this is the point of asking for the deadline first). Use the month-1 SEO milestone set:

| Milestone (working backwards from deadline) | Typical lead time before the next milestone |
|---|---|
| Content plan delivered | = deadline |
| Quick wins implemented | 3–4 days before content plan |
| Keyword research complete | 1 week before quick wins |
| Baseline audit complete | today, or 2–3 days out |

Adjust the lead times to fit the actual gap between today and the deadline — if the runway is short, compress evenly across milestones rather than leaving the content plan squeezed at the end. Assign owners from `references/team-roster.md`: Jaimee (baseline audit, keyword research, quick wins — SEO specialist), Michael (content plan sign-off — strategy).

Create one BasicOps subtask per milestone with its computed due date and owner. Report the BasicOps card link once created.

## Step 4: Comms

Draft the client kickoff email using the **SEO** section of `references/templates/kickoff-emails.md`. Fill `[Client]`, `[First name]`, and `[milestone date]` (use the "SEO audit and content plan ready to share by" milestone from Step 3 — this maps to the Content plan delivered milestone). Present the draft in chat. **Draft only — never send.**

## Step 5: Handoff

Report to the user:

- State file created (path, `project-management/seo.md`)
- BasicOps card link and the milestone subtasks created
- Client kickoff email drafted (Step 4)
- Next action: the first milestone's owner and task

Then hand off explicitly: "Kickoff complete. Next: run the `lhm-marketing-hub` `seo` agent — it picks up from here for the baseline audit, keyword research, and content strategy." Either invoke that agent directly if the user wants to continue now, or leave the pointer for them to run it themselves.

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- This skill never does delivery work itself — audits, keyword research, and content all belong to the `lhm-marketing-hub` `seo` agent.
