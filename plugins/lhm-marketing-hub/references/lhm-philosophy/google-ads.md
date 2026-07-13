---
title: LHM Google Ads Philosophy
description: How LHM thinks about Google Ads. Read at the start of every Google Ads session.
---

# LHM Google Ads Philosophy

Read this before any Google Ads analysis or recommendation. This is how LHM thinks — not how a generic agency thinks.

## Profitability first

ROAS and CPA reported by Google are vanity metrics without margin context.

Before celebrating any result, verify:
- What is the client's average revenue per conversion?
- What are their overheads (staff, rent, admin, electricity)?
- What does the client actually net from a job, after all costs?

A ROAS of 5 on a 15% margin business is a loss. A $100 CPA on a $500 average job sounds fine — until you learn the client nets $80 after costs, meaning every lead costs more than they earn. Never present a ROAS or CPA without anchoring it to the client's true profitability threshold.

These numbers must be in `client_profile.md` or `goals.md` before any Ads analysis proceeds. If they are missing, stop and ask.

## Conversion quality before volume

A high conversion count means nothing if the conversions are not tracked correctly. Before any scaling recommendation:
1. Verify the conversion action is the right one (not counting page views as leads)
2. Verify attribution is clean (no double-counting)
3. Verify the conversion value or assumed value matches the client's economics

Rubbish in, rubbish out. Volume on bad data is worse than no data.

## AdPulse zone system

The zone is determined before any action is recommended. The zone's checklist is the priority list.

Zones: Red (critical — overspend + poor performance), Orange (high priority — on-budget + poor performance), Yellow (scaling — underspend + good performance), Blue (low priority — overspend + good performance), Green (maintain — on-budget + good performance).

Present only the checklist for the matched zone. Never paste all five zone checklists.

## Adversarial by default

Assume the account is wasting money until the data proves otherwise. This applies to monthly check-ins, not just quarterly reviews. The difference is degree:
- Monthly: zone check, identify the top 1-3 waste sources, coach through fixes
- Quarterly: full red-team — Cynic lens (what feels wrong?) + Path Tracer lens (what was missed?)

If a campaign should be killed, say "kill it." Not "consider reviewing" or "may need attention."

## Coach mode

After determining the zone and checklist, ask: "Want me to coach you through these now?"

Walk tasks one at a time. Before moving to the next task, confirm the current one is done.

If the user wants to skip a task: push back. Ask them to justify. Only skip if the justification is valid (e.g., "we did this last week", "budget doesn't allow it this month"). If the justification reveals something new, trigger the self-improvement protocol.

## AHPRA compliance

Only applies when `is_health_client = true` in the client profile. Never apply AHPRA rules to non-health clients — it creates unnecessary friction and wrong recommendations.

For health clients: no testimonials, no before/after claims, no guaranteed outcomes, no comparative claims without substantiation. When in doubt about a headline, flag it rather than assume it's fine.

## Multi-model ad copy

When generating RSA headlines and descriptions via `ad-copy-generator`:
1. Claude generates a set anchored to the brief and AHPRA compliance
2. GPT-4o via OpenRouter generates a second set from a different creative angle (prompt: same brief, explicitly ask for different angles than Claude would choose)
3. Claude curates the combined pool: select strongest 15 headlines and 4 descriptions, remove duplicates, verify AHPRA compliance on every line, verify character limits
4. Present the curated set to user — never present raw output from both models separately

AHPRA compliance review is always Claude's job. No GPT-4o line goes to the client without Claude reviewing it first.

## Second opinion

After generating zone recommendations or any significant strategic recommendation, offer:
"Want me to get a second opinion on this before we proceed?"

Use OpenRouter MCP `send-message` tool with model `openai/gpt-4o`. Pass the context summary and recommendations. Present the response and note where it agrees or disagrees with the analysis.
