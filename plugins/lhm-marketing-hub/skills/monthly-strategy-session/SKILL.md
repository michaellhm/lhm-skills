---
name: monthly-strategy-session
description: Start-of-month orchestrator that analyses Google Ads account performance, identifies AdPulse zone (Red/Orange/Yellow/Blue/Green), and recommends 3-5 priority actions. Use this when users request monthly strategy review, account health check, zone analysis, PPC planning, or start-of-month analysis for healthcare clients.
license: MIT
---

# Monthly Strategy Session

## Purpose

Analyse your Google Ads account performance at the start of each month, identify your AdPulse zone, and get 3-5 prioritised recommendations for where to focus your optimisation efforts.

## When to Use

- **Start of each month** - Begin every month with a strategy session
- **After major changes** - Reassess zone after significant budget or performance shifts
- **Before client meetings** - Get a clear picture of account status
- **When feeling overwhelmed** - Let the framework prioritise your actions

## Prerequisites

- Client name and account details
- Campaign performance data for the last 30 days
- Target CPA or ROAS goal
- Monthly budget target
- (Optional) Your observations about the account

## How It Works

### Step 1: Data Access

First, I'll attempt to get your campaign data:

**Option A: Google Ads MCP (Recommended)**
If you have Google Ads MCP installed, I can fetch the data automatically.

> "Please use the Google Ads MCP to fetch campaign performance data for [client name] for the last 30 days."

**Option B: CSV Export (Fallback)**
If MCP isn't available, please export a campaign performance report from Google Ads:

1. Go to Google Ads > Reports
2. Select: Campaigns report
3. Columns: Campaign, Cost, Conversions, Conv. Value, CPA, ROAS, Budget
4. Date range: Last 30 days
5. Export as CSV

### Step 2: Gather Context

I'll ask you for:

1. **Client Name**: Which client/account are we analysing?
2. **Monthly Budget**: What's the target monthly spend?
3. **Performance Target**: What's the target CPA or ROAS?
4. **Your Observations**: What have you noticed in the last 30 days?

### Step 3: Calculate Metrics

Using your data, I'll calculate:

- **Budget Pacing %**: (Actual Spend ÷ Expected Spend) × 100
- **Performance Variance %**: (Actual CPA ÷ Target CPA) × 100 or (Actual ROAS ÷ Target ROAS) × 100
- **Remaining Budget**: Monthly Budget - Actual Spend
- **Required Daily Spend**: Remaining Budget ÷ Days Remaining

### Step 4: Determine Zone

Based on the calculations:

| Budget Pacing | Performance | Zone |
|--------------|-------------|------|
| >110% | Poor | 🔴 Red (CRITICAL) |
| 90-110% | Poor | 🟠 Orange (High) |
| <90% | Good | 🟡 Yellow (Scaling) |
| >110% | Good | 🔵 Blue (Low) |
| 90-110% | Good | 🟢 Green (Maintain) |

### Step 5: Generate Recommendations

Based on your zone, I'll provide:

- 3-5 prioritised action items
- Estimated impact for each action
- Specific metrics to target
- Reasoning for each recommendation

### Step 6: Approval Gate

⚠️ **APPROVAL REQUIRED**

Before we proceed, please review the recommendations and tell me:
- Which actions would you like to tackle?
- Any actions you want to skip or modify?
- Questions about any recommendations?

This ensures we focus on what matters most to you.

### Step 7: Recommend Next Skill

Based on your approved actions, I'll suggest the best skill to run next:

- Budget issues → **Bid & Budget Optimizer**
- Keyword waste → **Keyword Optimizer**
- Ad performance → **Ad Copy Generator**
- Conversion issues → **Landing Page Optimizer**

I'll include the specific parameters to pass to the next skill.

## Expected Interaction Flow

```
You: [Paste this SKILL.md content]

Claude: Let's run a Monthly Strategy Session! First, I'll try to get your
campaign data. Do you have Google Ads MCP installed, or would you prefer
to provide a CSV export?

You: I'll provide a CSV. [Pastes CSV data]

Claude: Got it! Now I need some context:
1. What's the client name?
2. What's the monthly budget target?
3. What's the target CPA (or ROAS)?
4. What have you noticed in the last 30 days?

You: Client is Brisbane Physio Clinic. Budget is $3,000/month.
Target CPA is $50. Noticed more competitor ads appearing lately.

Claude: [Analyses data and presents zone assessment]

📊 **Strategy Session: Brisbane Physio Clinic**

**Zone Assessment: 🔴 RED - CRITICAL**
- Budget Pacing: 127% (Overspending)
- Performance: CPA $78 (156% of target - Poor)

**Your 5 Priority Actions:**
1. [Action with reasoning and impact]
2. [Action with reasoning and impact]
3. [Action with reasoning and impact]
4. [Action with reasoning and impact]
5. [Action with reasoning and impact]

**⚠️ APPROVAL NEEDED**
Which of these actions would you like to tackle this month?

You: Let's do actions 1, 2, and 4.

Claude: Great! Based on your selections, I recommend running the
**Keyword Optimizer** next with focus on [specific parameters].

[Provides strategy session report]
```

## Outputs

### 1. Zone Assessment Summary
```
📊 Strategy Session: [Client Name]
Date: [Today's Date]

Zone: [Emoji] [Zone Name] - [Priority Level]

Key Metrics:
- Monthly Budget: $X,XXX
- Actual Spend: $X,XXX (XX% of month)
- Budget Pacing: XXX%
- Target CPA: $XX
- Actual CPA: $XX
- Performance: XX% of target
```

### 2. Prioritised Recommendations
```
Priority Actions:

1. [Action Title] - [Est. Impact]
   Reasoning: [Why this matters]

2. [Action Title] - [Est. Impact]
   Reasoning: [Why this matters]

[etc.]
```

### 3. Next Skill Recommendation
```
Recommended Next Step:
→ Run [Skill Name] with parameters:
  - Focus: [Specific focus area]
  - Priority: [What to prioritise]
  - Data needed: [What to prepare]
```

## Tips

- **Run at month start**: Days 1-5 is ideal for strategy sessions
- **Be honest about observations**: Your insights matter
- **Don't skip approval gate**: Review before acting
- **Follow the zone priorities**: Red/Orange before Yellow/Green
- **Document findings**: The report is useful for client updates

## Related Skills

- **Bid & Budget Optimizer**: Run when budget issues are identified
- **Keyword Optimizer**: Run when wasted spend is flagged
- **Ad Copy Generator**: Run when ad performance is poor
- **Landing Page Optimizer**: Run when conversion rate needs improvement

---

*Start your month with clarity - let AdPulse guide your priorities*
