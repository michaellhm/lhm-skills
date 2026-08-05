---
name: google-ads-kickoff
description: "Kick off a new Google Ads campaign build — gates on conversion tracking, intake, state file, BasicOps scaffold with backwards-scheduled milestones, client kickoff email, and handoff to the Ads specialist. Use this when the user says 'Google Ads kickoff', 'kick off Google Ads', 'start the ads campaign', or 'Ads audit and setup'. Follows references/kickoff-pattern.md. Delivery work itself belongs to the lhm-marketing-hub google-ads agent, never this skill. This is the skill client-onboarding Phase 4 delegates Ads campaign build work to."
---

# Google Ads Kickoff

Turn a newly-sold or newly-scoped Google Ads engagement into a running process: a state file the rest of the agency can read, a BasicOps scaffold with real dates, and a drafted client email. Follows `references/kickoff-pattern.md`'s 5-step shape exactly. This skill never touches account audits, campaign builds, or bid/budget work itself — that's the `lhm-marketing-hub` `google-ads` agent's job, starting the moment Step 5 hands off.

This is the skill `client-onboarding`'s Phase 4 ("Delegate, don't do") routes Ads campaign build work to. It can also be run standalone for an existing client — the tracking gate below applies either way.

## Step 0: Tracking gate

Before intake, read the client's `project-management/onboarding.md` and check the `## Phase status` line for Phase 3 — Tracking & Config. If that box isn't ticked `[x]`:

**STOP.** Conversion tracking isn't confirmed live yet, and building or launching Ads campaigns without it wastes spend. Tell the user tracking needs to be verified first, and route them to `lhm-project-hub:client-onboarding` — it will resume at Phase 3 and work through the remaining tracking items (GA4-collecting, Ads-conversions imported, and the rest of the tracking-setup checklist) until the gate condition is met. Do not proceed with intake until Phase 3 is ticked.

If `onboarding.md` doesn't exist (this client never ran Tier 1 onboarding, or tracking was set up outside that pipeline), ask the user directly whether conversion tracking is confirmed live before proceeding — don't assume.

## Step 1: Intake

Read `references/kickoff-pattern.md` first if you haven't already this session — its 5-step shape is what this skill implements. Ask these questions **one at a time, never batched**:

1. **Existing account or new build?** — if existing, get the CID and confirm an account audit is needed; if new, confirm account structure needs building from scratch.
2. **Monthly budget?**
3. **Conversion tracking live?** — confirm what Step 0 already found; if `onboarding.md` didn't exist, this is where that answer gets recorded.
4. **What is the launch date?** (required by the pattern — this is what backwards scheduling in Step 3 works from)

If this kickoff follows directly from `sales-handover` or `client-onboarding`, check the client folder first — CID, budget, or launch date may already be recorded in `client_profile.md` or the handover doc. Confirm rather than re-asking anything already on file, but still ask anything genuinely missing.

## Step 2: State

Locate or create the client folder per `references/folder-convention.md`. Create `project-management/google-ads.md` directly (no PM sub-skill owns this file) with this skeleton:

```markdown
# Google Ads — <Client>
Started: YYYY-MM-DD · Status: active
## Milestones
- [ ] Account audit / structure plan complete
- [ ] Campaign build complete (keywords, ad copy, targeting, budgets)
- [ ] Tracking re-verified
- [ ] Client approval received
- [ ] Campaign live
## Log
- YYYY-MM-DD: Kickoff. <existing/new account, CID if existing, budget, launch date from Step 1>.
```

Fill `<Client>` and `Started` (today's date) from `current-projects.md` / the handover doc.

Once the state file exists, add or update the Google Ads block in `current-projects.md` using the format from `references/folder-convention.md`:

```markdown
## Google Ads — Status: active
- Phase: Kickoff — account audit / structure plan in progress
- Owner: Michael
- Next action: Complete account audit (existing) or account structure plan (new)
- Detail: project-management/google-ads.md
- Updated: YYYY-MM-DD
```

## Step 3: Scaffold

Create the BasicOps scaffold on the `*Client Flow` board (project ID `68655`) — the same board every project-hub skill uses for client work. Find the client's card with `list_tasks_in_project` (`projectId: 68655`, `filter_title` set to the client's short name); create subtasks under it with `parentTaskId` set to the card's id, matching the established client-card pattern.

**Backwards-scheduled milestones.** Start from the launch date gathered in Step 1 and work backwards, assigning each preceding milestone a due date that leaves enough runway for the one after it (Project Planning SOP method — this is the point of asking for the deadline first). Use the audit → build → tracking check → approval → launch milestone set:

| Milestone (working backwards from deadline) | Typical lead time before the next milestone |
|---|---|
| Campaign live | = launch date |
| Client approval received | 2–3 days before launch |
| Tracking re-verified (conversions live in the new/updated campaigns) | 2–3 days before approval |
| Campaign build complete (keywords, ad copy, targeting, budgets) | 1 week before launch |
| Account audit (existing) or account structure plan (new) | today, or 2–3 days out |

Adjust the lead times to fit the actual gap between today and the launch date — if the runway is short, compress evenly across milestones rather than leaving client approval squeezed at the end. Assign owners from `references/team-roster.md`: Michael (audit/strategy sign-off, campaign plans), Kristalyn (client approval coordination).

Create one BasicOps subtask per milestone with its computed due date and owner. Report the BasicOps card link once created.

## Step 4: Comms

Draft the client kickoff email using the **Google Ads** section of `references/templates/kickoff-emails.md`. Fill `[Client]`, `[First name]`, and `[milestone date]` (use the "campaign draft ready for your approval by" milestone from Step 3 — this maps to the Client approval received milestone). Present the draft in chat. **Draft only — never send.**

## Step 5: Handoff

Report to the user:

- State file created (path, `project-management/google-ads.md`)
- BasicOps card link and the milestone subtasks created
- Client kickoff email drafted (Step 4)
- Next action: the first milestone's owner and task

Then hand off explicitly: "Kickoff complete. Next: run the `lhm-marketing-hub` `google-ads` agent — it picks up the account audit or structure plan and manages the campaign build." Either invoke that agent directly if the user wants to continue now, or leave the pointer for them to run it themselves.

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- This skill never does delivery work itself — account audits, campaign builds, and bid/budget work all belong to the `lhm-marketing-hub` `google-ads` agent.
