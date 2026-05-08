# Conversion Tracking Checklist (Pre-Launch)

PMax dies without correct conversion tracking. Every action below is a hard prerequisite. Refuse to launch the campaign until each one is verified.

## Required Conversion Actions

For a local-service-business PMax, the conversion actions matrix looks like this:

| Conversion Action | Type | Counting | Primary / Secondary | Default Value |
|-------------------|------|----------|---------------------|---------------|
| Form submit (booking form) | Website | One | Primary | $0 (or estimated lead value) |
| Form submit (general enquiry) | Website | One | Primary | $0 (or estimated lead value) |
| Phone call from ads (≥ 30s) | Call | One | Primary | $0 (or estimated lead value) |
| Phone call from website call asset (≥ 30s) | Call | One | Primary | $0 |
| Location action - directions | Local | One | Secondary | $0 |
| Location action - call from Maps | Local | One | Secondary | $0 |
| Lead form asset submit | Website | One | Primary (if used) | $0 |
| Contact-page view | Website | One | Secondary | $0 |

Notes:
- Primary actions count toward bid optimisation. Secondary actions are for reporting only.
- Set value where lead-value modelling is reliable; otherwise leave at $0 and use Maximise Conversions, not Max Conv Value.
- Never mark a soft action like "page view" as Primary - it inflates conversion counts and breaks Smart Bidding.

## Verification GAQL Queries

Run each via `mcp__GoogleAds__execute_gaql`. Replace `<CID>` in the customer call.

### List all conversion actions on the account
```sql
SELECT
  conversion_action.id,
  conversion_action.name,
  conversion_action.type,
  conversion_action.status,
  conversion_action.primary_for_goal,
  conversion_action.counting_type,
  conversion_action.value_settings.default_value,
  conversion_action.category
FROM conversion_action
WHERE conversion_action.status = 'ENABLED'
ORDER BY conversion_action.name
```

### Recent conversions per action (sanity check it's firing)
```sql
SELECT
  segments.conversion_action_name,
  metrics.all_conversions,
  metrics.conversions
FROM customer
WHERE segments.date DURING LAST_30_DAYS
```

### Confirm the campaign uses the right Goals page
```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.advertising_channel_type,
  campaign.advertising_channel_sub_type,
  campaign.bidding_strategy_type,
  campaign.maximize_conversions.target_cpa_micros
FROM campaign
WHERE campaign.name = '[Campaign Name]'
```

## Pre-Launch Sign-Off

The operator must tick each item before the campaign is set to ENABLED:

- [ ] Form-submit tag firing on every booking form (test in incognito, then check Tag Assistant or GA4 DebugView)
- [ ] Phone-call conversion firing for calls ≥ 30 seconds
- [ ] Location asset linked to the correct Google Business Profile
- [ ] Each Primary conversion has fired ≥ 1 time in the last 30 days (proves it's plumbed)
- [ ] Each conversion action's counting type is correct (One for leads, never Every)
- [ ] Each Primary conversion is assigned to the Default account-level goal OR a custom goal scoped to this campaign
- [ ] Imported GA4 events (where used) are mapped to the right account-level conversion goal
- [ ] No duplicate conversion actions firing for the same event (common after a CMS change)
- [ ] Cross-account conversion tracking enabled if the account is under MCC 394-736-1921 with shared conversions
- [ ] AHPRA / industry-compliance copy review on every conversion action's display name (these can leak into reports)

## What "Verified" Looks Like

Verified = the GAQL query returned the action AND the metrics.conversions count > 0 in the last 30 days.

If a Primary conversion has zero recent conversions, do not launch. Either fix the tracking or use a different action as Primary. PMax launched against a non-firing conversion action will spend without learning.

## Common Failure Modes

- **GA4 import is delayed.** GA4-imported conversions take 24–48 hours to surface in Google Ads. Don't launch in that window assuming they'll work.
- **Two form-submit conversions firing.** Often a Tag Manager + WordPress plugin double-up. Pause one before launch.
- **Call conversions counting < 30s calls.** Accidentally configured as 0s minimum. Fix to 30s.
- **Maps location actions counted but the GBP isn't linked.** Re-link via the Locations menu in Google Ads, then confirm a 24-hour data lag passes.
- **Primary goals at account level conflict with primary goals at campaign level.** Pick one scope and stick to it.
