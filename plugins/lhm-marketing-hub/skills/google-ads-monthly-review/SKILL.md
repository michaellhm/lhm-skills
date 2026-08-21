---
name: google-ads-monthly-review
description: "Analyse Google Ads performance, determine the AdPulse zone and measurement confidence, reconcile prior commitments, and return up to five evidence-backed actions with specialist skill routes. Use for monthly reviews, zone checks, account health checks, or the review stage of a Google Ads Lead session. The Google Ads Lead owns subsequent action selection and skill chaining."
license: MIT
---

# Google Ads Monthly Review

## Purpose

Analyse Google Ads account performance, determine the performance zone and measurement confidence,
and return no more than five prioritised actions. This skill decides what matters; it does not execute
the actions. The persistent `google-ads` Lead owns authority classification, sequencing and specialist
skill dispatch after this review returns.

## When to Use

- **Quick zone check** — "What zone are we in?"
- **Health check** — Quick account status before a meeting
- **Start of month** — Lightweight analysis without full execution
- **After major changes** — Reassess zone after budget or performance shifts

Read and follow `${CLAUDE_PLUGIN_ROOT}/references/google-ads-monthly-operating-model.md` before starting.
Read `${CLAUDE_PLUGIN_ROOT}/references/google-ads-zone-action-library.md` before selecting actions.

## Prerequisites

- Client name and account details
- Campaign performance data for the last 30 days
- Target CPA or ROAS goal
- Monthly budget target

## How It Works

### Step 1: Load canonical context

Use the canonical Obsidian context envelope supplied by Hermes. It must cover objectives, conversion definitions, service area, budget/targets, campaign strategy, open issues, prior decisions and commitments, Drive destination and any existing BasicOps task. Do not create blank local context files. Report precise gaps.

### Step 2: Data access and comparison

**Option A: Google Ads MCP (Preferred)**
If Google Ads MCP is available, fetch campaign performance data automatically. All accounts live under **MCC 394-736-1921**. Pull the current 30 days and immediately preceding 30 days using aligned definitions.

**Option B: CSV Export (Fallback)**
If MCP isn't available, ask the user to provide a campaign performance CSV with columns: Campaign, Cost, Conversions, Conv. Value, CPA, ROAS, Budget. Date range: last 30 days.

**Zone data specifically: use AdPulse MCP directly, don't hand-calculate it.** Read `${CLAUDE_PLUGIN_ROOT}/references/adpulse-integration.md` and pull `pacing`/`kpiPercentage` straight from AdPulse for Step 3-4 below instead of computing budget pacing % / performance variance % from raw Google Ads numbers. That reference also covers a known gap in the zone matrix (Under-pacing + Poor performance) and how to handle it.

Also reconcile every open commitment from the previous review against live settings. When Ads conversions are zero, falling, inconsistent or suspicious, query GA4 for the same date windows before diagnosing demand or tracking.

### Step 3: Calculate metrics

If AdPulse MCP is connected, pull `pacing` and `kpiPercentage` directly (see `references/adpulse-integration.md`) and skip the manual math below. Only calculate by hand if AdPulse isn't available for this account:

- **Budget Pacing %**: (Actual Spend / Expected Spend) x 100
- **Performance Variance %**: (Actual CPA / Target CPA) x 100 — or ROAS equivalent
- **Remaining Budget**: Monthly Budget - Actual Spend
- **Required Daily Spend**: Remaining Budget / Days Remaining

### Step 4: Determine performance zone and measurement confidence

Judge `Good` or `Poor` against the canonical business target CPA/ROAS. Show current-versus-prior movement separately as trend context; do not use a worsening prior-period comparison to redefine an otherwise on-target result as Poor.

| Budget Pacing | Performance | Zone |
|--------------|-------------|------|
| >110% | Poor (CPA >110% of target or ROAS <90% of target) | Red — CRITICAL |
| 90-110% | Poor | Orange — High |
| <90% | Good (CPA ≤110% of target or ROAS ≥90% of target) | Yellow — Scaling |
| >110% | Good | Blue — Low |
| 90-110% | Good | Green — Maintain |

