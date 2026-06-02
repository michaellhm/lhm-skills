---
name: quarterly-adversarial-review
description: "Adversarial 90-day Google Ads review that reconstructs last quarter's work from the client folder, red-teams the account and its assumptions against the prior 90 days, and assigns an AdPulse zone. Use this when the user mentions 'quarterly review', '90 day review', 'quarter review', 'adversarial review', 'red team the account', 'stress test the account', or 'Q review'. Runs every 90 days as a critical challenge to the account, not a friendly status update."
license: MIT
---

# Quarterly Adversarial Review

## Purpose

Every 90 days, stop trusting the account and attack it. This is a red-team review: assume the account is wasting money and that last quarter's wins were luck until the data proves otherwise. First reconstruct what was actually done last quarter and what was assumed when those decisions were made, then compare the last 90 days against the prior 90 days, assign the AdPulse zone, and produce a single-page verdict with the matched zone's execution checklist.

The monthly review asks "what zone are we in?" This review asks "what would a sceptical auditor tear apart if they were paid to find the waste, and which of last quarter's assumptions has the data since disproven?"

## When to Use

- **Quarterly cadence** — every 90 days, on schedule
- **Before a client renewal or budget conversation** — pressure-test the story before the client does
- **After a strong quarter** — challenge whether the gains are real or seasonal
- **When something feels off but the monthly reviews keep coming back green**

## The Two Lenses

This review runs two complementary review passes over the same account. Run both, every time.

**Lens 1 — The Cynic (attitude-driven).** You are a jaded auditor with zero patience for sloppy work. The account was handed to you by someone who wants you to believe everything is fine, and you expect to find problems. Be sceptical of every headline number. Look for what is *missing*, not only what is visibly wrong. Distrust improvements until they survive their counter-metric. Precise, professional tone — no hedging, no profanity, no personal attacks. If a campaign should die, write "kill it", not "consider reviewing".

**Lens 2 — The Path Tracer (method-driven).** You are a mechanical enumerator, not an intuition-led hunter. Walk *every* campaign, *every* metric pairing, and *every* assumption recovered in Step 1 — one by one, on a list — and for each one decide whether the account handles it or leaves a gap. Report only the gaps; discard the handled ones silently. This lens is orthogonal to the Cynic: it does not judge whether work is good or bad, it only finds unguarded paths the Cynic's intuition might skip.

The Cynic finds what feels wrong. The Path Tracer guarantees nothing was skipped. Neither alone is sufficient.

## MANDATORY EXECUTION

Execute the steps in the EXECUTION section **in exact order**. Do not skip steps or change the sequence. Each action within a step is required to complete that step. When a HALT condition triggers, follow its instruction exactly.

## Data Required

Two 90-day periods to compare. Default: **last 90 days vs the 90 days before that.**

### Option A: Google Ads MCP (Preferred)

Fetch from MCC **394-736-1921**. Pull both periods at campaign level:
- Impressions, Clicks, Cost
- Conversions, CPA, Conversion Value, ROAS
- Impression share, lost IS (budget), lost IS (rank)
- Current bid strategy and daily budget

Also pull the **90-day search terms report** and **90-day keyword report** for the waste hunt.

### Option B: CSV Fallback

Ask the user for two campaign exports (current 90 days + prior 90 days), plus a 90-day search terms export if they want the waste hunt to have teeth. Place files in `google_ads/YYYY-Qn/`.

## EXECUTION

### Step 1: Reconstruct prior work and surface assumptions

This is the content under review — the equivalent of the artifact a reviewer is handed. Before touching this quarter's numbers, read the client's Google Ads folder and rebuild what happened last quarter.

