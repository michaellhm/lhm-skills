# Monthly PMax Optimisation Checklist (Local Business)

Run every 30 days. Walk every item. Each item produces a status, evidence number, recommended action, owner, and routing.

Status legend:
- ✅ healthy - no action
- ⚠️ watch - monitor next month
- 🔴 act - recommended action goes into the top-of-report action list

## 1. Asset Performance Review

Pull asset performance ratings per asset group. Any asset rated **LOW** for ≥ 14 days is a candidate to drop.

- Status: 🔴 if any group has ≥ 3 LOW assets in headlines, descriptions, or images.
- Evidence: Group name + asset type + count of LOW.
- Action: Drop the LOW assets, brief replacements via `pmax-banner-generator`.
- Routing: `pmax-banner-generator`

## 2. Asset Coverage

Confirm every asset group has the full slot count: 15 headlines, 5 long headlines, 5 descriptions, full image set (1.91:1, 1:1, 4:5), at least one logo of each ratio, at least one video.

- Status: 🔴 if any slot below max.
- Action: Brief the gap via `pmax-banner-generator`.

## 3. Search-Terms / Insights Review

Pull the Insights report (or use the user-supplied CSV if MCP can't access it). Identify search terms that drove spend with zero conversions, plus any obvious irrelevant queries.

- Evidence: Top 10 zero-converting search terms by spend.
- Action: Add as negative keywords to the account-level negative list. List the additions in the action row.

## 4. Audience Signal Performance

Pull audience-signal performance per asset group. Identify signals with CTR materially below the group average and zero contribution to conversions.

- Action: Pause the underperformer and replace with a higher-intent Custom Segment.
- Routing: Inline action (don't route to another skill - small change).

## 5. Conversion Volume vs Target

Compare last-30 conversions against target (target = monthly budget ÷ target CPL).

- Status: 🔴 if conversions < 80% of target.
- Status: ⚠️ if 80–95%.
- Action: If 🔴, walk the rest of the checklist looking for the cause; the fix is rarely "raise the budget".

## 6. Conversion Mix

Break conversions down by action type (form / call / location / lead form). Compare against last month.

- Status: 🔴 if any single action type dropped > 25% MoM with no obvious cause.
- Action: Investigate tracking. Calls dropping is often a forwarding-number issue. Forms dropping is often a website / form-plugin update.

## 7. Budget Pacing

Compare daily spend against budget. Calculate pacing %.

- Status: 🔴 if pacing > 110% AND CPL > 110% of target (over-spending under-performing).
- Status: 🔴 if pacing < 80% AND CPL ≤ target (algorithm starved - Google can't find conversions cheaply enough at this budget).
- Action: Route to `bid-budget-optimizer`.
- Routing: `bid-budget-optimizer`

## 8. Final URL Expansion

If expansion is ON, pull the landing-page report.

- Status: 🔴 if any non-target page accounts for > 5% of spend.
- Action: Add to URL exclusions, OR turn expansion OFF if the leak is widespread.

## 9. Brand vs Non-Brand Spend

Filter the search-terms / Insights report by branded keywords (client name + variations).

- Status: ⚠️ if brand spend > 35% of total.
- Action: Consider adding a brand-only Search campaign to suck brand spend out of PMax (cheaper clicks, better attribution). Document in the action list - implementation is outside this skill.

## 10. Geo Performance

Break the geo report down by sub-location.

- Status: 🔴 for any sub-location with > 1× tCPA in spend AND zero conversions.
- Action: Add to location exclusions.

## 11. Ad Schedule Signal

Look at conversion-by-hour and conversion-by-day patterns.

- Note any obvious clusters (e.g. 90% of calls happen 9am–5pm).
- Action: Do **not** restrict the schedule yet - PMax handles this. Document the pattern for the 90-day review.

## 12. Landing Page Experience Flags

Check Google Ads' LP-experience indicator (where surfaced) and bounce-rate / engagement metrics from GA4 if linked.

- Status: 🔴 if LP-experience is "Below average" OR if GA4 bounce > 70% on landing.
- Routing: `landing-page-optimizer`

## 13. Negative Keyword List

Confirm the account-level negative keyword list is still applied to this campaign.

- Status: 🔴 if missing (sometimes detaches after a campaign edit).
- Action: Re-attach. Fast fix, no skill route.

## 14. AHPRA / Industry Compliance Spot-Check

Pull a sample of currently-serving headlines, descriptions, and asset IDs. Run the banned-language list against them.

- Status: 🔴 if any breach found. Pause the offending asset immediately.
- Routing: `pmax-banner-generator` for replacement copy.

## 15. Action List Output

Compile the prioritised action list at the top of the report.

- Order: Red items first (by spend impact), then Orange/Yellow.
- Cap at 7 actions. If more than 7 are red, the campaign needs a 90-day strategic review, not just a monthly.

## Output

Save to: `clients/<slug>/google_ads/YYYY-MM/pmax-optimisation-monthly-YYYY-MM.md`

The structure is in the parent SKILL.md. The 15-item walk-through goes under the headline numbers, with the action list at the top.
