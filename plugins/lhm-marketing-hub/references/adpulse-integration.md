---
title: AdPulse Integration
description: How to pull zone data (pacing/performance) directly from the AdPulse GraphQL MCP instead of hand-calculating it, and how to handle the zone matrix's known gap.
---

# AdPulse Integration

AdPulse MCP tools are prefixed `adpulse_graphql_*` (schema, schema_search, query, mutation). The exact server ID varies by session — search available tools for "adpulse" if the prefix isn't already visible.

**AdPulse does not expose a pre-computed Red/Orange/Yellow/Blue/Green zone field.** It exposes `pacing` (%) and `kpiPercentage` (%) on a budget's `entries`. Use AdPulse `pacing` for the matrix pacing axis instead of hand-calculating it. Use the canonical client CPA/ROAS target for the performance axis. Treat `kpiPercentage` as supporting trend evidence unless canonical context confirms that AdPulse is configured against that same business target.

## Finding a client's AdPulse budget

Each Google Ads account onboarded in AdPulse has a budget ID (format `bdg_...`). Look this up once per client and save it to `client_profile.md` under an "AdPulse Budget ID" field so future sessions don't need to re-resolve it.

```graphql
query FindBudget($adAccountIds: [AdAccountIdInput!]) {
  budgets__new(adAccountIds: $adAccountIds, limit: 20) {
    total
    nodes { __typename ... on BudgetCustomV2 { id name } }
  }
}
# variables: {"adAccountIds":[{"platform":"google","id":"<GOOGLE_ADS_CUSTOMER_ID>"}]}
```

If this returns nothing, the account isn't onboarded in AdPulse — say so explicitly rather than fabricating a zone. Fall back to the manual pacing/performance calculation in `skills/google-ads-monthly-review/SKILL.md` Step 3.

## Pulling pacing/performance

```graphql
query BudgetZoneData($id: ID!) {
  budget__new(budgetId: $id) {
    ... on BudgetCustomV2 {
      entries {
        current { interval{from to} target totalBudget spend progress pacing kpiPercentage }
        prev    { interval{from to} target totalBudget spend progress pacing kpiPercentage }
      }
      campaignBudgetGroup { kpi { __typename ... on CampaignBudgetGroupKpiCostPerConversionPreviousPeriod { currentCostPerConversion costPerConversionPreviousPeriod } } }
      history(days: 30) { date metrics { metrics { cost conversions costPerConversion } } }
    }
  }
}
# variables: {"id": "<ADPULSE_BUDGET_ID>"}
```

Also check `alertsSummary` for the budget — if AdPulse already has active alerts, factor them in; if a genuinely broken account shows zero alerts, note that as a monitoring gap worth mentioning to the client owner.

## Applying the zone matrix

Feed `current.pacing` and performance against the canonical client CPA/ROAS target into the matrix in `skills/google-ads-monthly-review/SKILL.md`. Show `current.kpiPercentage` separately as AdPulse trend/configuration context; never substitute a previous-period KPI for the business target.

**Known gap: the matrix has no defined cell for Under-pacing (<90%) + Poor performance.** This happens when a campaign isn't spending its full budget *because* it's converting so poorly that Target Spend/auction pressure can't find enough qualifying clicks/conversions — not because the client capped it. Do not default this combination to Yellow (the only "Under" cell that exists) — that would recommend scaling budget into a broken funnel. Treat it as Red-severity instead: performance problems override pacing when the two disagree. Say explicitly in the report that this was a matrix gap, not a real Yellow call, so the client owner understands why the checklist doesn't match a clean zone.

(2026-07-17) Confirmed via a live session against Your Story Physiotherapy: pacing 74.14%, kpiPercentage showing a 12x CPA blowout because real conversions had collapsed to ~0. Correctly treated as Red rather than Yellow.
