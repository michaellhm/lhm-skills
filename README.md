# LHM Marketing Skills

A Claude Code plugin marketplace for structured marketing work sessions. Built by LHM Digital.

## What This Is

143 skills across nine Claude Code plugins (52 marketing, 36 WordPress, 19 GMB/local SEO, 7 content engine, 1 learn, 6 finance, 3 client updates (deprecated — moved to project hub), 2 skill ops, 17 project hub) with a structured orchestration layer. The plugins enforce a consistent workflow: verify the client folder, load client context, route to the right skill, and save outputs in a predictable folder structure.

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
  agents/start.md                       # Main entry point — client context, routing, session management
  agents/google-ads.md                  # Self-sufficient Google Ads specialist
  agents/seo.md                         # Self-sufficient SEO specialist
  agents/content.md                     # Self-sufficient content specialist
  agents/wordpress.md                   # Self-sufficient WordPress specialist
  agents/marketing-assistant.md         # (legacy alias) — routes to start agent
  skills/                              # All 52 skills
    client-onboarding/                 # Client profile setup
    ad-copy-generator/                 # Google Ads RSA generation
    bid-budget-optimizer/              # Budget and bid strategy
    keyword-optimizer/                 # Keyword and wasted spend analysis
    landing-page-optimizer/            # Landing page audits
    google-ads-monthly-review/          # Account health check and zone analysis
    quarterly-adversarial-review/       # 90-day red-team review: reconstructs prior work, tests assumptions, assigns AdPulse zone
    competitive-analysis/               # Competitor evaluation and market positioning
    keyword-research/                  # Keyword discovery, intent analysis, topic clusters
    content-gap-analysis/              # Keyword, topic, and content gap identification
    seo-content-writer/                # SEO-optimized blog posts and articles
    geo-content-optimizer/             # AI citation and GEO optimization
    meta-tags-optimizer/               # Title tags, meta descriptions, OG tags
    meta-tag-refresh/                  # Site-wide meta refresh from Ads/GSC data, slug audit, Rank Math push + 301s
    content-quality-auditor/           # CORE-EEAT 80-item quality audit
    pr-content-auditor/                # Rewrite rejected Digital PRs
    content-refresher/                 # Identify and refresh underperforming content
    ga-event-config/                   # GA4 event discovery and conversion classification
    ga-dashboard-artifact/             # Analytics dashboard artifact with period comparison
    campaign-playbook-generator/       # Campaign & sales playbooks from transcripts
    pmax-banner-generator/             # Performance Max creative assets (CSV)
    pmax-campaign-setup/               # Performance Max campaign build spec for local businesses
    pmax-optimizer/                    # Performance Max monthly + 90-day optimisation passes
    copywriting/                       # Marketing copy for any page
    email-sequence/                    # Drip campaigns and email flows
    seo-audit/                         # SEO diagnostics
    pricing-strategy/                  # Pricing and packaging
    service-page-generator/             # Full service/condition page generation
    taya-question-discovery/            # They Ask, You Answer question bank
    ... and 20 more
