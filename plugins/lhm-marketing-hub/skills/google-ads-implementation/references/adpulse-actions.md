---
title: AdPulse actions cookbook
description: Working AdPulse GraphQL calls for applying Google Ads changes, sweeping Insights/Optimize, ignoring recommendations and checking run status. Verified against a live account on 2026-09-24.
---

# AdPulse actions cookbook

Tools: `adpulse_graphql_schema_search`, `adpulse_graphql_query`, `adpulse_graphql_mutation`. The server prefix varies by session; search for "adpulse".

The schema is very large. `adpulse_graphql_schema_search` results often overflow into a saved file, so grep that file for `^input <Type>` or `^type <Type>` rather than reading it whole.

## Account ID

The Google account ID is the plain Google Ads customer ID (digits, no dashes): `googleAdAccountId: "5308308105"`, or `adAccountIds: [{platform: google, id: "5308308105"}]`.

## Apply changes

All Google mutations go through one call:

```graphql
mutation Q($a: [ActionGoogleInput!]!) {
  actionsQueueGoogle(googleAdAccountId: "<CUSTOMER_ID>", actions: $a)
}
```

It returns a run ID. `ActionGoogleInput` is `@oneOf`: each list item has exactly one key.

Verified action shapes:

```json
{"negativeKeywordListKeywordRemove": {"negativeKeywordListId": "<shared_set.id>", "negativeKeywordId": "<shared_criterion.criterion_id>"}}
{"campaignNegativeKeywordRemove": {"campaignId": "<id>", "keywordId": "<campaign_criterion.criterion_id>"}}
{"adGroupKeyword": {"campaignId": "<id>", "adGroupId": "<id>", "keyword": "physio eastwood", "matchType": "exact"}}
{"adFinalUrl": {"campaignId": "<id>", "adGroupId": "<id>", "adId": "<id>", "url": "https://..."}}
{"adGroupUnpause": {"campaignId": "<id>", "adGroupId": "<id>"}}
{"adGroupPause": {"campaignId": "<id>", "adGroupId": "<id>"}}
{"campaignBiddingStrategy": {"campaignId": "<id>", "strategy": {"targetSpend": {"cpcBidCeiling": 6}}}}
```

- `targetSpend` is Maximize Clicks. `cpcBidCeiling` is in account currency, not micros.
- **BigDecimal fields must be JSON numbers** (`6`), never strings (`"6.00"`). Strings fail validation.
- Match type enums are lowercase: `exact`, `phrase`, `broad`.
- Get the IDs first with GAQL (`shared_criterion`, `campaign_criterion`, `ad_group`, `ad_group_ad`).

Other available keys include `adGroupKeywordPause`/`Unpause`/`Remove`, `adPause`/`adUnpause`, `adCreate`, `campaignBudgetDailyAmount`, `campaignNegativeKeyword`, `negativeKeywordListKeyword`, `campaignLocationTarget`/`Exclude`, `campaignPause`/`Unpause` and `adGroupAudienceAdd`. Before using a new one, check its input type (`grep -A8 "^input ActionGoogle<Name>Input"`).

**Not available in AdPulse (use Chrome):** PMax asset group audience signals and search themes, the account call conversion setting, and conversion action primary/secondary.

## Check a run

```graphql
{ actionRunInfo(id: "<RUN_ID>") { status { __typename
  ... on ActionRunStatusRan { completed errors { __typename } }
  ... on ActionRunStatusFailed { completed } } } }
```

Runs usually finish within a minute. `ActionRunStatusRan` with `errors: []` means AdPulse submitted the change. Still verify in Google Ads with GAQL.

## Sweep: Insights and Optimize

Counts by category:

```graphql
{ insightsCountByCategory(adAccountIds: [{platform: google, id: "<ID>"}]) { categories { category count passed } } }
```

Insights list. `insights` returns only the union members you give a fragment for. Alias any `total` fields, because their types clash between members:

```graphql
{ insights(adAccountIds: [{platform: google, id: "<ID>"}], limit: 50) { total nodes { __typename
  ... on InsightInterface { type subType category timestamp }
  ... on InsightSearchTermsSingleWord { swTotal: total }
  ... on InsightSmartBiddingCampaignRemove { sbTotal: total }
  ... on InsightSearchTermsBlockedConverters { bcTotal: total
      days360 { clicks cost conversions }
      searchTerms { campaign { name } searchTerm { value days30 { clicks cost conversions } days360 { clicks cost conversions } } } } } } }
```

Run the bare `__typename` + `InsightInterface` version first to see which types exist, then add fragments for those. Look up the fields with `grep -A20 "^type Insight<Name> "`.

Optimize tab (`performanceHighlights`), ranked by score:

```graphql
{ performanceHighlights(adAccountIds: [{platform: google, id: "<ID>"}], limit: 20) { __typename
  ... on PerformanceHighlightNGramAddNegativeKeyword { score ngrams { ngram score campaign { ... on CampaignGoogle { name } } } }
  ... on PerformanceHighlightSearchTermAddNegativeKeyword { score searchTerms { searchTerm score campaign { ... on CampaignGoogle { name } } } }
  ... on PerformanceHighlightSearchTermAddKeyword { score searchTerms { searchTerm score campaign { ... on CampaignGoogle { name } } } }
  ... on PerformanceHighlightKeywordPause { score keywords { id keyword matchType score
        campaign { ... on CampaignGoogle { name } } adGroup { ... on AdGroupGoogle { name } } } } } }
```

Other highlight variants cover pausing or re-bidding campaigns, ad groups and asset groups, audience/demographic/device bid adjustments, and publisher exclusions. Query `__typename` first and add fragments as needed.

## Ignore recommendations

These go through `actionsQueueGoogle` too:

```json
{"searchTermIgnore": {"campaignId": "<id>", "searchTerm": "north ryde physio"}}
{"searchTermIgnore": {"campaignId": "<id>", "searchTerm": "near me"}}
{"adGroupKeywordIgnore": {"campaignId": "<id>", "adGroupId": "<id>", "keywordId": "<id>", "until": "2026-10-01T00:00:00Z"}}
{"adGroupIgnore": {"campaignId": "<id>", "adGroupId": "<id>", "until": "..."}}
{"campaignIgnore": {"campaignId": "<id>", "until": "..."}}
```

- Leave out `until` to ignore permanently. Set it to hold an item until a review date.
- `searchTermIgnore` also clears n-gram suggestions: pass the n-gram as the `searchTerm`.
- N-gram suggestions regenerate. After ignoring one batch, AdPulse offers the next set of n-grams. On a low-conversion campaign, stop after one round and record the recommendation as noise rather than ignoring every n-gram.
- Once the underlying change has been applied, the item drops off on its own (for example the smart-bidding flag after a bidding change).
