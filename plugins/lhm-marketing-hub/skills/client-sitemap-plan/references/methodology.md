# Methodology — designing the client site architecture

Read this before assembling `sitemap.json`. The deliverable is a working plan: the full page architecture for the site, colour-coded by state and grouped by build order, that the client and the team both work from as pages get written.

## The core diagnosis (why more pages)

Most local-service and health sites bundle everything onto a handful of pages. Google ranks a page for one main idea, not five, so a single "Services" page covering six services captures almost none of them. The plan's job is to give every distinct thing the business does, and every place it serves, its own page.

Look for these gaps:

- **Bundled services.** One page covering many services. Split into one page per service, each targeting its own head term.
- **Demand living only in the blog.** High-volume commercial or funding themes that exist as blog posts but have no conversion page. Usually the biggest single win, because a blog post is not built to convert.
- **No location pages.** A business serving a region with zero suburb or town pages is invisible for "near me" and the map pack.
- **No audience or funding pages** where the buying decision is shaped by who the customer is (seniors, disability/NDIS) or how they pay (Home Care Packages, Support at Home, private).

## Building the page architecture

Group the proposed pages into sections that mirror how a visitor would navigate:

1. **Core** — Home (usually *enhance*), About, Contact, Blog hub.
2. **Services** — a hub per service family, then one page per granular service. Un-bundle aggressively. Each service with its own search demand earns a page.
3. **Who We Help** (audience) — segment pages where identity drives the decision.
4. **Getting Started / Funding** — one page per funding pathway. In Australian health and aged care this is high-value: NDIS, Home Care Packages, and the Support at Home program (live since 1 November 2025, with garden and home maintenance as funded services). Home Care Packages and Support at Home carry large informational search volume.
5. **Areas We Serve** (locations) — a hub plus suburb and town pages, built in tiers.

### Location pages, and being honest about them

Individual suburb searches ("gardener ‹suburb›") are tiny. Location pages are not a head-term play. They win the **map pack** and the large **"near me"** long tail, and they localise every service.

Build a **Phase 1** of the genuine population centres and the client's home base first, prove the model against real GSC data, then expand. Say this plainly in the section `note`, and mean it: with an existing client you will be held to it at the next review.

### Status colours

- `have` (green) — live and fine as it is.
- `enh` (yellow) — live but weak, scheduled for a rebuild.
- `new` (red) — not written yet.

For an existing client these are delivery states, not a sales device. The file gets used to track what is done, so a wrong colour becomes a missed page or duplicated work. Verify each one against the live site rather than against what the client folder claims.

## Sequencing the build

The phase grouping carries the narrative that the prospect version puts in the opportunity widget. Order the work on evidence:

1. **Pages that already earn impressions but rank on page two.** Cheapest wins available. A rebuild here moves existing demand, and GSC proves it before you start.
2. **New pages with measured demand and clear commercial intent.** Service and funding pages usually sit here.
3. **New pages that complete a cluster.** They lift the pages around them even where their own volume is thin.
4. **Location pages, Phase 1 only.** Prove the template on the real population centres before committing to a long tail of suburbs.
5. **Everything else, as backlog.** Say plainly that it is backlog rather than pretending a date exists.

Write the reasoning into the section `note` so the sequence survives a change of account manager.

## Sourcing the numbers

For an existing client, use both sources and keep them distinct:

- **Search Console** — actual impressions, clicks and average position for pages that exist. This is evidence, and it drives which pages are marked `enh` and what gets sequenced first.
- **Keywords Everywhere MCP** (`get_keyword_data`, `get_related_keywords`) — demand estimates for pages that do not exist yet.

Record volume per intended page in `vol`. Never fabricate a figure. Where there is no measured volume, use `null` so it renders "n/a" rather than a made-up number.

Record the source and the retrieval month in the footer so the numbers can be re-checked at the next review.

## What this deliverable does not do

No lead estimates, no click-through or conversion modelling, no revenue projection. Those belong in the prospect version. Adding them to a live client's content plan invites the plan to be read as a forecast, and it will be quoted back at the next quarterly review.
