---
name: quarterly-review
description: "Quarterly per-client strategy review: pulls three months of GA4/Ads/GSC data plus the quarter's monthly reports, analyses goal progress and channel performance, and drafts the next 3/6-month campaign plan for Michael's approval. Use this when the user says 'quarterly review', 'quarterly strategy', '90 day review', 'next quarter plan', or 'campaign plan for [client]'."
---

# Quarterly Review

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the review-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Run the quarterly per-client strategy cycle. Where `monthly-review` turns a month of delivery into a wrap, this skill turns a quarter of delivery into a forward plan: goal progress against `goals.md` targets, what worked and what didn't across the last three months, and a drafted campaign plan for the next 3–6 months that Michael signs off before anything moves.

Confirm the client name if it isn't already obvious from context.

## Step 1: Pull the quarter's data

Read the client's state first:
- `client_profile.md` and `goals.md` at the client root — `goals.md`'s Channel KPIs and Annual targets are the baseline the whole review is measured against.
- `current-projects.md` (per `references/folder-convention.md`) for the active-process index.
- Every file under `project-management/` that exists for this client (`onboarding.md`, `website.md`, `landing-pages.md`, `gmb.md`, `seo.md`, `google-ads.md`, `blog.md` — whichever are present).
- The **last three** `project-management/meetings/YYYY-MM-DD-monthly-*.md` files. Prefer `*-monthly-wrap.md` for a given month (it carries the client-facing metrics recap); fall back to that month's `*-monthly-internal.md` if no wrap exists. These three files are the month-by-month trend line this review is built on — read them in date order.

Then pull external data for the trailing three calendar months (the quarter just completed) compared against the three months before that, so every figure has a same-length prior window to trend against:

| Data | Tool | What to pull |
|---|---|---|
| Traffic + conversions | `analytics-mcp` → `run_report` | GA4 sessions/users and conversions across the trailing 3-month window vs. the prior 3-month window, for the client's property |
| Ad performance | `GoogleAds` → `execute_gaql` | Spend, conversions, and CPL (cost per lead) trend across the trailing 3-month window vs. the prior 3-month window, for the client's account |
| Rankings/clicks | `gscServer` → `compare_search_periods` | Ranking position and click movement across the trailing 3-month window vs. the prior 3-month window, for the client's property |
| Open/completed work | `basicops` → `list_tasks` / `list_tasks_in_project` | Open and recently-completed tasks for the client on the `*Client Flow` board (project ID `68655`) — filter by the client card or its subtasks |

**On any MCP failure or missing auth:** state plainly what's missing ("GSC data unavailable — gscServer isn't authenticated") and continue with everything else that did come back. This is a hard rule, not a style preference: **never fabricate a number, trend, or ranking to fill the gap.** A missing metric is reported as missing, in every section of the review report and every objective in the campaign plan this skill produces — no metric-driven line collapses into a "steady" or "on track" default when the data behind it didn't come back.

## Step 2: Analyse and produce the quarterly review report

Work through four things, each evidence-linked back to Step 1's data — never assert a trend, win, or loss without citing the figure or file it came from:

1. **Goal progress vs. targets** — for each channel with a target in `goals.md`, compare the quarter's actuals against it. If `goals.md` has no target set for a channel, say so plainly rather than inventing one to compare against.
2. **Channel performance shifts** — month-by-month movement across the three monthly reports plus Step 1's 3-month-vs-prior-3-month figures: is each channel trending up, down, or flat, and by how much.
3. **What worked / what didn't** — plain bullets, each citing the specific data point or file it's drawn from. No fabrication: if there's no evidence for a claim, don't make the claim.
4. **Risks** — anomalies flagged in the internal monthly reviews, anything slipping in `current-projects.md`, blocked items carried across more than one monthly report.

Save to `project-management/meetings/YYYY-MM-DD-quarterly-review.md`:

```markdown
# Quarterly Review — <Client> — Q<N> <Year>

## Goal progress vs targets
- <channel>: target <from goals.md> vs actual <from Step 1> — <plain-English evaluation>
[If goals.md has no target for this channel: "No target set in goals.md for <channel> — nothing to compare against."]
[If the actual figure needed for this line is missing: "Data unavailable — <source>; do not infer."]

## Channel performance shifts (quarter-over-quarter)
- Google Ads: <spend / conversions / CPL trend across the 3 months, evidence-linked>
[If GoogleAds data is missing: "Data unavailable — GoogleAds MCP; do not infer."]
- SEO: <ranking / click trend across the 3 months, evidence-linked>
[If GSC data is missing: "Data unavailable — gscServer; do not infer."]
- Website (GA4): <sessions / conversions trend across the 3 months, evidence-linked>
[If GA4 data is missing: "Data unavailable — analytics-mcp; do not infer."]

## What worked / what didn't
- <each bullet cites the data point or file it's drawn from>

## Risks
- <each bullet, or "None flagged this quarter" if the internal reviews and current-projects.md genuinely show nothing>

## Delivery track record (last 3 months)
- <done / carried / blocked counts pulled from the three monthly reports, one line per month>
```

Every metric line follows the missing-data discipline from Step 1: an explicit "Data unavailable — <source>; do not infer" branch, never a silent gap and never a default-to-normal assessment.

## Step 3: Draft the campaign plan

Draft the next 3/6-month campaign plan from Step 2's analysis. This is a draft for Michael to review — it does not touch BasicOps, `current-projects.md`, or any client-facing file yet. That only happens in Step 4, and only after Michael approves.

