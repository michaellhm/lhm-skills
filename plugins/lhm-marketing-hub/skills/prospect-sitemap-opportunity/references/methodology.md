# Methodology — designing the proposed sitemap and opportunity model

This is the thinking that turns a keyword list into a sitemap that sells. Read it before assembling `sitemap.json`. The goal of the deliverable is to make a prospect see, in one screen, that their current site only opens a small door to search demand and that a structured rebuild opens a much bigger one.

## The core diagnosis (why more pages)

Most local-service and health sites bundle everything onto a handful of pages. Google ranks a page for one main idea, not five, so a single "Services" page covering six services captures almost none of them. The rebuild's job is to give every distinct thing the business does, and every place it serves, its own page.

Look for these gaps on the live site:

- **Bundled services.** One page covering many services. Split into one page per service, each targeting its own head term.
- **Demand living only in the blog.** High-volume commercial or funding themes that exist as blog posts but have no conversion page. Usually the single biggest opportunity, because a blog post is not built to convert.
- **No location pages.** A business serving a region with zero suburb or town pages is invisible for "near me" and the map pack.
- **No audience or funding pages** where the buying decision is shaped by who the customer is (seniors, disability/NDIS) or how they pay (Home Care Packages, Support at Home, private).

## Building the page architecture

Group the proposed pages into sections that mirror how the client would navigate:

1. **Core** — Home (usually *enhance*), About, Contact, Blog hub.
2. **Services** — a hub per service family, then one page per granular service. Un-bundle aggressively. Each service with its own search demand earns a page.
3. **Who We Help** (audience) — segment pages where identity drives the decision.
4. **Getting Started / Funding** — one page per funding pathway. In Australian health and aged care this is high-value: NDIS, Home Care Packages, and the Support at Home program (live since 1 November 2025, with garden and home maintenance as funded services). Home Care Packages and Support at Home carry large informational search volume.
5. **Areas We Serve** (locations) — a hub plus suburb and town pages, built in tiers.

### Location pages, and being honest about them

Individual suburb searches ("gardener ‹suburb›") are tiny. Location pages are not a head-term play. They win the **map pack** and the large **"near me"** long tail, and they localise every service.

Recommend a **Tier 1** of the genuine population centres and the client's home base first, prove the model, then expand to Tier 2 and a backlog. Say this plainly in the section `note`. It protects credibility when a sharp prospect asks "who searches 'gardener Newtown'?"

### Status colours (the sales device)

- `have` (green) — page exists today. Only mark green what is genuinely live.
- `enh` (yellow) — exists but weak. Rebuild to rank and convert.
- `new` (red) — does not exist. Red means gap means opportunity, and it should visually dominate the Services, Funding and Areas sections. That contrast is the pitch.

## The opportunity model

The widget converts structure into a lead estimate the prospect can feel. Keep it conservative and defensible. A number a prospect can argue down destroys trust.

- **`imp_now` (current addressable searches/mo)** — sum the monthly volume of the head terms the *current* structure realistically targets. Bundled pages rank weakly, so keep this modest.
- **`imp_new` (proposed addressable searches/mo)** — sum the local, geo-qualified service terms plus the funding and audience terms the new structure targets. For the large national **"near me"** terms, include only a small local slice (around 1%), because only a fraction is capturable locally. Say so in `composition_note`. Leave giant informational terms (for example "home care packages") as stated upside rather than baking their full volume into the headline.
- **`ctr` / `conv`** — open conservative. 4% and 4% is a safe default for local service. They are editable in the page, so they can be tuned live on the call.
- **SEO slider** — each step adds `seo_step_pct`% to both impressions and conversion, with click-through held flat. Note in the page that CTR improves too, and that holding it flat is the conservative choice. This separates two messages cleanly: *the website* gets you the structure (Today to New website), and *ongoing SEO* compounds it (the slider). Keep the SEO framing a soft seed unless the prospect is buying SEO. The website is the hero of this deliverable.

Always write `composition_note` so the derivation of `imp_now` and `imp_new` is visible. "Illustrative and editable" is the right posture. It is a conversation tool, not a forecast.

Never fabricate a volume. If a term has no measured volume, set `vol` to `null` and let it render as "n/a".

## Sourcing the numbers

Use the Keywords Everywhere MCP for volumes (`get_keyword_data`, `get_related_keywords`). Pull, at minimum: each service plus the main city, "near me" variants, the funding terms for the vertical, and the second town or market if there is one.

If Search Console access exists, layer in where they already rank to sharpen priority. For a cold prospect, demand data alone is the honest basis, so label it as demand and not as rankings.

Record the source and the retrieval month in `composition_note` and in the footer, so the numbers can be re-checked later.
