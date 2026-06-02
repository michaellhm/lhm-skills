# GAQL Queries - PMax Optimizer

Every query this skill runs. Copy-paste ready for `mcp__GoogleAds__execute_gaql`. Replace `[CAMPAIGN_ID]` and date placeholders before running.

> Validate any query against `mcp__GoogleAds__get_gaql_doc` if you change it. The Google Ads Query Language schema does change between API versions.

## 1. Campaign-Level Performance (Last 30 Days)

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.advertising_channel_type,
  campaign.advertising_channel_sub_type,
  campaign.bidding_strategy_type,
  campaign.maximize_conversions.target_cpa_micros,
  campaign_budget.amount_micros,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion,
  metrics.search_budget_lost_impression_share,
  metrics.search_rank_lost_impression_share
FROM campaign
WHERE campaign.id = [CAMPAIGN_ID]
  AND segments.date DURING LAST_30_DAYS
```

## 2. Campaign-Level Performance (Last 90 Days, for 90-day review)

Same as above, change `LAST_30_DAYS` → `LAST_90_DAYS`.

## 3. Period-over-Period Comparison

Run query 1 twice, once with `LAST_30_DAYS`, once with a custom range for the prior 30 days, e.g.:

```sql
WHERE campaign.id = [CAMPAIGN_ID]
  AND segments.date BETWEEN '[YYYY-MM-DD start]' AND '[YYYY-MM-DD end]'
```

## 4. Asset Group Performance

```sql
SELECT
  asset_group.id,
  asset_group.name,
  asset_group.status,
  asset_group.final_urls,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion
FROM asset_group
WHERE asset_group.campaign = 'customers/[CID]/campaigns/[CAMPAIGN_ID]'
  AND segments.date DURING LAST_30_DAYS
```

## 5. Asset Performance Ratings (BEST / GOOD / LOW)

```sql
SELECT
  asset.id,
  asset.type,
  asset.name,
  asset.text_asset.text,
  asset_group_asset.field_type,
  asset_group_asset.performance_label,
  asset_group_asset.status,
  asset_group.id,
  asset_group.name
FROM asset_group_asset
WHERE asset_group.campaign = 'customers/[CID]/campaigns/[CAMPAIGN_ID]'
  AND asset_group_asset.status = 'ENABLED'
```

`asset_group_asset.performance_label` returns `BEST`, `GOOD`, `LOW`, `LEARNING`, `PENDING`, or `UNSPECIFIED`. Filter for `LOW` to find candidates to drop.

## 6. Conversion Action Breakdown

```sql
SELECT
  segments.conversion_action_name,
  segments.conversion_action_category,
  metrics.conversions,
  metrics.all_conversions,
  metrics.conversions_value
FROM campaign
WHERE campaign.id = [CAMPAIGN_ID]
  AND segments.date DURING LAST_30_DAYS
```

## 7. Geo Performance (User Location View)

```sql
SELECT
  geographic_view.country_criterion_id,
  geographic_view.location_type,
  segments.geo_target_city,
  segments.geo_target_region,
  metrics.cost_micros,
  metrics.conversions,
  metrics.cost_per_conversion
FROM geographic_view
WHERE campaign.id = [CAMPAIGN_ID]
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
LIMIT 200
```

## 8. Hour-of-Day / Day-of-Week Performance

```sql
SELECT
  segments.day_of_week,
  segments.hour,
  metrics.cost_micros,
  metrics.conversions,
  metrics.clicks
FROM campaign
WHERE campaign.id = [CAMPAIGN_ID]
  AND segments.date DURING LAST_30_DAYS
```

## 9. Search Impression Share Lost (already in query 1)

`metrics.search_budget_lost_impression_share` and `metrics.search_rank_lost_impression_share` from query 1. Watch both - the first means "raise budget", the second means "improve quality / bids".

## 10. Negative Keyword List Verification

```sql
SELECT
  shared_set.id,
  shared_set.name,
  shared_set.member_count,
  campaign_shared_set.status
FROM campaign_shared_set
WHERE campaign.id = [CAMPAIGN_ID]
```

Confirms the account-level negative list is still attached to this campaign.

## 11. Brand Exclusion List Verification

```sql
SELECT
  campaign.brand_guidelines_enabled,
  campaign_shared_set.shared_set,
  shared_set.name
FROM campaign_shared_set
WHERE campaign.id = [CAMPAIGN_ID]
  AND shared_set.type = 'BRANDS'
```

## 12. Final URL Expansion Landing Page Report

If expansion is ON:

```sql
SELECT
  landing_page_view.unexpanded_final_url,
  metrics.cost_micros,
  metrics.clicks,
  metrics.conversions,
  metrics.bounce_rate
FROM landing_page_view
WHERE campaign.id = [CAMPAIGN_ID]
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
LIMIT 100
```

## 13. Customer Acquisition Setting

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.customer_acquisition.optimization_mode,
  campaign.customer_acquisition.value_per_new_customer_micros
FROM campaign
WHERE campaign.id = [CAMPAIGN_ID]
```

## 14. Auction Insights (campaign-level absolute top IS - proxy for competitive pressure)

```sql
SELECT
  campaign.id,
  campaign.name,
  metrics.search_impression_share,
  metrics.search_top_impression_share,
  metrics.search_absolute_top_impression_share
FROM campaign
WHERE campaign.id = [CAMPAIGN_ID]
  AND segments.date DURING LAST_90_DAYS
```

## 15. Brand vs Non-Brand Search Term Split

PMax doesn't always expose full search terms. If the API returns them via `campaign_search_term_insight`:

```sql
SELECT
  campaign_search_term_insight.category_label,
  metrics.clicks,
  metrics.impressions,
  metrics.conversions,
  metrics.cost_micros
FROM campaign_search_term_insight
WHERE campaign_search_term_insight.campaign = 'customers/[CID]/campaigns/[CAMPAIGN_ID]'
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
```

Filter `category_label` containing the brand name vs not. If this query is unsupported on the account, fall back to the UI-exported Insights CSV.

## When the MCP Returns "Permission Denied"

Some MCC-level permissions block search-term and Insights data. If a query returns permission errors:

1. Note in the report which query failed.
2. Ask the user to export the Insights report from the Google Ads UI:
   `Campaign → Insights → Search categories → Download CSV`.
3. Save to `clients/<slug>/google_ads/YYYY-MM/insights-export-YYYY-MM.csv`.
4. Read the CSV manually for items 3, 9, 15.

## What NOT To Query

- Don't query asset-level click / impression metrics directly - Google does not attribute these reliably for PMax assets, only the BEST / GOOD / LOW label.
- Don't query audience-segment-level conversions for PMax - the data is partial. Use the audience-signal performance view in the UI for the full picture.
- Don't query keyword-level data for PMax - there are no keywords in PMax.