plugins/lhm-wordpress-hub/             # WordPress build plugin
  .claude-plugin/plugin.json            # Plugin manifest
  agents/                               # 8 phase agents
    wordpress-orchestrator.md           # Main entry point and phase router
    client-intake.md                    # Phase A — client context extraction
    seo-strategist.md                   # Phase B — sitemap and briefs
    content-writer.md                   # Phase C — page copywriting
    design-system.md                    # Phase D — brand, design, prototype
    wordpress-builder.md                # Phase E — theme scaffold and page build
    site-ops.md                         # Phase F — performance and security
    site-extension.md                   # Post-launch page management
  skills/                               # All 36 skills
    wp-start/                           # Entry point — /wp-start command
    wp-project-setup/                   # Initialize project folder structure (platform choice)
    wp-project-manager/                 # PM doc — create, read, mark complete, gate-check
    client-data-collection/             # Phase 0 — Drive folder, BasicOps checklist, data-gathering email, weekly follow-up
    digital-audit/                      # Phase 4 — GA4 checks (data, key events, Ads link) + manual GTM/GSC checklist
    client-context-intake/              # Extract facts from call notes
    sitemap-architect/                  # Site IA and keyword map
    page-brief-generator/               # Per-page content briefs
    page-copywriter/                    # Write page copy from briefs
    brand-discovery/                    # Brand guidelines extraction
    design-system-generator/            # Design tokens and theme.json specs
    html-prototype/                     # Static HTML/CSS prototypes → pushes to prototype repo
    block-architect/                    # Gutenberg block specifications
    theme-scaffold/                     # Custom block theme scaffolding
    css-sync-check/                     # Validate theme CSS matches prototype
    wp-page-builder/                    # Build pages in WordPress
    wp-blog-publisher/                  # Publish blog posts via WP-CLI
    visual-qa/                          # Pixel-perfect visual regression testing
    wp-performance/                     # Performance audit and optimization
    wp-security/                        # Security hardening checklist
    site-launch-qa/                     # Automated + guided pre-launch QA checklist (WordPress & Astro)
    repo-init/                          # Create GitHub repos and scaffold docs/ for a new client
    repo-install/                       # Clone client repos onto a new machine
    astro-build/                        # Phase 5 for Astro — scaffold, convert prototype, SEO, deploy
    decap-cms-astro/                    # Decap CMS setup for Astro on Cloudflare Pages — Git-backed editing, drafts, previews
    lp-project-manager/                 # LP campaign PM doc — create, read, mark complete
    lp-subsite-setup/                   # Configure multisite subsite for LP campaign
    lp-copy/                            # Write landing page copy per ad group
    lp-prototype/                       # Build HTML/CSS landing page prototypes → pushes to prototype repo
    lp-deploy-1/                        # Push first LP prototype to WordPress
    lp-deploy-2/                        # Convert LP to native Gutenberg blocks
    lp-deploy-3/                        # Deploy remaining LP pages
    lp-subsite-deploy/                  # Deploy subsite from Docker to live server
    wp-ssh-deploy/                      # General WordPress SSH deployment
    contact-form-submissions/           # Cloudflare Pages forms — D1, Turnstile, private R2 uploads, email, admin
    rankmath-redirects/                 # Rank Math 301 redirect creation, import, cleanup, and verification
plugins/lhm-gmb-hub/                   # GMB/Local SEO plugin
  .claude-plugin/plugin.json            # Plugin manifest
  agents/                               # 6 agents
    gmb-orchestrator.md                 # Master agent — phase detection and routing
    onboarding-agent.md                 # Month 0 — GBP foundation
    service-optimizer-agent.md          # Month 1 — service pages
    content-expansion-agent.md          # Month 2 — FAQ or overlay pages
    link-building-agent.md              # Month 3 — link acquisition
    content-writer.md                   # 8-pass writing utility
  skills/                               # All 19 skills
    gmb-project-manager/                # Project tracking and status
    run-local-diagnostic/               # Grid scans + competitor audit
    gbp-optimiser/                      # GBP profile optimisation
    gbp-post-generator/                 # Weekly posts (13, matched to 3-month cycle)
    citation-audit/                     # Directory NAP check
    entity-mapper/                      # Competitor entity extraction
    site-architecture-mapper/           # GBP-mirrored silo
    blog-schedule-builder/              # 3-month blog content schedule
    monthly-loop-setup/                 # Scheduled automation for the monthly GMB cycle
    service-priority-selector/          # Pick 3 services per cycle
    consistency-signal-audit/           # 8 homepage signals
    service-page-writer/                # Goal-completion content
    technical-page-audit/               # Schema, speed, indexing
    faq-content-builder/                # PAA to supporting pages
    neighbourhood-overlay-writer/       # Geo pages
    link-gap-finder/                    # Pages missing links
    local-authority-finder/             # Chambers, sponsorships
    pr-brief-generator/                 # Press release drafts
    monthly-cycle-report/               # Monthly/cycle reports
  references/                           # 10 reference files
    anti-ai-writing-guidelines.json
    ahpra-compliance-framework.md
    gmb-ranking-principles.md
    mcp-setup-guide.md
    8-pass-writing-engine.md
    content-guardrails/                 # 4 content type guardrails
