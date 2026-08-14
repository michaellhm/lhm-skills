---
name: monthly-review
description: "Monthly per-client review engine with three modes. Use this when the user says 'monthly review', 'monthly wrap', 'monthly update for [client]', 'end of month review', 'prep for the [client] meeting', 'meeting prep', or 'account review'. Wrap mode (KP): walk through every open task/project/milestone, confirm done/carried/blocked, update all project files and BasicOps, draft the monthly achievement email, and generate the client report with Google Ads and SEO wins. Internal mode (Michael): 30-minute account review with anomaly flags. Pre-meeting mode: brief + timed agenda."
---

# Monthly Review

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the review-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Run the monthly per-client review cycle from `references/cadences.md`. This is the flagship client-success skill — it's what turns a month of delivery work into three things: KP's client-facing wrap, Michael's internal account check, and the pre-meeting brief that ties them together. `pm-orchestrator` triggers this automatically on cadence; it's also invoked directly at any point.

All three modes share one data pull (Step 2) before branching into mode-specific work.

## Step 1: Mode selection

Infer the mode from phrasing:

- **"wrap" / "monthly update for [client]" / "monthly wrap"** → Wrap mode (Step 3)
- **"prep for the meeting" / "meeting prep" / "brief me for [client]"** → Pre-meeting mode (Step 5)
- **"account review" / "internal review" / "internal"** → Internal mode (Step 4)

If the phrasing doesn't clearly land on one of the three, ask which mode before doing anything else — don't guess and burn an MCP pull on the wrong one:

"Which review — wrap (client-facing, KP), internal (account review, Michael), or pre-meeting (brief + agenda)?"

Confirm the client name too if it isn't already obvious from context.

## Step 2: Shared data pull (all modes)

Run this once, regardless of which mode Step 1 selected. Every mode below assumes this data is already in hand.

Read the client's state first:
- `client_profile.md` and `goals.md` at the client root.
- `current-projects.md` (per `references/folder-convention.md`) for the active-process index.
- Every file under `project-management/` that exists for this client (`onboarding.md`, `website.md`, `landing-pages.md`, `gmb.md`, `seo.md`, `google-ads.md`, `blog.md` — whichever are present; not every client has all of them).

Then pull external data. Use the date range "this calendar month to date vs. the prior calendar month" unless the client's meeting cadence calls for a different window (e.g. mid-month prep runs partial-month-to-date vs. the same partial window last month, so the comparison stays apples-to-apples):

| Data | Tool | What to pull |
|---|---|---|
| Traffic + conversions | `analytics-mcp` → `run_report` | GA4 sessions/users and conversions, this month vs. prior month, for the client's property |
| Ad performance | `GoogleAds` → `execute_gaql` | Spend, conversions, and CPL (cost per lead) trend for the client's account, this month vs. prior month |
| Rankings/clicks | `gscServer` → `compare_search_periods` | Ranking position and click movement for the client's property, comparing the same two periods |
| Open/completed work | `basicops` → `list_tasks` / `list_tasks_in_project` | Open and recently-completed tasks for the client on the `*Client Flow` board (project ID `68655`) — filter by the client card or its subtasks |

**On any MCP failure or missing auth:** state plainly what's missing ("GSC data unavailable — gscServer isn't authenticated") and continue with everything else that did come back. This is a hard rule, not a style preference: **never fabricate a number, trend, or ranking to fill the gap.** A missing metric is reported as missing, in every mode and every report file this skill produces.

## Step 3: Wrap mode (KP)

Client-facing monthly wrap. Produces `project-management/meetings/YYYY-MM-DD-monthly-wrap.md`, refreshed state files, updated BasicOps, and a drafted achievement email.

### 3a. Build the follow-up list and walk it