**Gap: Under-pacing (<90%) + Poor performance has no defined cell.** Follow `references/adpulse-integration.md` and state the rationale. Keep this performance judgement separate from measurement confidence.

Assign measurement confidence independently:

- `high` — core conversion definitions reconcile and Ads/GA4 evidence is consistent
- `medium` — a bounded discrepancy exists but directional performance remains usable
- `low` — missing or conflicting evidence materially affects CPA or action selection

A tracking concern does not by itself make the performance zone Red. Use `unclassified` if evidence cannot support a zone.

If the mechanical matrix produces Yellow but unfinished commitments or a negative trend make scaling unwise, retain `performance_zone=yellow` and add an operational caution such as `treat as orange`. Do not replace the mechanical classification.

See the **Zone Reference** section below for full zone decision trees and execution checklists.

### Step 5: Generate the top five proposed actions

Use the matched zone as a candidate library, not a mandatory checklist. Rank its highest-impact
candidates first, then filter them through live evidence, client economics, prior commitments and
campaign-level exceptions. A failing campaign may justify Orange/Red repair actions inside a Yellow
account, but the account's mechanical zone must remain unchanged.

Provide no more than five prioritised action items. Each recommendation must include:
- Action title and urgency
- Estimated impact
- Specific metrics to target
- Reasoning
- Owning specialist skill
- Dependencies and verification method
- Authority class: `lead` or `michael`
- Mutation scope: `read_only`, `prepare_only`, `manual_execution`, or `consequential_approval`

### Step 6: Dispatch, save and verify delivery

Saving the read-only monthly report and creating its review record are part of delivery, not consequential Google Ads actions. Do this **before** asking for approval.

1. Read the client's canonical service file and use its exact Google Drive destination for Google Ads deliverables. Do not infer a folder from the client name when a destination is recorded.
2. Return the completed one-page report to Hermes. Hermes submits one bounded monthly-review delivery job to the configured ChatGPT/Codex bridge; it must not require a direct Drive or BasicOps connector in the Hermes session.
3. The delivery worker saves `google_ads/YYYY-MM/monthly-review-YYYY-MM.md`, reads it back, and captures the observed Drive file ID/URL and parent folder.
4. In the same job, the worker invokes `lhm-project-hub:basicops-task-manager`, deduplicates and creates or updates the review parent, writes the discussion and reads it back.
5. Hermes polls the recorded delivery run ID and resumes it rather than submitting duplicates. It may proceed to the approval gate only after receiving verified Drive and BasicOps URLs.

If the destination is missing, dispatch is unavailable, either connector is unavailable, or either readback fails:

- preserve the completed report content in the worker result;
- set the business work state to `needs review` (or `failed` when no report was produced);
- state the exact missing destination, permission or verification problem;
- say `analysis complete; delivery incomplete`, preserve the delivery run ID and do not silently save somewhere else.

### Step 7: Hermes overview, BasicOps record and approval gate

Return the compact overview and structured handback defined in the operating model after the delivery
worker returns both verified links. Put the report URL, overview, top five, authority classes and any
exact consequential decision in the BasicOps discussion; do not create execution subtasks merely
from report delivery. If a Michael decision is actually required, set the governed waiting-on-Michael
state. Otherwise hand the action register to the Google Ads Lead for sequential dispatch.

The Google Ads Lead classifies each action after review delivery. Lead-authorised actions become
`approved` automatically and enter the sequential queue. Consequential actions remain
`waiting_approval` and Hermes asks Michael only for the exact decision required. Do not stop the
entire action register merely because one action requires Michael.

### Step 8: Recommend Next Skills

For every selected action, name the skill the Google Ads Lead should dispatch next:

| Issue Identified | Recommended Skill |
|-----------------|-------------------|
| Budget cuts/increases | `bid-budget-optimizer` |
| Keyword waste/negatives | `keyword-optimizer` |
| Ad performance/refresh | `ad-copy-generator` |
| Landing page issues | `landing-page-optimizer` |

