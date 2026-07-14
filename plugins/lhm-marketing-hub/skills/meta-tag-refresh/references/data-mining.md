# Data Mining Recipes

All Google Ads queries run via the GoogleAds MCP (`execute_gaql`). Use the client's account ID and the agency MCC as `login_customer_id` (both usually in prior reports in `[client-folder]/google_ads/`). Date ranges: GAQL has no LAST_12_MONTHS — use explicit `BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`.

## 1. Discover conversion actions first

```sql
SELECT conversion_action.name, conversion_action.id, conversion_action.status
FROM conversion_action WHERE conversion_action.status = 'ENABLED'
```

Identify which actions are real outcomes (booking confirmed, form submit, phone call) vs soft proxies (booking page view, scroll). Prior monthly reviews in the client folder usually document which is which — read them. Segmenting by action is what stops a pageview-inflated conversions column from misleading the whole analysis.

## 2. Converting search terms, segmented

```sql
SELECT search_term_view.search_term, segments.conversion_action_name, metrics.all_conversions
FROM search_term_view
WHERE segments.date BETWEEN '...' AND '...'
  AND segments.conversion_action_name IN ('<real actions>', '<soft actions>')
  AND metrics.all_conversions > 0
ORDER BY metrics.all_conversions DESC LIMIT 80
```

## 3. Search term volume signal

```sql
SELECT search_term_view.search_term, metrics.clicks, metrics.impressions, metrics.cost_micros
FROM search_term_view WHERE segments.date BETWEEN '...' AND '...'
ORDER BY metrics.clicks DESC LIMIT 40
```

## 4. RSA copy angles

Asset texts by impressions (clicks are NOT available at asset level for RSAs — performance_label is usually PENDING at low volume, don't rely on it):

```sql
SELECT asset.text_asset.text, ad_group_ad_asset_view.field_type, ad_group_ad_asset_view.performance_label, metrics.impressions
FROM ad_group_ad_asset_view
WHERE ad_group_ad_asset_view.field_type IN ('DESCRIPTION','HEADLINE') AND segments.date BETWEEN '...' AND '...'
ORDER BY metrics.impressions DESC LIMIT 60
```

Ad-level CTR since the last copy refresh (the usable click signal):

```sql
SELECT ad_group.name, ad_group_ad.ad.id, metrics.clicks, metrics.impressions, metrics.ctr, metrics.conversions
FROM ad_group_ad
WHERE segments.date BETWEEN '<last refresh date>' AND '...'
  AND ad_group_ad.status = 'ENABLED' AND metrics.impressions > 100
ORDER BY metrics.ctr DESC LIMIT 25
```

Cross-reference the ad-level CTR winners with the RSA refresh report in the client folder to identify which angles those ads led with.

## 5. GSC pulls

- `get_search_analytics(site, days=180, dimensions="query")` and `dimensions="page"`.
- Decline analysis: `compare_search_periods` if available; otherwise two `get_search_analytics` windows (days=180 now, and the prior 180 via date-bounded query) and diff page-level clicks/impressions yourself. Then `get_search_by_page_query` on the top decliners for both windows to isolate which queries fell.
- Classify dropped queries by intent before prioritising. Commercial markers: clinic/provider nouns, treatment/service terms, cost/price, near me, book, suburb+service. Informational markers: what/why/how, symptoms, causes, at home.
- Watch for UTM-tagged homepage URLs (GMB listing links) in page data — they're not separate pages, aggregate them mentally with the homepage and note that redirects must preserve query strings at launch.

## 6. Keywords Everywhere

`get_keyword_data` with the client's country code and currency. Batch all candidates in one call (~35 keywords). Remember the calibration rule: zero-volume in KE for suburb/local terms means nothing when GSC impressions and Ads conversions prove demand. Note 12-month trends — a term climbing month over month deserves priority beyond its average volume.
