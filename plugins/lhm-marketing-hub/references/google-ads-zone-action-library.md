---
title: Google Ads Zone Action Library
description: AdPulse-derived candidate actions, skill routes and selection rules for monthly reviews.
---

# Google Ads Zone Action Library

Use this library during a monthly review after determining the account-level performance zone and
measurement confidence. The zone supplies candidates; live evidence, client economics, prior
commitments and campaign-level exceptions determine the final actions.

## Selection rules

1. Start with the matched zone's `highest_impact` candidates.
2. Add `go_deeper` candidates only when observed evidence supports them.
3. A materially failing campaign may use Red or Orange repair candidates even when the mechanical
   account-level zone is Yellow, Blue or Green. Preserve the account-level zone and label the
   campaign exception; never relabel the whole account to justify the action.
4. Reconcile prior commitments before creating new actions. Continue a partial or unverified
   commitment under its existing history rather than presenting it as a fresh discovery.
5. Select no more than five actions. Every action must cite account-specific evidence, expected
   outcome, owning skill, dependencies, authority class and verification method.
6. Do not select a checklist item merely because it appears in the matched zone. Omit unsupported,
   irrelevant or lower-value candidates.

## Candidate-to-skill routes

| Candidate | Owning skill | Default authority |
|---|---|---|
| Reduce, increase or reallocate budget | `bid-budget-optimizer` | consequential when total budget or material allocation changes |
| Adjust bids, CPC ceilings or bid modifiers | `bid-budget-optimizer` | Lead for bounded reversible tuning; consequential for strategy changes |
| Change or experiment with bid strategy | `bid-budget-optimizer` | consequential |
| Audit search terms, waste, blocked terms or paused keywords | `keyword-optimizer` | Lead |
| Add converting queries or upgrade match types | `keyword-optimizer` | Lead |
| Expand strong campaigns or create keyword/ad-group structure | `keyword-optimizer` then `ad-copy-generator` where creative is required | Lead unless material targeting or spend changes |
| Check or improve ads and assets | `ad-copy-generator` | Lead for substantiated compliant copy; consequential for subjective brand claims |
| Check primary conversion actions, campaign goals, GA4 firing and imports | `google-ads-conversion-audit` | Lead for diagnosis; consequential for conversion-definition changes |
| Check 404s or landing-page performance | `landing-page-optimizer` | Lead for diagnosis/preparation; route implementation through Production |
| Diagnose PMax performance or expansion | `pmax-optimizer` | Lead for analysis; owning downstream gates still apply |
| Diagnose device, location, audience or demographic anomalies | `bid-budget-optimizer` | Lead for diagnosis and bounded reversible tuning; consequential for major targeting exclusions |
| Evaluate search partners or new networks/campaign types | `paid-ads` | consequential before launch or material scope expansion |

## Zone candidates

### Red — reduce spend, then repair performance

`highest_impact`: reduce budget toward controlled pacing; reallocate toward proven campaigns; find
weak CPA/ROAS drivers; ensure budgets last the day; reduce excessive bids; audit waste; verify
primary conversions.

`go_deeper`: device/location/audience/demographic anomalies; bid-strategy experiment; search
partners; approvals and assets; geo tightness; landing-page failures; expansion of proven winners;
match-type improvement; converting-query promotion; paused/blocked-term recovery.

### Orange — repair performance, then increase spend

`highest_impact`: reallocate toward proven campaigns; find weak CPA/ROAS drivers; inspect anomaly
segments; ensure budgets last the day; audit keyword/search-term waste; assess bid strategy; recover
valuable paused or blocked traffic; verify primary conversions.

`go_deeper`: search partners; approvals and assets; geo tightness; landing-page failures; controlled
winner expansion; match-type improvement; campaign duplication experiments.

### Yellow — increase profitable spend

`highest_impact`: remove avoidable budget limits from proven campaigns; recover valuable blocked
traffic; raise bids or relax smart-bidding targets where economics support it; expand proven
campaigns; improve match types and coverage.

`go_deeper`: new campaign types or networks; remarketing; asset coverage; campaign duplication
experiments; landing-page failures; positive anomaly modifiers. These require specific evidence and
the owning approval gate; Yellow is not blanket authority to spend more.

### Blue — slow spend while protecting strong performance

`highest_impact`: prepare the commercial case for more budget; otherwise reduce bids, exclude the
worst observed segments, reduce budget, then pause the worst campaigns as a last resort.

### Green — maintain and learn

`highest_impact`: preserve working settings; make small evidence-backed improvements; monitor
competitors and anomalies; run one bounded experiment; document the reusable success pattern.