plugins/lhm-content-engine/            # Content pipeline plugin
  .claude-plugin/plugin.json            # Plugin manifest
  agents/content-orchestrator.md        # Batch pipeline orchestrator
  skills/                               # All 7 skills
    generate-outline/                   # Structured article outline from CSV row
    write-blog/                         # Full blog article from outline
    generate-social-posts/              # GMB social posts from blog content
    quality-controller/                 # Anti-AI refinement and compliance gate
    publish-google-doc/                 # Create formatted Google Doc for review
    update-csv/                         # Update tracking CSV with results
    run-batch/                          # Orchestrate full pipeline for all rows
plugins/lhm-learn/                    # Session learning capture plugin
  .claude-plugin/plugin.json            # Plugin manifest
  skills/                               # All 1 skill
    learn/                              # /learn — capture session learnings
plugins/lhm-client-updates-hub/       # (deprecated — skills migrated to lhm-project-hub; shims remain)
  .claude-plugin/plugin.json            # Plugin manifest
  skills/                               # All 3 skills — shims that route to lhm-project-hub
    post-meeting-review/                # Post-meeting follow-up triage — state files, BasicOps subtasks, agent routing, team email (shim → lhm-project-hub)
    client-update/                      # Propagate a client data change across all client files
    client-update-email/                # Plain-language client-facing update emails
plugins/lhm-project-hub/              # Agency process hub — sales handover through monthly/quarterly reviews
  .claude-plugin/plugin.json            # Plugin manifest
  agents/pm-orchestrator.md             # Main entry point — reads client state, flags cadence breaches, routes to the right skill
  skills/                               # All 17 skills
    sales-handover/                     # Hand a newly-closed client from sales to delivery
    client-onboarding/                  # Scope-aware Obsidian-first onboarding — 5 top-level BasicOps gates
    website-kickoff/                    # New website build kickoff (WordPress or Astro) → handoff to WordPress hub
    landing-page-kickoff/               # New PPC landing page campaign kickoff → handoff to WordPress hub
    seo-kickoff/                        # New SEO engagement kickoff → handoff to the SEO specialist
    gmb-kickoff/                        # New GMB/local SEO cycle kickoff → handoff to the GMB hub
    blog-kickoff/                       # New blog/article content pipeline kickoff → handoff to the content engine
    google-ads-kickoff/                 # New Google Ads campaign build kickoff — gates on conversion tracking
    monthly-review/                     # Monthly per-client review engine (3 modes: wrap, prep, account review)
    quarterly-review/                   # Quarterly strategy review — 3-month data pull + next-quarter plan
    client-meeting-email/               # Client-ready meeting follow-up email + meeting capture — saves notes, stands up the BasicOps card
    post-meeting-review/                # Post-meeting follow-up triage — state files, BasicOps subtasks, team email (migrated from client updates hub; shim remains)
    client-update/                      # Propagate a client data change across all client files (migrated from client updates hub; shim remains)
    client-update-email/                # Plain-language client-facing update emails (migrated from client updates hub; shim remains)
    wp-project-manager/                 # Website build PM doc (migrated from WordPress hub; shim remains)
    lp-project-manager/                 # Landing page campaign PM doc (migrated from WordPress hub; shim remains)
    gmb-project-manager/                # GMB optimisation cycle PM doc (migrated from GMB hub; shim remains)
  references/                           # 5 reference files + checklists/ + templates/
    folder-convention.md                # Canonical client folder + current-projects.md structure
    team-roster.md                      # Team roles, contacts, retired-tool warnings
    cadences.md                         # Review/report cadence rules per client tier
    kickoff-pattern.md                  # Shared kickoff skill pattern (intake → state → BasicOps → email → handoff)
    anti-ai-writing-guidelines.json     # Shared anti-AI writing guardrails
    checklists/                         # 4 onboarding checklists (billing, platform access, tracking, first 30 days)
    templates/                          # 6 email/doc templates (kickoff, billing, welcome, handover, meeting agenda)