Build one combined list:
- Every open BasicOps task for the client (from Step 2's pull).
- Every unticked `- [ ]` milestone across the `project-management/` files read in Step 2 (onboarding, website, landing pages, GMB, SEO, Google Ads, blog — whichever exist).

Present the count, then walk the list **one item at a time** — never batched, never as a single multi-part `AskUserQuestion`:

"Item 3 of 11 — [BasicOps] 'Riverside location ad copy approval'. Done, carried over, or blocked? If blocked, why?"

Wait for KP's answer before moving to the next item. The only three valid answers are done / carried over / blocked (with a reason for blocked). Do not infer an answer from KP moving on to something else, and do not mark anything done on a guess — this is the wrap-mode-specific guardrail below, and it exists because this list feeds a client-facing report next.

### 3b. Apply answers

Apply each item's answer as soon as it's confirmed, before moving to the next item in the walk:

- **Done** — BasicOps-sourced item: `update_task` to mark it complete. File-sourced milestone: tick `- [x]` in the owning `project-management/*.md` file and append a one-line entry to that file's `## Log`.
- **Carried over** — leave the BasicOps task open / the milestone unticked; add an inline note ("carried to <next month>") so it's visibly distinct from an item nobody has looked at yet.
- **Blocked** — leave open/unticked; add an inline note with KP's stated reason.

Once the whole list is walked and every item has an applied answer, do the aggregate updates in one pass:
- Refresh each affected `current-projects.md` block (status, next action, updated date) per `references/folder-convention.md`'s block format. **Note:** blocks in the wild may predate this format — `post-meeting-review` and older skill runs write their own shape. Update the fields within whatever block shape you find rather than rewriting it wholesale; only use the folder-convention format when creating a block that doesn't exist yet.
- Post one monthly summary comment to the client's BasicOps card (`create_message_in_task`) — done / carried / blocked counts, and each item under its bucket.

### 3c. Draft the achievement email

Invoke `lhm-project-hub:client-update-email`, seeded with the confirmed completions from 3b so it doesn't need to re-derive them or re-ask its own intake questions — pass "monthly review / routine check-in" as the reason and the list of done items as the work completed. **Draft only, never sent** — same as every client-facing comms step in this hub.

### 3d. Generate the client report

Save to `project-management/meetings/YYYY-MM-DD-monthly-wrap.md`:

```markdown
# Monthly Wrap — <Client> — <Month Year>

## Work completed this month
- <each "done" item from 3a/3b, plain-English framing — what changed and why it matters>

## Google Ads wins
- Spend: $<amount> (<vs. last month>)
- Conversions: <count> (<vs. last month>)
- CPL trend: $<this month> vs. $<last month> — <plain-English one-liner: "your cost per enquiry is heading the right way / needs attention">
[If GoogleAds data is missing: "Google Ads data unavailable this month — <what's missing>."]

## SEO wins
- Ranking movement: <summary from compare_search_periods> — <plain-English one-liner>
- Click movement: <summary> — <plain-English one-liner>
[If GSC data is missing: state it plainly, same as above.]

## Website performance (GA4)
- Conversions: <count> (<vs. last month>) — <plain-English one-liner explaining what a "conversion" means for this client, e.g. "people who booked or enquired through your site">
[If GA4 data is missing: state it plainly.]

## Next month's focus
- <each "carried over" or "blocked" item from 3a, reframed forward — what's happening next, not what didn't happen>
```

Every metric line gets a plain-English one-liner — write it the way `client-update-email` writes for clients: no jargon, acronyms explained on first use, honest about what a number means rather than just reporting it. Don't borrow client-update-email's email structure or send mechanics here (this is a standalone report file, not an email), just its plain-language voice.

## Step 4: Internal mode (Michael)

30-minute internal account review. Produces `project-management/meetings/YYYY-MM-DD-monthly-internal.md`. Nothing here touches the client — no client-facing draft, no BasicOps writes beyond an optional Jaimee brief (below).

```markdown
# Internal Account Review — <Client> — <Month Year>

## 1. Any unexpected issues?
- <anomaly flags, or "None flagged this month">

## 2. Right direction?
- <one paragraph: is the account trending the way goals.md targets say it should, using Step 2's month-over-month data>
- [If the underlying GA4/Ads/GSC data needed for this call is missing: "Data unavailable — <source> pull failed; cannot assess direction this month." Never default to "on track" or "within normal range" when the number behind the assessment is absent.]

## 3. Promised work on track?
- <cross-check current-projects.md / project-management files against what was committed — handover doc promises, prior meeting-brief action items, sales commitments — flag anything slipping>

## 4. Forward ideas
- <opportunities surfaced by this review that aren't yet scoped as work>

## Anomaly flags (references/cadences.md)
- Organic traffic: <flag if down ≥20% month-on-month>, <"Within normal range" only if the GA4/GSC comparison actually returned data>, or **["Data unavailable — <source> pull failed; do not infer" if the comparison data needed to compute this is missing]**
- Update cadence: <flag if >7 days since the last client-facing update (client_updates/ folder or BasicOps card activity)>, <"Within normal range" only if both sources were actually checked>, or **["Data unavailable — <source> couldn't be checked; do not infer" if neither source was reachable]**

## Converting-keyword → SEO opportunity
- <cross-reference GoogleAds execute_gaql's best-converting keywords against gscServer's organic position for the same terms; flag terms converting well in paid but ranking weakly or not at all organically>
- Keyword brief for Jaimee: <drafted below if an opportunity was found, else "No opportunity found this month">
```

**Anomaly flags.** Compute both directly from Step 2's data — traffic drop from the GA4/GSC comparison, update gap from the most recent file in `client_updates/YYYY-MM/` or the most recent BasicOps card message, whichever is more recent. Per `references/cadences.md`, a traffic drop ≥20% escalates to Michael immediately — since Michael is the one running internal mode, surface it prominently at the top of the report rather than burying it in section 1's list. **"Within normal range" is only a valid value when the underlying data actually came back.** If Step 2 flagged the GA4/GSC pull or the update-cadence check as missing or failed, the flag line says so explicitly — never let an absent metric collapse into the "normal" branch by default. This applies to every metric-driven line in this report, not just the two flags: section 2's direction call is equally subject to it.

**Converting-keyword → SEO suggestions.** Pull the client's top-converting Google Ads keywords (execute_gaql, sorted by conversions) and check each against its organic ranking (compare_search_periods / the client's GSC data). Where a keyword converts well in paid but the client doesn't rank for it organically (or ranks weakly), that's a content opportunity worth a brief.

