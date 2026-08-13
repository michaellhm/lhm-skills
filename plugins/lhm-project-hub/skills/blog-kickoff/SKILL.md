---
name: blog-kickoff
description: "Kick off a new blog/article content pipeline — intake, state file, BasicOps scaffold with backwards-scheduled milestones, client kickoff email, and handoff to the content engine. Use this when the user says 'blog kickoff', 'article marketing kickoff', 'start the blog engine', or 'content pipeline for [client]'. Follows references/kickoff-pattern.md. Delivery work itself belongs to lhm-content-engine:content-orchestrator, never this skill."
---

# Blog Kickoff

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the blog-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Turn a newly-sold or newly-scoped blog/article content engagement into a running process: a state file the rest of the agency can read, a BasicOps scaffold with real dates, and a drafted client email. Follows `references/kickoff-pattern.md`'s 5-step shape exactly. This skill never touches outlining, drafting, or publishing work itself — that's `lhm-content-engine`'s job, starting the moment Step 5 hands off.

## Step 1: Intake

Read `references/kickoff-pattern.md` first if you haven't already this session — its 5-step shape is what this skill implements. Ask these questions **one at a time, never batched**:

1. **Article cadence and volume** — how many articles per month?
2. **Topics source** — a CSV of pre-researched topics, or should keyword research feed the list?
3. **Approval flow** — does the client review and approve each draft before publishing?
4. **Publication targets** — WordPress only, or syndication to other channels as well?
5. **What is the deadline for the first published article (or first batch)?** (required by the pattern — this is what backwards scheduling in Step 3 works from)

If this kickoff follows directly from `sales-handover` or `client-onboarding`, check the client folder first — cadence or topic sourcing may already be recorded in `client_profile.md` or the handover doc. Confirm rather than re-asking anything already on file, but still ask anything genuinely missing.

## Step 2: State

Locate or create the client folder per `references/folder-convention.md`. Create `project-management/blog.md` directly (no PM sub-skill owns this file) with this skeleton:

```markdown
# Blog — <Client>
Started: YYYY-MM-DD · Status: active
## Milestones
- [ ] Pipeline setup complete (cadence, topics source, approval flow confirmed)
- [ ] First batch drafted
- [ ] Client review complete
- [ ] First article published
## Log
- YYYY-MM-DD: Kickoff. <cadence, topics source, approval flow, publication targets from Step 1>.
```

Fill `<Client>` and `Started` (today's date) from `current-projects.md` / the handover doc.

Once the state file exists, add or update the Blog block in `current-projects.md` using the format from `references/folder-convention.md`:

```markdown
## Blog — Status: active
- Phase: Kickoff — pipeline setup in progress
- Owner: Kristalyn
- Next action: Confirm topics list and cadence, start first batch
- Detail: project-management/blog.md
- Updated: YYYY-MM-DD
```

## Step 3: Scaffold

Create the BasicOps scaffold on the `*Client Flow` board (project ID `68655`) — the same board every project-hub skill uses for client work. Find the client's card with `list_tasks_in_project` (`projectId: 68655`, `filter_title` set to the client's short name); create subtasks under it with `parentTaskId` set to the card's id, matching the established client-card pattern.

**Backwards-scheduled milestones.** Start from the first-published-article deadline gathered in Step 1 and work backwards, assigning each preceding milestone a due date that leaves enough runway for the one after it (Project Planning SOP method — this is the point of asking for the deadline first). Use the pipeline milestone set:

| Milestone (working backwards from deadline) | Typical lead time before the next milestone |
|---|---|
| First article published | = deadline |
| Client review complete | 2–3 days before publish |
| First batch drafted | 1 week before client review |
| Pipeline setup complete (topics, cadence, approval flow confirmed) | today, or 2–3 days out |

Adjust the lead times to fit the actual gap between today and the deadline — if the runway is short, compress evenly across milestones rather than leaving client review squeezed at the end. Assign owners from `references/team-roster.md`: Jaimee (topics/keyword sourcing), Kristalyn (approval-flow coordination, client comms).

Create one BasicOps subtask per milestone with its computed due date and owner. Report the BasicOps card link once created.

## Step 4: Comms

Draft the client kickoff email using the **Blog** section of `references/templates/kickoff-emails.md`. Fill `[Client]`, `[First name]`, and `[milestone date]` (use the "first draft ready for review by" milestone from Step 3 — this maps to the First batch drafted milestone). Present the draft in chat. **Draft only — never send.**

## Step 5: Handoff

Report to the user:

- State file created (path, `project-management/blog.md`)
- BasicOps card link and the milestone subtasks created
- Client kickoff email drafted (Step 4)
- Next action: the first milestone's owner and task

Then hand off explicitly: "Kickoff complete. Next: run `lhm-content-engine:content-orchestrator` — it runs the full pipeline (outline, draft, social posts, quality control, publish, CSV update) for the first batch." Either invoke that agent directly if the user wants to continue now, or leave the pointer for them to run it themselves.

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- This skill never does delivery work itself — outlining, drafting, quality control, and publishing all belong to `lhm-content-engine:content-orchestrator`.