plugins/lhm-skill-ops/                # Team skill-improvement pipeline plugin
  .claude-plugin/plugin.json            # Plugin manifest
  skills/                               # All 2 skills
    sync-observations/                  # Push local Task Observer logs to observations/<person>/
    weekly-skill-review/                # Cross-team review — applies learnings on a branch, opens a PR
```

## Skills Catalog

**Client Management** (2 skills): Client onboarding and profile setup, campaign playbook generation from transcripts.

**Google Ads & PPC** (9 skills): Ad copy, bid/budget optimization, keyword analysis, landing page audits, monthly review (+ agent for full execution), quarterly adversarial 90-day review, PMax banner creative, PMax campaign setup for local businesses, PMax monthly + 90-day optimisation.

**Strategy & Research** (3 skills): Competitive analysis with Porter's 5 Forces, keyword research with intent analysis and topic clustering, They Ask You Answer question discovery.

**SEO & Content** (9 skills): Content gap analysis, service page generation, SEO content writing, GEO/AI citation optimization, meta tags optimization, site-wide meta tag refresh (Ads conversion + GSC decline data, slug audit, Rank Math REST push with 301 redirects), CORE-EEAT content quality auditing, PR content rewriting for rejected distributions, content refresh planning.

**Analytics & Reporting** (2 skills): GA4 event discovery and conversion classification, analytics dashboard artifact with period comparison and visual output.

**SaaS & Growth Marketing** (25 skills): A/B testing, analytics tracking, competitor pages, content strategy, copy editing, copywriting, email sequences, form CRO, free tool strategy, launch strategy, marketing ideas, marketing psychology, onboarding CRO, page CRO, paid ads, paywall CRO, popup CRO, pricing strategy, product marketing, programmatic SEO, referral programs, schema markup, SEO audit, signup flow CRO, social content.

**Pricing** (1 skill): Standalone pricing strategy and monetization.

### GMB Hub (Local SEO)

**Month 0 — Onboarding** (8 skills): Project management and tracking, 169-point grid scan diagnostics, GBP profile optimisation, weekly post generation (13 posts, matched to the 3-month cycle), citation audit, competitor entity mapping, GBP-mirrored site architecture, 3-month blog content schedule builder.

**Month 1 — Service Pages** (4 skills): Priority service selection, homepage consistency signal audit, goal-completion service page writing (via 8-pass engine), technical page audit with schema and indexing checks.

**Month 2 — Content Expansion** (2 skills): FAQ and supporting content from PAA/Reddit questions, hyper-local neighbourhood overlay pages for proximity problems.

**Month 3 — Link Building** (3 skills): Link gap analysis, local authority opportunities (chambers, sponsorships, .edu links), PR brief generation.

**Cross-Phase** (2 skills): Adaptive monthly/cycle reporting with ranking trends, scheduled automation setup for the recurring monthly GMB cycle (Telegram + email notifications, BasicOps task creation, site-change staging).

### WordPress Hub

**Website Build Pipeline** (23 skills): Project setup (with WordPress/Astro platform choice), Phase 0 client data collection (Drive folder, BasicOps access checklist, data-gathering email, weekly automated follow-up), client context intake, sitemap architecture, page briefs, page copywriting, brand discovery, design system generation, HTML prototyping, block architecture, theme scaffolding, CSS sync checking, page building, blog publishing, visual QA, performance optimization, security hardening, the /wp-start entry point, the Astro build skill (scaffold, prototype conversion, SEO, deployment), Decap CMS setup for Astro on Cloudflare Pages (Git-backed editing, drafts, scheduled publishing, deploy previews), the pre-launch QA checklist (automated + guided, for both WordPress and Astro), Rank Math 301 redirect management, and the Phase 4 digital audit (automated GA4 checks — data, key events, Ads link — plus a manual GTM/Search Console checklist).

**Git Repo Workflow** (2 skills): First-time client repo setup — creates GitHub repos, scaffolds docs/ context folder, commits the initial scaffold, and invites confirmed default LHM collaborators with write access (`repo-init`). Clones an existing client project onto a new machine or pulls the latest (`repo-install`).

**Landing Page Pipeline** (7 skills): Subsite setup for LP campaigns, landing page copywriting per ad group, HTML/CSS prototype generation (auto-pushed to prototype repo), WordPress deployment (HTML blocks), Gutenberg block conversion, multi-page deployment, and live server deployment via SSH.

**Deployment** (1 skill): General-purpose WordPress SSH deployment (theme, pages, CPTs, media, customizer, menus, options).

**Cloudflare Pages Forms** (1 skill): End-to-end contact form implementation for Astro/Cloudflare Pages — Cloudflare D1 persistence, Turnstile spam protection, Mailgun/Postmark/Resend email notifications, GA-trackable thank-you pages, and a Basic Auth protected admin submissions view.

### Content Engine

**Content Pipeline** (7 skills): CSV-driven batch processing for allied health clinics. Structured article outline generation, blog writing with anti-AI refinement, GMB social post generation, compliance quality gate, Google Doc publishing, tracking CSV updates, and full batch orchestration.

### Learn

**Session Capture** (1 skill): Scan conversation context for skill learnings and client profile updates, write to the correct LEARNED.md and client_profile.md files.

### Client Updates Hub (deprecated — moved to Project Hub)

**Client Communication** (3 skills, shims only): All three skills now live in `lhm-project-hub`; the entries here route straight there. See the Project Hub catalog below for current descriptions. Kept in place so existing muscle memory and any external references to `lhm-client-updates-hub:*` keep working.

### Project Hub

**Client Lifecycle** (2 skills): Sales-to-delivery handover — pulls the sales conversation, creates the client folder, and hands off with a structured brief. Tier 1 client onboarding pipeline across four resumable phases (payment/billing, platform access, tracking setup, first 30 days).

**Delivery Kickoffs** (6 skills): Website build kickoff (WordPress or Astro), PPC landing page campaign kickoff, SEO engagement kickoff, GMB/local SEO cycle kickoff, blog/article content pipeline kickoff, and Google Ads campaign build kickoff (gated on conversion tracking being live). Each follows the same shared pattern: intake, a project-management state file, a BasicOps scaffold with backwards-scheduled milestones, a client kickoff email, and handoff to the delivery specialist hub.

**Client Success** (6 skills): Monthly per-client review engine with three modes (KP wrap-up, meeting prep, full account review). Quarterly strategy review — pulls three months of GA4/Ads/GSC data plus the quarter's monthly reports and drafts the next 3/6-month plan. Client-ready meeting follow-up email and meeting capture — turns the Fathom summary and transcript into a polished Gmail-ready wrap with decisions verified against the transcript, action items grouped by owner, and next steps; also saves the structured meeting record and stands up the client's BasicOps card with a matching summary note. Post-meeting follow-up triage — reads that saved meeting record to update client state files, sweep the client folder for stale artefacts, and turn action items into BasicOps subtasks, walking through each one to propose an owner and offer to run research or prepare a live-system handoff plan before drafting a team summary email (migrated from Client Updates Hub). Propagates a client data change across every file that references it (migrated from Client Updates Hub). Plain-language client-facing update emails after completing work (migrated from Client Updates Hub).

**Project Managers** (3 skills): Website build PM doc, landing page campaign PM doc, and GMB optimisation cycle PM doc — all migrated from their originating hubs (WordPress hub, WordPress hub, GMB hub respectively); shims remain in place there so existing routing keeps working.

### Skill Ops

**Team Skill Improvement** (2 skills): Weekly sync of each person's local Task Observer observation logs into `observations/<person>/` in this repo, and a cross-team weekly review that deduplicates observations, applies clear improvements to plugin skills on a branch, bumps versions, and opens a PR for sign-off (see TEAM-SETUP.md).

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
