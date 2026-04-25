# LHM WordPress Hub - Development Backlog

Future plugin development items captured during SOP work. Dated. Not prioritised.

## Open Items

### Phase 4 — Brand, Design System & Prototype

- **(2026-04-25) (1a) LHM design-prototype staging integration.** Add a skill (or extend `html-prototype`) to upload Phase 4 prototype variants to `lhmstaging.net/design/[clientname]/` (and `/v1/`, `/v2/`, `/v3/` subfolders for multiple variants). Needs SSH access configured per client and a consistent folder convention. Should handle: creating the folder, uploading the prototype HTML + assets, verifying assets resolve, returning the live URL for the client review email. Confirmed by SOP Phase 4 Step 4.5.

- **(2026-04-25) Client-facing brand style guide document.** Add a skill (or extend `brand-discovery`) to output a client-shareable brand style guide separate from `brand_guidelines.md`. Should include: primary and secondary colour palette with hex codes and usage examples, typography specimens (H1 through body + button), button variants (primary, secondary, tertiary, states), logo usage rules, imagery direction with example treatments, tone of voice examples. Output: PDF or Google Doc. Workflow: this document goes to the client in parallel with prototype work in Step 4.4 — should not block prototype progress. Confirmed by SOP Phase 4 Step 4.1.

- **(2026-04-25) Figma integration for design system.** Build a pathway for design system tokens to flow into Figma so designers can produce visual prototypes, then export back to code. Goal: reduce the "AI-looking" feel of pure HTML prototypes. Likely needs a Figma plugin or API integration that reads `design_system.md` and generates matching Figma variables, libraries, and components. Reverse flow (Figma back to HTML) is a separate scoping problem. Lower priority — the SOP intentionally bypasses Figma in favour of HTML prototypes.

### Phase 5 — WordPress Build

- **(2026-04-25) (1b) LHM site-staging deployment integration.** Extend `wp-ssh-deploy` (or wrap it in a lightweight skill) to push the local WP site to `staging.lhm.com.au/[clientname]/` (Phase 5 Step 5.10). Should handle theme files, pages, custom post types, meta fields, media, customizer/Site Editor settings, menus, and options. Confirmed by SOP Phase 5 Step 5.10. Merges and supersedes the prior "Milestone staging mirror" backlog item.

- **(2026-04-25) Local WordPress provisioning skill.** Build a skill that automates local WordPress instance setup. Detect whether Local by Flywheel is installed; use it as default. Fall back to `wp-env` or Docker with a standard `docker-compose.yml`. Output: running local WP site, admin credentials recorded in the PM doc, canonical project folder structure created. Confirmed by SOP Phase 5 Step 5.1, currently manual.

- **(2026-04-25) Dynamic menu provisioning.** Extend `wp-page-builder` (or `theme-scaffold`) to read the approved sitemap from Phase 2 and auto-create the primary menu in WordPress. Add menu items for every top-level page, configure sub-menus for service/location hierarchies, assign to Primary location. Confirmed by SOP Phase 5 Step 5.5, currently manual.

- **(2026-04-25) Tracking & analytics setup skill.** Single skill (or set) that handles GA4 + GTM + GSC + Yoast site-wide configuration on the local site before deploy. Should include sitemap submission to GSC, analytics event taxonomy alignment with the marketing hub's `ga-event-config`, and form-submission event tracking. Confirmed by SOP Phase 5 Step 5.9. Likely cross-plugin — may belong in marketing hub.

- **(2026-04-25) Forms configuration skill.** Set up + test contact forms during Step 5.9. Form-builder choice (CF7 vs Fluent Forms vs Gravity Forms) needs a decision before this can be built — pick one, build the skill against it. Submissions route to client's nominated email; end-to-end testing automated.

- **(2026-04-25) Image optimisation pass skill.** Compression, alt text, file naming for images uploaded during Step 5.8. Compression and filename can be automated; alt text needs human or vision-LLM pass. Could partial-automate then prompt user for the alt text portion.

### Phase 6 — QA & Go-Live

- **(2026-04-25) Go-live / DNS cutover skill.** Skill or set of playbooks that handles DNS cutover for SOP Phase 6 Step 6.2. DNS provider varies per client (Cloudflare, GoDaddy, registrar-direct) — needs per-provider playbook before automation is meaningful. Pre-launch checks (SSL, robots.txt, redirects), the cutover itself, and post-launch verification (forms, GA4 on live domain).

### Cross-cutting

- **(2026-04-25) AHPRA compliance check skill.** Currently inlined into Claude's writing pass. Worth pulling out as a standalone skill so Krystalyn or Jaimee can run it on any page or set of pages without re-reading SOP rules. Confirmed by SOP Steps 3.2, 3.3, 6.1 (three review gates).

- **(2026-04-25) Client review email/page generator.** Used at every approval gate (Phase 1 Steps 1.3/1.4, Phase 4 Step 4.5, Phase 5 Steps 5.7/5.10, Phase 6 Step 6.2). Generates the email body + the staged review URL + the specific questions for the client. Best home is probably the marketing hub since other workflows hit approval gates too.

- **(2026-04-25) Blog Content Production sub-workflow.** SOP mentions "Phase 6 Blog Content" running in parallel to Phase 5, but never defines it. Needs a scoping pass: which skills, where the briefs come from (Step 2.1 blog schedule), where posts are written, AHPRA review, publishing to live (after go-live or pre-launch), GMB social post generation tie-in (link to lhm-content-engine plugin which already does this).

- **(2026-04-25) Content guardrails expansion.** This rollout shipped minimal starter guardrails for marketing hub (`blog-post.md`, `page-copy.md`) and WordPress hub (`web-copy.md`). The GMB hub's existing four (service-page, category-page, location-page, supporting-content) are richer. Expand the marketing and WP hub guardrails with the same level of detail when the next long-form content task surfaces gaps.
