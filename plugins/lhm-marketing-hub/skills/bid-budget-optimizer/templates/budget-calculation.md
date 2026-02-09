# Budget Calculation Reference

Formulas and decision matrices for bid and budget recommendations.

---

## Core Formulas

### Budget Pacing

```
Budget Pacing % = (Actual Spend to Date / Expected Spend to Date) x 100
Expected Spend to Date = (Monthly Budget / Days in Month) x Days Elapsed
```

### Ideal Daily Spend

```
Remaining Budget = Monthly Budget - Actual Spend to Date
Ideal Daily Spend = Remaining Budget / Days Remaining
```

### Period-over-Period Change

```
Change % = ((Current - Previous) / Previous) x 100

If positive: "Up X%"
If negative: "Down X%"
If within +/-2%: "Flat"
```

---

## Bid Strategy Decision Matrix

| Current Strategy | Signal | Recommendation |
|-----------------|--------|----------------|
| Max Clicks | High CPA, decent clicks | Switch to Max Conversions with target CPA |
| Max Clicks | Low volume, high CPA | Switch to Max Conversions with target CPA, increase budget |
| Max Clicks | Good CPA | Switch to Max Conversions (no cap) to scale |
| Max Conversions | CPA volatile/high | Add target CPA cap at 1.2x your goal |
| Max Conversions | CPA stable, good | Keep — or test Target ROAS if tracking value |
| Target CPA | Not spending budget | Raise target CPA by 10-15% |
| Target CPA | CPA higher than target | Lower target CPA by 10% (gradual) |
| Target CPA | On target | Keep |
| Target ROAS | Not spending | Lower ROAS target by 10-15% |
| Target ROAS | ROAS above target | Keep or tighten target slightly |
| Manual CPC | Consistent results | Consider automation if volume supports it |
| Manual CPC | Low volume | Keep manual until data justifies automation |

---

## Budget Change Guidelines

### Increases
- Max 20% daily increase for Max Clicks / Max Conversions / Max Conversion Value
- Target CPA and Target ROAS: no hard limit (self-regulating)
- Manual CPC: no limit

### Decreases
- Any reduction over 30%: recommend gradual over 2-3 days
- Over 60%: consider pausing instead
- Always protect best-performing campaigns from cuts

### When to Pause
- CPA >2.5x target with no improvement trend
- Zero conversions over 14+ days with meaningful spend
- Campaign has been outperformed by a replacement

---

*Reference: AdPulse Quadrant Budget Optimization*
