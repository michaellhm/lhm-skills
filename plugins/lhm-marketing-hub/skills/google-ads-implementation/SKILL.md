---
name: google-ads-implementation
description: Implement approved Google Ads recommendations from a BasicOps task. Use when Michael shares a BasicOps Google Ads task (link or name) and says "work on this task", "implement the recommendations", "action the review", "make the changes", or asks for an AdPulse Insights/Optimize sweep. Reconciles the task with live account data, presents every pending change for approval, applies approved changes through AdPulse, falls back to a guided Chrome session for anything AdPulse cannot do, verifies each change in Google Ads and logs the outcome back to the BasicOps task.
license: MIT
---

# Google Ads Implementation

## Purpose

Turn a Google Ads BasicOps task (usually a monthly review with proposed actions) into verified, logged account changes, with Michael approving every change.

The review skills decide *what* should change. This skill does the *doing*:

1. read the task and its history
2. confirm the live account still matches it
3. present each pending change in plain language
4. apply approved changes through AdPulse
5. apply what AdPulse cannot do through a guided Chrome session
6. verify every change in Google Ads
7. log the result on the BasicOps task

It also runs an **AdPulse sweep**: it pulls the AdPulse Insights and Optimize recommendations, checks each one against the account data, and sorts them into apply, reject or hold.

Read `${CLAUDE_PLUGIN_ROOT}/references/google-ads-departmental-delivery.md` for approval authority and evidence rules. This skill follows them; it does not relax them.

Supporting references in this skill folder:

- `references/adpulse-actions.md`: working AdPulse GraphQL calls (sweep, apply, ignore, run status)
- `references/browser-changes.md`: the guided Chrome procedure and UI paths for changes AdPulse cannot make

## Hard rules

- **Nothing changes in the account without Michael's explicit approval for that item.** A proposal in a task, a review manifest or an AdPulse recommendation is not approval. Approval covers only the item it names.
- **Budget, bidding strategy, conversion settings and campaign pauses are always consequential.** Only Michael can approve them. Ask for them by name.
- **Verify every change in Google Ads.** An AdPulse run with no errors is not proof. Read the change back with GAQL, or with a screenshot for UI-only settings.
- **Log to BasicOps after each batch of changes.** Mutate BasicOps only through the conventions of `lhm-project-hub:basicops-task-manager`.
- **Write for Michael in plain language.** Spell out every item in full sentences: what it is, what's done, what's pending, and what you need from him. Never compress the status into a dense multiple-choice question. He has had to reply "what are you asking?" when this was ignored.

## When to Use

- Michael shares a BasicOps task URL for a Google Ads review or implementation task
- "Implement the recommendations for [client]", "make the changes", "action A1-A5"
- "Do an AdPulse sweep", "check the Optimize tab", "review the AdPulse insights"
- Not for producing the monthly review itself: use `google-ads-monthly-review` for that
- Not for campaign builds: use `pmax-campaign-setup` or the Google Ads Lead

## Step 1: Resolve the BasicOps task

BasicOps links look like `https://app.basicops.com/481630853364967730?l=_805_31C_...`.

- The number in the path is the **workspace** ID, not the task ID. It also exceeds JavaScript integer precision, so passing it to `get_task` fails.
- The `l=` token can't be decoded. Find the task by listing: `list_tasks` with `filter_title` set to the client name, then match on the `url` field. Results can be large, so save them and filter by URL with a script.
- Then read `get_task`, `list_subtasks_in_task` and `list_messages_in_task`.

Read the messages newest first. **The most recent "Next handoff" is authoritative.** Earlier messages may be superseded: an earlier manifest can list $12.27/day as the budget while a later message records the live value as $11.64. Extract:

- actions already completed and verified
- actions approved but not yet applied
- actions still waiting on a decision
- open questions, trials in progress and their review dates
- the Drive review file and any local records it names

## Step 2: Load client context

From the client's canonical Obsidian folder, or the Drive client folder if that is what's connected:

- `client_profile.md` or the Google Ads service file: **Customer ID and login (MCC) customer ID**. Example: Any Stage Physio is 5308308105 with MCC 3947361921.
- Targets: the booking CPA goal and what counts as a conversion.
- Any live trial record (for example `google_ads/YYYY-MM/*-trial-*.md`) and its rules on what must not change mid-trial.

## Step 3: Reconcile with the live account (read-only)

Before proposing anything, confirm the task still matches reality using the Google Ads MCP (`execute_gaql`, with `login_customer_id` set to the MCC). Always check:

- campaign status, budget, bidding strategy, impression share and budget/rank lost share (last 30 days)
- ad group status and `primary_status` for every group the task mentions
- keywords in those groups, including paused ones
- the campaign negatives and shared negative lists attached to each campaign, with member counts
- the conversion actions: primary vs secondary, and included in conversions or not
- the account default call conversion: `customer.call_reporting_setting.call_conversion_action`

**Report drift before acting.** Examples found on Any Stage Physio:

- All three budgets had risen by about 13.6% since they were recorded.
- Ad groups the notes described as "serving zero" were actually paused.
- A group described as "empty" had ads but no keywords, while a sister group had keywords but no ads.

**GAQL gotchas**

- `DURING LAST_90_DAYS` is invalid. Use `BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`.
- `OR` is not supported in `WHERE`. Run separate queries.
- Selecting `ad_group_ad.ad.final_urls` currently makes the MCP call fail. Check that landing URLs are live with `landing_page_view.unexpanded_final_url`, or confirm them in the UI.
- `change_event` only reaches back 30 days and needs a `LIMIT`.
- PMax search terms: `search_term_view` returns nothing for PMax. Use `campaign_search_term_insight` (category level), and split conversions by action with `segments.conversion_action_name` on the campaign.