1. Read `client_profile.md` for the active client.
2. Scan the client's `google_ads/` folder (including dated `YYYY-MM/` and `YYYY-Qn/` subfolders) for every Google Ads trace from the last ~6 months:
   - `monthly-review-YYYY-MM.md` and `bid-budget-review-YYYY-MM.md` — zone calls and pacing/bid decisions
   - `keyword-optimization-*.md`, `keyword-changes-*.csv`, `negative-keywords-*.txt` — what was paused, added, or re-matched
   - `ad-copy-*.md` / `ad-copy-*.csv` — creative that was written or refreshed
   - `pmax-optimisation-90day-*.md`, `insights-export-*.csv` — PMax actions
   - the **prior** `quarterly-review-YYYY-Qn.md` — last quarter's verdict, findings, and the actions it prescribed
3. From those traces, build two lists:
   - **Actions taken** — the concrete changes made last quarter (bid strategy switches, budget moves, new campaigns, keyword pauses, creative refreshes).
   - **Assumptions made** — the *reasons* behind those actions, stated or implied. Every report carries assumptions: "switching to tCPA will hold CPA while scaling", "the brand campaign is incremental", "pausing those keywords won't cost conversions", "this zone is Yellow so we scale". Write each one as a falsifiable claim.
4. If the folder is empty or has no Google Ads traces, say so and tell the user this becomes a baseline review with no prior assumptions to test — then continue with the data passes.

The Actions list tells you what to judge. The Assumptions list becomes the input to Step 4 (each assumption is a path to walk).

### Step 2: Build the period comparison

For each campaign and for the account total, compute current 90 days vs prior 90 days:
- Cost, Conversions, CPA/ROAS, Conversion Value — each with direction and both values
- Always show the counter-metric alongside the headline (e.g. CPA improved but conversions down)

### Step 3: Cynical adversarial analysis (Lens 1)

Review with extreme scepticism — assume waste and fragility exist. Hunt hard:
- **Zero-conversion spend** over the quarter — name the keywords/campaigns and the dollar figure
- **CPA drift** — keywords/campaigns now >2x target that were fine last quarter
- **Hidden volume loss** — conversions down even where CPA looks good
- **Lost impression share to budget** on profitable campaigns — money left on the table
- **Stale creative** — RSAs unchanged for 90 days with declining CTR
- **Lucky-quarter check** — is the improvement explained by seasonality, a one-off order, a competitor dropping out, or double-counted tracking, rather than the work?

Quantify everything. "Roughly $X of the quarter's spend produced zero conversions" beats "some waste exists". Aim to surface **at least ten** distinct issues or risks before filtering. A thin list means you have not hunted hard enough — go back and look for what is missing, not only what is broken.

### Step 4: Exhaustive assumption and path enumeration (Lens 2)

Now switch to the mechanical pass. Take the **Assumptions list from Step 1** and the **full campaign list from Step 2** and walk every item on a checklist. Do not rely on intuition or on what Step 3 already found.

- For each **assumption** from last quarter: has the data since confirmed it, or quietly disproven it? Discard the confirmed ones silently. Report each disproven assumption as a finding: what was assumed, what the data now shows, and what it cost.
- For each **campaign**: walk its boundary conditions — pacing against budget, IS lost to budget vs rank, bid strategy still appropriate for its volume, conversion tracking still firing, a single keyword carrying the whole ad group.
- For each **metric pairing**: confirm the counter-metric was actually checked (CPA vs conversion volume, ROAS vs order count, CTR vs conversion rate).

Report only the unhandled paths and the broken assumptions. This pass exists to catch the gaps the Cynic's intuition skipped.

### Step 5: Determine the AdPulse zone

Use the same framework as the monthly review. Read the full decision tree and per-zone checklists from:

`${CLAUDE_PLUGIN_ROOT}/skills/google-ads-monthly-review/templates/zone-analysis.md`

| Budget Pacing (90-day) | Performance | Zone |
|--------------|-------------|------|
| >110% | Poor (CPA >110% of target or ROAS <90% of target) | 🔴 Red — CRITICAL |
| 90-110% | Poor | 🟠 Orange — High |
| <90% | Good (CPA ≤110% of target or ROAS ≥90% of target) | 🟡 Yellow — Scaling |
| >110% | Good | 🔵 Blue — Low |
| 90-110% | Good | 🟢 Green — Maintain |

