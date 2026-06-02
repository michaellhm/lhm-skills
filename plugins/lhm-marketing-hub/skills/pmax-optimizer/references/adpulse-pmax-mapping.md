# AdPulse Zone Mapping - PMax Campaign Level

The AdPulse zone framework lives canonically in `agents/google-ads-monthly-review.md`. That framework is account-level. This file applies the same logic at **campaign level** for a PMax campaign, with PMax-specific signals layered in.

## The Two-Axis Framework (Same as Account-Level)

| Budget Pacing | Performance | Zone | Priority |
|---------------|-------------|------|----------|
| > 110% (Over) | > 110% CPL or < 90% conv vs target (Poor) | 🔴 Red | CRITICAL - same-day action |
| 90–110% (On Pace) | > 110% CPL or < 90% conv vs target (Poor) | 🟠 Orange | High - 2–3 days |
| < 90% (Under) | ≤ 110% CPL or ≥ 90% conv (Good) | 🟡 Yellow | Medium - scaling opportunity |
| > 110% (Over) | ≤ 110% CPL or ≥ 90% conv (Good) | 🔵 Blue | Low - decision needed |
| 90–110% (On Pace) | ≤ 110% CPL or ≥ 90% conv (Good) | 🟢 Green | Maintain |

Zones match the AdPulse framework exactly so a reader can switch between account-level and campaign-level views without re-learning thresholds.

## PMax-Specific Modifiers

After computing the base zone, apply these modifiers. Each one nudges the zone up (worse) or down (better).

### Modifier 1 - Asset Quality

| Condition | Effect |
|-----------|--------|
| ≥ 30% of assets across the campaign rated LOW | Bump zone up one (Green → Yellow, Yellow → Orange, etc.) |
| All asset groups have at least one BEST asset across each type | Stay or bump down one |
| One or more asset groups Incomplete (missing logos / video) | Bump up one |

### Modifier 2 - Conversion Mix Stability

| Condition | Effect |
|-----------|--------|
| Single conversion-action type dropped > 25% MoM with no obvious cause | Bump up one |
| Conversion mix stable, ≥ 3 active conversion actions firing | No change |
| Only one conversion action firing | Bump up one (concentration risk) |

### Modifier 3 - Search Impression Share Lost (Budget)

| Condition | Effect |
|-----------|--------|
| > 30% Search IS lost to budget AND Yellow base zone | Push hard for budget increase; document zone as "Yellow - scale" |
| > 30% Search IS lost to rank AND any base zone | Bump up one (suggests bid / quality issue) |

### Modifier 4 - Final URL Expansion Health

| Condition | Effect |
|-----------|--------|
| Expansion ON, > 5% spend on non-target URLs | Bump up one |
| Expansion ON, < 2% spend on non-target URLs | No change (expansion working) |
| Expansion OFF | No modifier |

### Modifier 5 - Brand Spend Share

| Condition | Effect |
|-----------|--------|
| Brand spend > 35% of campaign | Bump up one (PMax is eating brand traffic) |
| Brand spend 15–35% | No change |
| Brand spend < 15% | No change |

## Worked Examples

### Example A - Healthy Mature Campaign

- Pacing: 95% (On Pace)
- CPL: $48 vs target $50 (= 96% of target - Good)
- Base zone: 🟢 Green
- LOW assets: 12% - no bump
- Conversion mix stable
- Search IS lost (rank): 18% - no bump
- Brand spend: 22% - no bump

→ Final zone: 🟢 Green - Maintain

### Example B - Scaling Opportunity

- Pacing: 78% (Under)
- CPL: $42 vs target $50 (= 84% of target - Good)
- Base zone: 🟡 Yellow
- LOW assets: 8%
- Search IS lost (budget): 38% - strong scale signal

→ Final zone: 🟡 Yellow - scale recommendation. Route to `bid-budget-optimizer`.

### Example C - Critical

- Pacing: 118% (Over)
- CPL: $76 vs target $50 (= 152% of target - Poor)
- Base zone: 🔴 Red
- LOW assets: 35% - bump up (already Red, stays Red but priority emphasis raised)
- Brand spend: 42% - additional bump

→ Final zone: 🔴 Red - CRITICAL. Action list: pause spend creep via `bid-budget-optimizer`, refresh creative via `pmax-banner-generator`, audit LP via `landing-page-optimizer`.

## What to Write in the Report

Always show:

1. The base zone with its two component values (pacing %, performance %).
2. Each modifier applied, with the condition that triggered it.
3. The final zone after modifiers.

Example block in the output report:

```
## Zone (PMax Campaign): 🟠 Orange - High

### Zone Calculation
- Budget pacing: 102% (On Pace)
- CPL vs target: 118% (Poor)
- Base zone: 🟠 Orange

### Modifiers Applied
- Asset quality: 28% LOW - no bump (threshold is 30%)
- Conversion mix: stable - no change
- Search IS lost (rank): 42% - bump up one → 🔴 Red

### Final Zone: 🔴 Red - CRITICAL

### Why
[1–2 sentences. The "why" is what the operator and the client read first.]
```

## Where the Zone Routes

| Final Zone | Default skill route |
|------------|---------------------|
| 🔴 Red | `bid-budget-optimizer` (pull-back) + `pmax-banner-generator` (creative refresh) + `landing-page-optimizer` (LP audit) |
| 🟠 Orange | `bid-budget-optimizer` (correction) + `pmax-banner-generator` (creative refresh on LOW assets) |
| 🟡 Yellow | `bid-budget-optimizer` (scale) - only if Search IS lost to budget is high |
| 🔵 Blue | Inline review of pacing only - usually a settings issue, no skill route needed |
| 🟢 Green | Maintain. Keep monthly cadence. |

The action list at the top of the optimisation report enforces these routes.