## Step 4: Build the action list and present it

List every pending item in full. For each one give:

- what the change is, in plain words, including the exact entities (campaign, ad group, keyword, list, IDs)
- the evidence behind it
- the channel it will go through: **AdPulse**, **Chrome**, or **Michael manually**, using the capability table below
- whether it is consequential

Then ask which items to proceed with. If Michael asks a strategy question mid-flow (for example "should we add PMax converting terms to Search?"), answer it with data before continuing.

### Capability table

| Change | AdPulse | Chrome UI |
|---|---|---|
| Pause or enable an ad group, keyword or ad | yes | yes |
| Add keywords to an ad group | yes | yes |
| Add or remove campaign negatives | yes | yes |
| Add or remove shared negative list keywords | yes | yes |
| Change an ad's final URL | yes | yes |
| Change a campaign budget | yes | yes |
| Change a campaign bidding strategy | yes | yes |
| Location targeting | yes | yes |
| PMax audience signals and search themes | **no** | yes |
| Account default call conversion action | **no** | yes |
| Conversion action primary/secondary, goals | **no** | yes |
| RSA copy edits and new assets | limited (`adCreate`) | yes |

## Step 5: Apply through AdPulse

Follow `references/adpulse-actions.md`.

1. Queue approved changes in a single `actionsQueueGoogle` call per logical batch. Keep consequential changes in their own batch so a failure doesn't block routine work.
2. Wait about 45-60 seconds, then check `actionRunInfo` for `ActionRunStatusRan` with an empty `errors` list.
3. Verify each change with GAQL (keyword status, ad group status, shared set `member_count`, `campaign.bidding_strategy_type`, budget).
4. Anything you can't read back (such as RSA final URLs): say so plainly and ask Michael to spot-check it in the UI.

## Step 6: Apply through Chrome

Follow `references/browser-changes.md`. In outline:

1. Open a new Chrome tab at `https://ads.google.com/aw/overview`. Don't build URLs with `__e=` or other parameters; they return a 400 error.
2. Tell Michael exactly where to go (account, campaign, screen) and to approve any "Confirm it's you" prompt. **Wait for him to say he's there.**
3. Screenshot, make the changes, save, then screenshot the saved state as proof.
4. If Google rejects something (for example a health-policy rejection of a search theme), remove that element, save the rest, and report the rejection with its policy reason. Never request a policy exemption without asking.

Account-level settings such as Goals > Conversions > Settings can be opened by URL once the account is selected, reusing the `ocid`/`__c`/`__u` parameters from the current tab URL.

## Step 7: AdPulse sweep (Insights and Optimize)

Run this when asked, or offer it at the end of an implementation session. Queries are in `references/adpulse-actions.md`.

1. Pull `insightsCountByCategory`, `insights` (with a fragment per insight type) and `performanceHighlights` for the account.
2. For each recommendation, check the evidence yourself with GAQL (search terms, conversions, CPC trend, keyword status, negatives) and against the client context (trials, core keywords, decisions already in the task).
3. Classify each one as **apply**, **reject** or **hold (with a date)**, with one line of evidence. Present them grouped that way and wait for approval.
4. Apply approved items (Step 5). Ignore rejected items permanently. Ignore held items with `until` set to the review date so they come back then.

### Triage rules learned in practice

- **Never accept negatives on core geo or brand terms.** AdPulse suggested "ryde", "north ryde physio" and "physio north ryde" as negatives for a North Ryde clinic. Reject these outright.
- **Treat n-gram negative suggestions as noise on low-conversion campaigns.** When a campaign has near-zero conversions, AdPulse flags every word pattern. Each time you ignore one batch, it offers the next ("near", "near me", then "physio north", "ryde physio"...). Ignore the first batch, then say the recommendation is noise for this account and stop.
- **"Blocked converters" is high value. Always investigate it.** It found that the Brand campaign had exact negatives on "anystage physio"/"anystage physiotherapy". Those terms had produced 7 conversions at about $5.70 each, and the traffic was leaking to PMax. The fix was to remove the negatives and add the terms as exact keywords.
- **Check the "smart bidding campaign remove" flag against conversion volume.** With fewer than about 15 conversions in 30 days, Maximize Conversions pushes CPCs up without learning. The evidence is the monthly average CPC trend and click volume. The fix is Maximize Clicks with a CPC cap near the historical average (as a bidding change it is consequential).
- **Hold, don't action, keyword pauses on core terms during a live trial.** Ignore until the trial review date.
- **Brand "add as keyword" suggestions in PMax** can't be actioned (PMax has no keywords). Ignore them, and consider brand exclusions on PMax at the next review.

## Step 8: Log to BasicOps

After each batch, add one message to the task with `create_message_in_task`:

- what changed (entities and IDs, AdPulse run IDs, before and after values)
- how it was verified, and anything unverified
- what was rejected or held, and why
- the next handoff: who does what, and when
- the line `AI authorship: Claude.`

Keep it factual. Include task and project links as returned by the tool. Don't mark the parent task complete unless Michael says so.

## Step 9: Close out

Reply to Michael with:

- what changed and how it was verified
- what's still open (with owner and date)
- the BasicOps message link

No step-by-step recap. Close any browser tab you opened unless he wants it kept.

## Related skills

- `google-ads-monthly-review`: produces the review this skill implements
- `google-ads-delivery-qa`: independent check of a worker's action and evidence before the Lead records it as done. Use it for high-stakes changes, or when a change was prepared by another worker.
- `keyword-optimizer`, `bid-budget-optimizer`, `pmax-optimizer`: specialist analysis when an item needs deeper work before approval
- `lhm-project-hub:basicops-task-manager`: BasicOps mutation conventions
