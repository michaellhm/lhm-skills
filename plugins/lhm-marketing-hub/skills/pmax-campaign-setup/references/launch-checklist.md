# Pre-Launch Checklist - Local-Business PMax

Twenty-five sign-off points. Walk every one before the campaign goes ENABLED. Skip none.

## A. Account & Access

- [ ] CID confirmed under MCC 394-736-1921 via `mcp__GoogleAds__list_accessible_accounts`
- [ ] Conversions linked across the MCC if cross-account tracking is in use
- [ ] Google Business Profile linked to the account (and to this campaign via location asset)
- [ ] No naming collision with an existing campaign - verify with:
```sql
SELECT campaign.id, campaign.name, campaign.status
FROM campaign
WHERE campaign.status != 'REMOVED'
ORDER BY campaign.name
```

## B. Conversion Tracking

- [ ] Primary conversion actions verified firing in last 30 days (see `conversion-tracking-checklist.md`)
- [ ] Counting type = One for every lead action
- [ ] Secondary actions assigned correctly (location actions, page views)
- [ ] No duplicate conversion actions for the same event

## C. Campaign Settings

- [ ] Objective = Leads (NOT Sales)
- [ ] Bid strategy = Maximise Conversions (no target on day 1) OR tCPA if account has historical PMax data
- [ ] Daily budget set per the formula in `local-business-config.md`
- [ ] Final URL expansion = OFF
- [ ] Customer acquisition setting reviewed (default: bid equally for new and existing)
- [ ] URL exclusions added (`/blog/*`, `/news/*`, `/jobs/*`, `/careers/*`)

## D. Geo & Schedule

- [ ] Location options = "Presence: People in or regularly in your targeted locations" (NEVER "Interest")
- [ ] Locations include the radius around the clinic + named suburbs
- [ ] Excluded suburbs added
- [ ] Languages set (English + any community languages with translated LPs)
- [ ] Ad schedule = 24/7 by default

## E. Asset Groups

- [ ] One asset group per service line, named `[Service] - [Stage] - [Theme]`
- [ ] Every group has the full slot count (15 headlines, 5 long, 5 descriptions, full image set, logos, videos)
- [ ] Every group's final URL is the matching service LP (not the homepage)
- [ ] AHPRA / industry-compliance check on all copy
- [ ] Each group's image set has the three required ratios (1.91:1, 1:1, 4:5)
- [ ] Each group has at least one logo (1:1) and one wide logo (4:1)
- [ ] Each group has at least one video (≥ 10 s) - auto-generated is acceptable but flag it

## F. Audience Signals

- [ ] Each asset group has at least one Custom Segment
- [ ] Customer Match assessed for AHPRA / Privacy Act eligibility (not added unless compliant)
- [ ] In-market segments added (1–2 per group)
- [ ] Detailed demographics added only where genuinely relevant

## G. Account-Level Assets

- [ ] Sitelinks (4–8) approved
- [ ] Callouts (4–6) approved
- [ ] Structured snippets approved (Header = "Services")
- [ ] Location asset linked
- [ ] Call asset added with tracked number (where call-tracking is in use)
- [ ] Lead form asset configured (if used)
- [ ] Promotion asset configured (only if a real promotion exists)

## H. Negatives & Brand Exclusions

- [ ] Account-level negative keyword list applied (existing or newly seeded)
- [ ] Brand exclusion list applied for branded competitor terms
- [ ] Verify negatives via:
```sql
SELECT shared_set.id, shared_set.name, shared_set.member_count, shared_set.type
FROM shared_set
WHERE shared_set.status = 'ENABLED'
```

## I. Final Sanity

- [ ] LP passes `landing-page-optimizer` scoring at ≥ 7/10
- [ ] LP loads in < 3 seconds on mobile
- [ ] LP has the same CTA wording as the BOF asset group's CTA
- [ ] Phone number on LP matches the call asset
- [ ] Spec file saved at `clients/<slug>/google_ads/YYYY-MM/pmax-setup-<campaign-slug>-YYYY-MM.md`

## J. Schedule the First Review

- [ ] First `pmax-optimizer` (monthly, light) scheduled at +14 days
- [ ] First `pmax-optimizer` (monthly, full) scheduled at +30 days
- [ ] First 90-day strategic review scheduled at +90 days

## Sign-Off

Spec author: ____________________
Reviewer (LHM): ____________________
Client approval (if required): ____________________
Launch date: ____________________

Once every box is ticked, the spec is ready to enter into Google Ads Editor / UI. Do not skip the manual review step - PMax is hard to roll back.
