---
name: google-ads-conversion-audit
description: Audit Google Ads conversion actions, account-default and campaign-specific goals, GA4 event firing, and GA4-to-Ads imports. Use during every Google Ads monthly review and whenever conversion counts, call tracking, primary/secondary status, campaign optimisation goals, attribution, or imports are unclear. Produce a one-page current-to-recommended conversion matrix and exact implementation steps.
---

# Google Ads Conversion Audit

## Outcome

Produce a one-page measurement decision sheet. Diagnose first; do not change conversion definitions
or campaign goals without the authority defined by the Google Ads Lead.

## Evidence sequence

1. Load canonical business outcomes and prior conversion decisions from the supplied client context.
2. Read all enabled and recently used Google Ads conversion actions. Record source, category, status,
   primary/secondary state, account-default inclusion, attribution setting and recent activity.
3. Read every active campaign's goal configuration. State whether it uses account-default or
   campaign-specific goals and list the actions bidding can optimise towards.
4. Identify duplicates, soft actions counted as leads, missing business outcomes, zero-firing actions
   and Ads-hosted/GA4 pairs that may count the same outcome.
5. When firing or import state is unclear, use the Google Analytics connector for the same date
   windows. Check the canonical event name, event/conversion counts, Google Ads link, and whether the
   event exists in GA4 but is missing or inactive in Ads. Do not ask the client to test first when the
   connector can answer it.
6. Separate these diagnoses: site event not firing; GA4 event firing but not imported; imported but
   not included in the campaign goal; included but not attributed; insufficient evidence.

## Decision rules

- Primary means a real business outcome used for bidding. Soft funnel signals are secondary unless
  the canonical strategy explicitly says otherwise.
- Do not recommend deleting or demoting an Ads-hosted conversion when the platform does not permit
  it. Exclude it through account-default or campaign-specific goal settings and state the exact path.
- Do not count both an Ads-hosted and GA4 version of the same outcome as primary without a documented
  deduplication reason.
- Treat conversion-definition changes as consequential. Diagnosis and implementation preparation
  remain Lead-authorised read-only or prepare-only work.
- Never infer that zero Ads conversions means zero leads until GA4 and import evidence are checked.

## Required one-page output

Save as `google_ads/YYYY-MM/conversion-tracking-YYYY-MM.md`.

When invoked by `google-ads-monthly-review`, return the same one-page content to the monthly Lead for
embedding under `Conversion Tracking Findings` in the consolidated monthly review. In that mode, do
not save a separate conversion file. Standalone conversion audits retain the filename above.

```markdown
# Conversion Tracking: [Client] | [YYYY-MM]

Measurement confidence: [High/Medium/Low] | [one-line reason]

| Conversion | Source | Fires? | Current role | Recommended role | Account default | Campaign usage | Required action |
|---|---|---:|---|---|---|---|---|
| [name] | Ads/GA4 | Yes/No/Unknown | Primary/Secondary | Primary/Secondary/Exclude | Yes/No | [campaigns] | [exact action or Keep] |

## GA4 and import checks
| GA4 event | Same-window activity | Ads import | Ads link | Finding |
|---|---:|---|---|---|

## Changes required
| Object | Current | Change to | Exact location | Authority | Verification |
|---|---|---|---|---|---|

## Blockers
- [Missing capability or evidence, or None]
```

Keep the file to one printed page. Put detailed queries or screenshots in specialist findings, not
in this one-pager.

## Handback

Return the observed evidence, one-page artefact, exact proposed changes, authority class, mutations
performed (`none` unless explicitly authorised), and verification method to the Google Ads Lead and
Google Ads Delivery QA.