Include specific parameters to pass to the next skill.

### Step 9: Sequential specialist execution

Once the report is saved and the Lead has classified action authority, hand off to the shared guided
task execution protocol. Lead-authorised actions may begin immediately; Michael-authorised actions
wait at their exact consequential gate:

`${CLAUDE_PLUGIN_ROOT}/references/guided-task-execution.md`

Read it and follow it. Hermes dispatches exactly one approved action at a time. After every worker handback, record evidence and status in Obsidian and BasicOps before dispatching another action.

## Report format

Save and verify the zone assessment through Step 6:

**File**: `google_ads/YYYY-MM/monthly-review-YYYY-MM.md`

**This report is a one-pager. One page maximum.** Keep prose to a minimum, lead with the data, no preamble or wrap-up. The whole thing should fit on a single printed page.

Include the **Execution Checklist for the matched zone only** (see Zone Reference section below). Do not paste all five zone checklists — only the one that applies.

```
# Google Ads Monthly Review: [Client Name]
Date: [Today's Date]

## Performance Zone: [Emoji] [Zone] — [Priority]

Measurement confidence: [High/Medium/Low] — [one-line reason]

### Key Metrics
- Monthly Budget: $X,XXX | Actual Spend: $X,XXX (XX% of month elapsed)
- Budget Pacing: XXX% | Target CPA: $XX | Actual CPA: $XX | Performance vs Target: XX%
- Prior 30d CPA: $XX | Change: XX%

### Prior Commitments
| Commitment | Live verification | Status |
|------------|-------------------|--------|
| ... | ... | Applied/Partial/Not applied/Unknown |

### Campaign Breakdown
| Campaign | Spend | Conv | CPA | vs Target | Status |
|----------|-------|------|-----|-----------|--------|
| ... | ... | ... | ... | ... | ... |

### Priority Actions
1. [Action] — [Impact] — [Reasoning]
2. ...

### [Zone] Execution Checklist
[Paste the matched zone's checklist from zone-analysis.md]

### Recommended Next Skills
- [Skill name] for [specific focus]
```

## Tips

- Run at month start (days 1-5 is ideal)
- Do not skip consequential approval gates
- Follow zone priorities: Red/Orange before Yellow/Green
- For execution across skills, return to the persistent `google-ads` Lead

## Related Skills

- **Bid & Budget Optimizer**: Run when budget issues are identified
- **Keyword Optimizer**: Run when wasted spend is flagged
- **Ad Copy Generator**: Run when ad performance is poor
- **Landing Page Optimizer**: Run when conversion rate needs improvement

---

*Quick zone check — let AdPulse guide your priorities*

---

## Zone Reference

### Zone Determination Matrix

| Budget Pacing | Performance | Zone | Priority |
|--------------|-------------|------|----------|
| >110% (Over) | >110% CPA or <90% ROAS (Poor) | Red | CRITICAL |
| 90-110% (On Pace) | >110% CPA or <90% ROAS (Poor) | Orange | High |
| <90% (Under) | ≤110% CPA or ≥90% ROAS (Good) | Yellow | Medium |
| >110% (Over) | ≤110% CPA or ≥90% ROAS (Good) | Blue | Low |
| 90-110% (On Pace) | ≤110% CPA or ≥90% ROAS (Good) | Green | Maintain |

### Red Zone Execution Checklist

Stabilise the patient: check vitals, treat life-threatening issues first, then stabilise.

**One-off**
- [ ] Budget reduced to 80-90% of ideal daily calculation
- [ ] Budget allocation tweaked to favour best performers
- [ ] Conversion actions are firing (check GA4 directly via `analytics-mcp` before asking the client — see "Conversion quality before volume" in the philosophy doc)
- [ ] Geo-targeting tight enough
- [ ] Search partners performance checked
- [ ] Ad extensions - all relevant types exist
- [ ] Search term audit - wasted spend focus
- [ ] Blocked search terms checked
- [ ] Competitor analysis - check ads and special deals
- [ ] Best campaigns - can they be expanded? (duplicate with different bid strategy / match type upgrade / demographics / audiences / geo)