- **Objectives** — pulled from `goals.md`'s Channel KPIs and Annual targets sections. If a channel has no target in `goals.md`, note it as a gap to fill rather than inventing an objective for it.
- **Initiatives per channel** — for each channel that's active for this client (per `current-projects.md` and the `project-management/` files present), list concrete initiatives. Each initiative gets:
  - **Owner** — from `references/team-roster.md` (Jaimee for SEO/technical SEO/content, Aiya for design/site work, Kristalyn for client comms and delivery coordination, Michael for strategy and Google Ads direction, Josephine for billing-adjacent items) — always spelled **Kristalyn**, never "Kristalynn" or "KP" in this file.
  - **Target month** — the calendar month the initiative is aimed at completing or launching in, within the quarter (or the following quarter, if this is a 6-month plan).
- **Expected outcomes stated as hypotheses, never promises.** Every expected-outcome line uses "we expect" or "hypothesis:" framing and never states a guaranteed number. Write "Hypothesis: tightening negative keywords should reduce wasted spend; we expect CPL to trend down over the quarter" — never "This will cut CPL by 15%." If Step 2 found no evidence to support a hypothesis, don't include one for that initiative — leave the expected-outcome line as "No hypothesis yet — needs more data" rather than manufacturing one.

Save to `project-management/campaign-plan-YYYY-QN.md`:

```markdown
# Campaign Plan — <Client> — Q<N> <Year>

## Objectives
- <objective, from goals.md>
[If goals.md has no target for a channel this plan covers: "No target set in goals.md for <channel> — flag to Michael before this plan is finalised."]

## Initiatives

### <Channel, e.g. Google Ads>
| Initiative | Owner | Target month | Expected outcome |
|---|---|---|---|
| <initiative> | <owner, per team-roster.md> | <month> | <"We expect ..." / "Hypothesis: ..." — never a guaranteed number> |

### <Channel, e.g. SEO>
| Initiative | Owner | Target month | Expected outcome |
|---|---|---|---|

<repeat per active channel>
```

**Present the draft to Michael for approval.** State plainly that this is a draft — the skill drafts, Michael decides. Do not proceed to Step 4 on an assumed yes; wait for explicit approval. If Michael requests changes, revise and re-present rather than partially applying Step 4 against an unapproved version.

## Step 4: On approval

Only run this step once Michael has explicitly approved the campaign plan (or an edited version of it).

### 4a. Create BasicOps tasks for month-1 initiatives

"Month 1" = every initiative in the approved plan whose target month is the quarter's first calendar month.

Find the client's card: `list_tasks_in_project` with `projectId: 68655`, `filter_title` set to the client's short/common name, on the `*Client Flow` board. If no card is found, tell the user plainly and ask before creating anything standalone.

For each month-1 initiative:
1. `create_task` with `projectId: 68655`, `parentTaskId: <card id>`, `section: 107750`, `title: "<Acronym> - Campaign - <initiative>"` (`<Acronym>` per `client_profile.md`'s `Acronym:` field — if missing, derive and confirm with the user per the standard first-letter-of-each-word pattern before using it). At most one line in `description`.
2. `create_message_in_task` with the full briefing: **Why it matters** (the objective it serves and the evidence from Step 2 behind it) and **What done looks like** (the initiative's own definition of done). Two short bullet lists.
3. `update_task` with `assignee` set to the owner already named for this initiative in the approved plan — no separate assignment question here, since Michael's approval of the plan already confirmed who owns what. Resolve the owner's name to a BasicOps user id via `list_users` first if `assignee` needs one rather than an email/name.

If BasicOps isn't authorized, skip this step and tell the user plainly: "BasicOps isn't connected. I've saved the approved plan to the file, but you'll need to add the month-1 tasks manually."

### 4b. Update current-projects.md

Add or refresh a campaign-plan block, per `references/folder-convention.md`'s block format:

```markdown
## Quarterly Campaign Plan (Q<N> <Year>) — Status: active
- Phase: Month 1
- Owner: Michael
- Next action: <first month-1 initiative due, or "BasicOps tasks created — see card">
- Detail: project-management/campaign-plan-YYYY-QN.md
- Updated: YYYY-MM-DD
```

**Note:** if a campaign-plan block already exists in `current-projects.md` from a prior quarter, it may not be in this exact shape — update the fields within whatever block shape you find rather than rewriting it wholesale (same rule `monthly-review` follows). Only use the format above when creating a block that doesn't exist yet.

### 4c. Offer the client-facing summary

Ask whether to draft the client-facing quarterly summary email. If yes, invoke `lhm-project-hub:client-update-email`, seeded with the approved plan's objectives and headline initiatives so it doesn't need to re-derive them — pass "Monthly review / routine check-in" as the reason (closest fit; note inline this is a quarterly cadence if it matters to the draft) and the objectives/initiatives as the work summary. **Draft only, never sent** — same as every client-facing comms step in this hub.

## Rules

- Client-facing emails are drafts only, never sent.
- Missing or unauthenticated MCP → state plainly what's missing and continue with what did come back, never silently skip a section.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics, targets, or client data — every metric-driven line in the review report and every objective in the campaign plan traces to a real figure or an explicit "Data unavailable — <source>; do not infer" branch.
- Expected outcomes in the campaign plan are hypotheses, never promises — "we expect" / "hypothesis:" framing only, never a guaranteed number.
- The campaign plan is a draft until Michael approves it explicitly. BasicOps tasks, the `current-projects.md` update, and the client-facing summary offer only happen after that approval — Step 4 never runs on an assumed yes.