**Keyword brief for Jaimee, when relevant.** If an opportunity was found, draft a short brief (the keyword, why it converts, the organic gap) and include it in the report above. Ask Michael whether to also push it to BasicOps as a subtask assigned to Jaimee (per `references/team-roster.md`, Jaimee owns local SEO/technical SEO/content) — don't assume the assignment, ask first, same as every other assignment decision in this hub.

### 4a. Hermes-prepared overnight handoff

When internal mode is run by Hermes as an overnight or on-demand marketing review, prepare one
review-delivery handoff after the report content is complete. Hermes sends it to the configured
ChatGPT/Codex delivery worker, which saves and verifies the Drive artefact and invokes
`lhm-project-hub:basicops-task-manager` for the BasicOps parent. Hermes does not need either
connector directly.

- Reuse the client's existing monthly-review parent for the same service and month when one exists;
  dedupe key: `basicops:<client-slug>:<service>:monthly-review:<yyyy-mm>`.
- For Google Ads, assign the parent to Michael in `Michael Tasks` (`49020`) / `Google Ads Flow`
  (`106309`). For other services, use the client's established `*Client Flow` mother task unless a
  governed approval queue is recorded. Record Hermes as `orchestration_owner=hermes`, not as a
  BasicOps assignee.
- Put only the exact LHM metadata line and verified report/dashboard URLs in Description.
- In Discussion, put a short human overview, data-confidence caveats and the five highest-priority
  proposed actions in order, labelled `A1`–`A5` and `Proposed — not approved`. End by asking Michael
  to approve, defer, reject or reorder specific labels through Hermes.
- Initial state is `workflow_state=waiting-on-michael-via-hermes` and
  `approval_status=pending-michael`. Do not create execution subtasks or dispatch execution agents
  during review preparation.
- When Michael later says to tackle the client, Hermes reads this parent and tells him exactly what
  is waiting. Only explicit action-level approval releases work. The shared task manager then
  creates approved subtasks and governs one-at-a-time specialist dispatch, evidence updates and
  final verification.

If dispatch, Drive or BasicOps is unavailable, preserve the exact payload and delivery run ID,
return `analysis complete; delivery incomplete`, and mark the handoff pending. Never ask Michael to
paste the payload and never claim the review is queued for him without both verified URLs.

## Step 5: Pre-meeting mode

Brief + timed agenda ahead of the monthly client meeting. Produces `project-management/meetings/YYYY-MM-DD-meeting-brief.md`.

Read the most recent file in `project-management/meetings/` that carries action items — prefer the latest `*-monthly-wrap.md`; if none exists yet (e.g. the first meeting after onboarding), fall back to the latest `*-meeting-notes.md` from `client-meeting-email`. Pull its "Next month's focus" / "Action Items" section as last meeting's open items.

```markdown
# Meeting Brief — <Client> — <Meeting Date>

## Last meeting's action items
- <pulled from the file above, each with its original owner (LHM/Client)>

## This month's numbers
- <Step 2's month-over-month traffic, conversions, ad spend/CPL, ranking movement — same figures the wrap/internal reports use, condensed to what's meeting-relevant>
- [If any of Step 2's data sources came back missing or unauthenticated: list each one plainly, e.g. "Google Ads data unavailable — GoogleAds MCP not authenticated." Never omit the line or substitute a placeholder number — a gap here is a gap Michael needs to know about walking into the meeting.]

## Agenda
<pre-filled from references/templates/meeting-agenda.md, with the "Project updates & deliverables" and "Last meeting's action items" sections populated from the above>
```

Use `references/templates/meeting-agenda.md` as the timed-agenda skeleton verbatim — don't redesign the agenda structure, just fill it with this client's specifics.

Close with a reminder, exactly: "After the meeting, run `lhm-project-hub:client-meeting-email` to capture it, then `lhm-project-hub:post-meeting-review` to triage the follow-up."

## Rules

- Client-facing emails are drafts only, never sent.
- Follow-up items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- Wrap mode never marks an item done without KP's explicit answer — one item at a time, no batch questions, no ticks without it.
