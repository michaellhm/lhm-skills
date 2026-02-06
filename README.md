# LHM Marketing Skills

A Claude Code plugin marketplace for marketing workflows. Built by LHM Digital.

## What This Is

A collection of 33 marketing skills packaged as a Claude Code plugin. You invoke `/start` (or just describe what you need) and the plugin identifies your client, picks the right skill, and walks you through the task.

## Structure

```
.claude-plugin/marketplace.json    # Marketplace manifest
plugins/lhm-marketing-hub/        # The plugin
  .claude-plugin/plugin.json       # Plugin manifest
  agents/marketing-assistant.md    # Orchestrator agent
  skills/                         # All 33 skills
    start/                        # Entry point - /start command
    ad-copy-generator/            # Google Ads RSA generation
    bid-budget-optimizer/         # Budget and bid strategy
    keyword-optimizer/            # Keyword and wasted spend analysis
    landing-page-optimizer/       # Landing page audits
    monthly-strategy-session/     # Monthly account review
    pmax-banner-generator/        # Performance Max assets
    copywriting/                  # Marketing copy for any page
    email-sequence/               # Drip campaigns and email flows
    seo-audit/                    # SEO diagnostics
    pricing-strategy/             # Pricing and packaging
    ... and 23 more
```

## Skills Catalog

**Google Ads & PPC** (6 skills): Ad copy, bid/budget optimization, keyword analysis, landing page audits, monthly strategy, PMax banners.

**SaaS & Growth Marketing** (25 skills): A/B testing, analytics tracking, competitor pages, content strategy, copy editing, copywriting, email sequences, form CRO, free tool strategy, launch strategy, marketing ideas, marketing psychology, onboarding CRO, page CRO, paid ads, paywall CRO, popup CRO, pricing strategy, product marketing, programmatic SEO, referral programs, schema markup, SEO audit, signup flow CRO, social content.

**Pricing** (1 skill): Standalone pricing strategy and monetization.

## Usage

Install the plugin, then either:
- Say "I need to work on [client name]" and the agent will guide you
- Use `/start` to begin a structured work session
- Ask for a specific task directly (e.g., "write ad copy for my physio client")
