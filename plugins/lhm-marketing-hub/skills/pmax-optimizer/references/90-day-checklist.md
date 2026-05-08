# 90-Day Strategic PMax Review (Local Business)

Run every quarter. Includes everything from `monthly-checklist.md` **plus** the strategic items below. The 90-day review is the moment to make structural decisions Google's algorithm can't make for you.

Run the monthly checklist first, then the strategic layer. Total: 30 items (15 monthly + 15 strategic, items 16-30). Cadence is non-negotiable for any campaign over $2K/mo.

## Items 1–15 - Monthly checklist
Run every monthly item. See `monthly-checklist.md`.

## 16. Asset Group Restructure Decision

Compare asset-group performance across the 90 days. For each group:
- Conversions / day
- CPL
- Spend share
- Asset coverage and quality

Decisions:
- **Merge** two groups if one has < 5% spend share for two consecutive months and similar service intent.
- **Split** a group if it accounts for > 60% of spend AND has heterogeneous service intent (e.g. "general physio" really has knee, back, and shoulder treatment threads under it).
- **Rename** if the current name no longer reflects the actual creative bundle.
- **Pause** if zero conversions in 90 days.

## 17. Audience Signal Experiment Review

Look at the 90-day signal performance. For each signal:
- Did Custom Segments outperform In-Market on conversions?
- Did Customer Match (if used) materially lower CPL on its matched-user share?
- Are any signals unused / never expanded into?

Action: Retire dead signals, expand on the winners. Refresh Custom Segments using the past-quarter top converting search terms.

## 18. Bid Strategy Review

Decision tree:
- Currently Maximise Conversions, ≥ 50 conversions / 30 days, CPL stable or improving → switch to **tCPA = current avg CPL × 0.95** (gentle squeeze).
- Currently tCPA, hitting target ≥ 80% of days → consider tightening tCPA by 5–10%.
- Currently tCPA, missing target ≥ 50% of days → loosen tCPA by 10% OR drop back to Maximise Conversions for re-learning.
- Considering Max Conv Value with tROAS → only if conversion values are reliable, ≥ 50 weighted conversions / month, AND there's a real lead-value model. Otherwise stay on conversion-count strategies.

## 19. Conversion Goal Weighting Re-Validation

Re-examine the goal weights set in `pmax-campaign-setup`.

- Are calls converting to actual booked patients at the rate assumed?
- Are forms still primary, or has the channel shifted?
- Should location actions be weighted up if walk-ins are now a measurable revenue source?

Action: Update weights in the account-level conversion goals. Document the change.

## 20. Geo Targeting Strategy

Build a 90-day conversion-density map by suburb.

- Suburbs with ≥ 5 conversions and CPL ≤ target → consider a targeted asset group with a suburb-themed LP.
- Suburbs with 0 conversions and > 1× target spend → exclude.
- Suburbs at the radius edge with strong performance → consider expanding the radius by 5 km.

## 21. Brand Exclusions Refresh

- Pull current brand exclusion list.
- Run a competitive scan: any new clinic in the same suburb? Any rebrands?
- Add new branded competitor terms to the exclusion list.

## 22. Demographic Exclusions Review

For applicable services, review demographic performance.

- Are conversions concentrated in a specific age band? Shift signals to favour it.
- Are some bands consistently zero-converting at material spend? Apply demographic exclusions where compliant.
- **Never** apply exclusions that breach Google's personalised-ads policy or anti-discrimination rules. Health-condition demographics are off-limits.

## 23. Account Structure Review

Decision: should this account run **one** PMax or **multiple** PMax campaigns?

Move to multiple PMax campaigns when:
- Service lines have CPL targets varying > 1.5×.
- One service line consistently exceeds 60% of spend.
- Total spend ≥ $5,000 / month and asset groups are stable.

Document the recommendation and route to `bid-budget-optimizer` for the budget reallocation step.

## 24. Search Lift / Brand vs Non-Brand Trend

Plot 90-day brand spend % and brand-search volume.

- Is non-brand search interest rising (good - brand awareness is working)?
- Is brand spend in PMax climbing (bad - PMax is eating brand traffic that should be cheaper)?

If brand-eating is visible: recommend a separate brand Search campaign (outside this skill).

## 25. LSA Interaction (if Local Service Ads are running)

If the client also runs Local Service Ads (LSA):

- Compare lead-to-conversion rates between LSA and PMax.
- Look for cannibalisation in shared geo + service.
- Consider time-of-day separation (LSA for business hours, PMax 24/7).

## 26. Competitor Benchmark via Auction Insights

Pull the 90-day Auction Insights GAQL data:

```sql
SELECT
  campaign.id,
  campaign.name,
  metrics.search_impression_share,
  metrics.search_top_impression_share,
  metrics.search_absolute_top_impression_share
FROM campaign
WHERE segments.date DURING LAST_90_DAYS
  AND campaign.id = [campaign_id]
```

PMax doesn't expose competitor-level Auction Insights the way Search does, but the campaign-level absolute-top-impression-share trend tells the story.

## 27. CPL Trend (90-Day Plot)

Plot weekly CPL over the 90 days.

- Trend down → working.
- Trend flat at target → maintain.
- Trend up → diagnose: is it audience saturation? LP fatigue? Algorithm regression after a setting change?

## 28. New Audience-Signal Hypotheses for Next Quarter

Generate 3–5 new Custom Segment ideas for the upcoming quarter, based on:

- Past-quarter top converting search terms.
- New competitor URLs that have appeared in SERPs.
- New service launches at the clinic.

Document them in the report as "to deploy at the next monthly".

## 29. Quarterly Client Update Email

Draft a plain-English summary of the 90-day window and route to `client-update-email` for delivery.

## 30. Schedule the Next 90-Day Review

Add the next 90-day review date to the report and the client folder. Default: today + 90 days.

## Output

Save to: `clients/<slug>/google_ads/YYYY-MM/pmax-optimisation-90day-YYYY-MM.md`

Structure: action list at the top, monthly walk-through next, strategic items 16–30 last. The strategic recommendations often need client sign-off - flag explicitly which ones do.