Pacing is measured against the 90-day expected spend (monthly target × 3).

### Step 6: Validate completeness

Before writing the verdict, revisit the work and confirm nothing was skipped:
- Did every assumption from Step 1 get a verdict (confirmed or disproven)?
- Did every campaign get walked in Step 4?
- Was the counter-metric checked on every headline improvement claimed in Step 3?
- Add any newly found issue to the findings; drop any finding that does not survive a second look.

### Step 7: Write the verdict and emit the zone checklist

1. **Verdict** — one blunt paragraph: is the account healthier or worse than last quarter, and is the trajectory real or fragile? Name the single biggest threat for next quarter.
2. **Zone checklist** — pull the **matched zone's Execution Checklist only** from `zone-analysis.md` (never all five). This is the prescribed action set for the quarter ahead.

### Step 8: Approval gate

Present the verdict, zone, and top findings. Ask which findings to action this quarter before chaining into `keyword-optimizer`, `bid-budget-optimizer`, or `ad-copy-generator`.

## Output

**Filename:** `google_ads/YYYY-Qn/quarterly-review-YYYY-Qn.md` (e.g. `2026-Q2/quarterly-review-2026-Q2.md`)

**This report is a one-pager. One page maximum.** Lead with the verdict and the numbers. No preamble, no recap of methodology, no inspirational close. If it does not fit on one printed page, cut findings to the top 3 plus the disproven assumptions.

```
# Quarterly Adversarial Review: [Client Name]
Period: [last 90 days] vs [prior 90 days] | Date: [Today]

## Verdict: [Emoji] [Zone] — [Healthier / Worse / Fragile]
[2-3 blunt sentences: real trajectory or luck, and the single biggest threat next quarter.]

## 90-Day vs Prior 90-Day
| Metric | Prior 90 | Last 90 | Δ |
|--------|----------|---------|---|
| Cost | $X | $X | ±X% |
| Conversions | X | X | ±X% |
| CPA / ROAS | $X | $X | ±X% |
| Conv. Value | $X | $X | ±X% |

## Assumptions on Trial
[From Step 1. Each one: what we assumed last quarter → what the data now shows → verdict.]
1. [Assumption] → [data] → CONFIRMED / DISPROVEN ([$ impact])
2. ...

## What I'd Tear Apart (waste hunt)
1. [Finding] — [$ quantified] — [kill / fix / investigate]
2. ...
3. ...

## Lucky-Quarter Check
[1-2 lines: is the result explained by seasonality / one-off / tracking, or by the work?]

## [Zone] Execution Checklist
[Paste the matched zone's checklist from zone-analysis.md — only that one zone]
```

## HALT CONDITIONS

- **HALT if Step 1 cannot run** — if there is no active client folder and the user gives no client, ask which client to review and stop.
- **HALT if both data periods are empty or unreadable** — ask for the MCP access or the two CSV exports and stop.
- **HALT if zero findings.** A genuinely clean account is rare and suspicious. Before declaring it clean, re-run Steps 3 and 4, then show the three specific checks that *would* have caught a problem. A clean bill of health is a valid verdict only after that proof.

## Tips

- Run on a fixed 90-day cadence so the comparison windows never overlap
- Always pull the counter-metric — a single improving number is never the whole story
- Quantify waste in dollars; vague findings get ignored
- The assumptions pass is what makes this adversarial — last quarter's reasoning is the easiest thing to leave untested
- For a lighter monthly cadence, use `google-ads-monthly-review` instead

## Related Skills

- **Google Ads Monthly Review**: The lighter monthly cadence using the same AdPulse zones
- **Keyword Optimizer**: Execute the waste-hunt findings (pause keywords, add negatives)
- **Bid & Budget Optimizer**: Act on pacing and impression-share findings
- **Ad Copy Generator**: Refresh creative flagged as stale

---

*Every 90 days, attack the account and its assumptions before the client does*
