# LHM Marketing Skills

A Claude Code plugin marketplace for structured marketing work sessions. Built by LHM Digital.

## What This Is

35 marketing skills packaged as a Claude Code plugin with a structured orchestration layer. The plugin enforces a consistent workflow: verify the client folder, load client context, route to the right skill, and save outputs in a predictable folder structure.

## How It Works

1. **Pre-flight** — Checks you're in a directory with client folders
2. **Client selection** — Finds or creates the client folder, runs onboarding if needed
3. **Context load** — Reads `client_profile.md` as authoritative context
4. **Task routing** — Matches your request to a skill from the catalog
5. **Skill execution** — Loads the skill, saves outputs to `client/skill_name/YYYY-MM/`

Use `/start` to begin a session, or just describe what you need.

## Structure

```
.claude-plugin/marketplace.json         # Marketplace manifest
plugins/lhm-marketing-hub/             # The plugin
  .claude-plugin/plugin.json            # Plugin manifest
  agents/marketing-assistant.md         # Orchestrator agent
  agents/google-ads-monthly-review.md  # Full monthly review with skill chaining
  skills/                              # All 35 skills
    start/                             # Entry point — /start command
    client-onboarding/                 # Client profile setup
    ad-copy-generator/                 # Google Ads RSA generation
    bid-budget-optimizer/              # Budget and bid strategy
    keyword-optimizer/                 # Keyword and wasted spend analysis
    landing-page-optimizer/            # Landing page audits
    google-ads-monthly-review/          # Account health check and zone analysis
    campaign-playbook-generator/       # Campaign & sales playbooks from transcripts
    pmax-banner-generator/             # Performance Max assets
    copywriting/                       # Marketing copy for any page
    email-sequence/                    # Drip campaigns and email flows
    seo-audit/                         # SEO diagnostics
    pricing-strategy/                  # Pricing and packaging
    ... and 22 more
```

## Skills Catalog

**Client Management** (2 skills): Client onboarding and profile setup, campaign playbook generation from transcripts.

**Google Ads & PPC** (6 skills): Ad copy, bid/budget optimization, keyword analysis, landing page audits, monthly review (+ agent for full execution), PMax banners.

**SaaS & Growth Marketing** (25 skills): A/B testing, analytics tracking, competitor pages, content strategy, copy editing, copywriting, email sequences, form CRO, free tool strategy, launch strategy, marketing ideas, marketing psychology, onboarding CRO, page CRO, paid ads, paywall CRO, popup CRO, pricing strategy, product marketing, programmatic SEO, referral programs, schema markup, SEO audit, signup flow CRO, social content.

**Pricing** (1 skill): Standalone pricing strategy and monetization.

## Key Behaviours

- **Client context is mandatory** — `client_profile.md` is loaded before any skill runs
- **No hallucination** — the plugin refuses to invent metrics, files, or context
- **Google Ads via MCP first** — falls back to CSV if MCC 394-736-1921 can't be reached
- **Structured outputs** — all work saved to `client/skill_name/YYYY-MM/` as `.md`, `.csv`, or `.json`
- **Confirm-then-act** — narrates state changes, confirms before executing

## Usage

```
/start                              # Begin a structured work session
"I need to work on [client name]"   # The agent picks up from there
"Write ad copy for my physio client" # Routes directly to the right skill
```