**Daily**
- [ ] Budget reduced to 80-90% of ideal daily calculation
- [ ] Budget allocation tweaked to favour best performers
- [ ] All ads approved
- [ ] No 404 errors on landing pages

**Weekly**
- [ ] Budgets lasting all day - adjust bids down if not
- [ ] Search terms - wasted spend focus
- [ ] Check troubleshooter to find weak metrics

**Monthly**
- [ ] Check performance & add bid modifiers on anomalies (devices / locations / audiences / demographics)
- [ ] Pause/exclude poor performers (landing pages / ad groups / ads / keywords / search terms)
- [ ] Bid strategy - change/experiment?
- [ ] Landing page speed
- [ ] Bounce rate or time-on-page metrics

### Orange Zone Execution Checklist

Flip the Red Zone priorities: performance fixes on top, budget increases only once performance is back on track.

**One-off**
- [ ] Budget allocation tweaked to favour best performers
- [ ] Conversion actions are firing (check GA4 directly via `analytics-mcp` before asking the client — see "Conversion quality before volume" in the philosophy doc)
- [ ] Feed issues checked
- [ ] Geo-targeting tight enough
- [ ] Search partners performance checked
- [ ] Ad extensions - all relevant types exist
- [ ] Search term audit - wasted spend focus
- [ ] Blocked search terms checked
- [ ] Competitor analysis - check ads and special deals
- [ ] Best campaigns - can they be expanded? (duplicate with different bid strategy / match type upgrade / demographics / audiences / geo)

**Daily**
- [ ] Budget allocation tweaked to favour best performers
- [ ] All ads approved
- [ ] No 404 errors on landing pages

**Weekly**
- [ ] Budgets lasting all day - adjust bids down if not
- [ ] Search terms - wasted spend focus
- [ ] Check troubleshooter to find weak metrics

**Monthly**
- [ ] Check performance & add bid modifiers on anomalies (devices / locations / audiences / demographics)
- [ ] Pause/exclude poor performers (landing pages / ad groups / ads / keywords / search terms)
- [ ] Bid strategy - change/experiment?
- [ ] Landing page speed
- [ ] Bounce rate or time-on-page metrics

### Yellow Zone Execution Checklist

Easy zone: increase budgets where impactful, expand existing campaigns, then add new campaign types/networks.

**One-off**
- [ ] Budget allocation - increase where impactful
- [ ] Raise bids in best campaigns
- [ ] Blocked search terms checked
- [ ] Turn on search partners?
- [ ] Ad extensions - all relevant types exist
- [ ] Best campaigns - can they be expanded? (duplicate with different bid strategy / match type upgrade / keyword expansion / new ad formats / demographics / audiences / geo)
- [ ] Remarketing campaigns?
- [ ] Pay-for-conversions (display)?
- [ ] Add new campaign types?
- [ ] New networks (Bing)?

**Daily**
- [ ] Budget allocation - ensure top performers are not limited
- [ ] All ads approved
- [ ] No 404 errors on landing pages

**Weekly**
- [ ] Budgets lasting all day? Increase budgets if not

**Monthly**
- [ ] Check performance & add positive bid modifiers on anomalies (devices / locations / audiences / demographics)
- [ ] Bid strategy - change/experiment?

### Blue Zone Actions (ordered steps)

The whitepaper gives Blue no checklist. Run these in order until spend is back in line:

1. [ ] Ask the client for more budget (performance is good - more leads/sales is an easy conversation)
2. [ ] Decrease bids, starting with poorer performers (10%/day until spend drops)
3. [ ] Decrease budget on poorer performers if bids alone do not pull spend back
4. [ ] Turn off worst-performing keywords / ad groups / campaigns as a last resort

### Green Zone Maintenance

- [ ] Test a new strategy or experiment (use the stability to learn)
- [ ] Incremental optimisation - small, low-risk improvements
- [ ] Monitor competitor impression share and offers
- [ ] Plan for next month / anticipate seasonal shifts
- [ ] Document what is working as a template for other accounts
