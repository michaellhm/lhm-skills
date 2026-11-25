---
name: content-rollout
description: Run a client Astro website's page content in rounds, from sitemap SEO and a chosen template page through briefs, 8-pass copy, independent anti-AI editing, healthcare advertising review, integration into site/, deploy verification, the client review checklist and the client email draft. Use this when the user mentions 'content rollout', 'content round', 'write the next pages', 'roll out the service pages', 'client copy review', 'content approval tracker', 'copy this page template', 'write a section using sitemap keywords', 'page rollout' or 'stage the pages for client review'.
---

# Content Rollout

Run a client website's content programme in rounds, with persistent page status. Discover the client's implementation instead of assuming paths. Follow the user's requested mode and scope: setup does not start writing pages automatically.

## Where things live

- **Client repo** (made by `client-repo-setup`): `README.md`, `brain/`, `skills/` and `site/`. The Astro project is in `site/`. The client-facing checklist is `brain/Project.md`, rendered by `review_release.py`. Nothing internal goes in this repo.
- **Registered client work root** (see [client routing](../../references/obsidian-context-contract.md)): the internal state files. `project.md`, `content-plan.json` and `content-plan.md`, `action-plan.md`, `templates/<family>.md` and `pages/<page-key>/`. Never commit these to the client repo or `site/public/`.
- **The brain**: `brain/Overview.md`, `brain/Profile.md`, `brain/Content Rules.md` and, as needed, `brain/Services.md`, `brain/Staff.md`, `brain/What We Do.md`, `brain/Who We Serve.md` and `brain/Brand.md`. `brain/Content Rules.md` replaces the old `how-to-write.md` and `client-learnings.md`. Every rule in it is mandatory, and the brain is the voice source.
- **Internal vault project file**: the client's project file in the internal vault, where the round's handback is recorded at the end. Executable tasks stay with the task owner; do not mark the website complete from a finished round.

Read the [project state](references/project-state.md) before writing. Initialise missing records without overwriting existing feedback. Inventory every sitemap destination, deduplicate shared routes and separate existing pages, missing pages and updates. Existing content is not evidence of client approval; record unknown approval as unknown. Preserve unrelated local edits and the user's approved work.

## Step 0: refresh the brain if the client has changed things

Before writing, check whether the client has committed since the brain last learned. Read the cursor:

```sh
python3 ${CLAUDE_PLUGIN_ROOT}/skills/update-content-brain/scripts/brain_cursor.py "CLIENT_REPO/brain/Change Log.md"
```

If client commits exist past the `<!-- last-processed: <sha> -->` marker, run `update-content-brain` first, get its proposal approved and let it update `brain/Content Rules.md` before any brief is written. Do not treat LHM's own commits as voice changes. Then read `brain/Overview.md`, `brain/Profile.md` and `brain/Content Rules.md`. Record each note's revision and the applicable rule IDs in every brief, editor and reviewer handoff. Confirmed rules apply at their recorded scope, observed patterns guide phrasing, proposed rules stay labelled, and service-specific facts must not spread across pages. A rule never overrides the selected template, the sitemap, verified facts or healthcare review.

**Brain gaps.** If the brain lacks a fact the page needs, use the brief's fallback wording (truthful, bounded copy or defer the section) and add the question to the client email. Never invent staff, credentials, prices, results or availability, and never leave a visible placeholder on a page.

## The round flow

1. **Scope and template.** Ask which pages this round covers and which template. A template is a prototype page, for example a service overview or condition page. Before research, briefing, writing or integration, ask: **"Which existing page should I copy as the template for this section? Please send its URL."** If the user already gave an explicit template for this scope, acknowledge and reuse it. A menu grouping or a page you discovered yourself is not a selection. Different sections may have different templates; ask again for a section with none. While awaiting the answer, only independent discovery and page inventory continue.
2. **Check the sitemap fields.** Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/astro-sitemap/scripts/page_brief_seed.py sitemap.json --check` for those pages. Any page missing a primary keyword, audience or intent is reported by name; fix the gaps (with the user) before any brief is seeded. Never fill them silently.
3. **Propose the round.** Show N pages, in order, with the template for each, and the SEO mapping per page (see below). Get a yes.
4. **Mock-up or batch.** Ask: "Would you like me to make the first page as a mock-up for you to approve, or batch the lot?" A mock-up means one page goes all the way through to a deployed preview and waits for approval before the rest. Default to one page at a time unless the user chooses the batch.
5. **For each page, through `agents/content.md`:** seed (`page_brief_seed.py` with the page name) then brief (`seo-page-brief`) then write (8-pass, `seo-content-writer`, or `copywriting` for non-search copy) then `content-quality-auditor` then integrate into `site/` then `npm run build` then push to `main` then wait for a successful Cloudflare deploy then curl each URL for 200. The detail of each stage is below.
6. **Release for client review.** Run `review_release.py scan`, show the proposal and get approval, then run `apply` with release id `round-<n>`. This updates `brain/Project.md`, grouped by `## Round round-<n>`. Use the commands in `client-review-release` and do not hand-edit `brain/Project.md`.
7. **Draft the client email** with `client-update-email` and the invitation text in the `client-review-release` skill, `references/client-invitation.md`. It includes the preview links, the brain questions from any gaps, and the copyable prompt to run `review-website`. Draft only. Send only on the user's explicit approval, as an HTML email with real links (plain-text URLs get wrapped by mail redirects).
8. **Update the internal vault project file** with the round's pages, SHAs, URLs, open questions and next round, and update `action-plan.md` with the resume instruction.

Publishing during staging means pushing to `main`; there are no round or review branches. Production deploy is a separate approval stop. Do not infer permission to deploy production from a request to write copy.

## Template contract

Inspect the selected URL's rendered desktop and mobile page and its source components. Record its URL, inspected revision and date, applicable pages and source files in `templates/<family>.md` (work root). Capture the ordered sections, form position, card counts and grids, spacing, backgrounds, media, FAQs, clinic cards, CTA placement, booking destination and responsive behaviour. Copy that structure across the selected pages, adapting subject wording and verified facts. Do not replace it with a generic outline or silently drop or reorder modules. Reuse the existing renderer and components. If a module is clinically inappropriate or unsupported, propose the specific exception and get the user's decision before producing it. Never copy an unsupported claim merely to match the template. Template changes to approved pages need explicit revision scope.

## Take SEO from the agreed sitemap

The agreed sitemap and its accepted keyword research are the SEO authority, not the template page's keyword or a fresh invented service and location combination. `page_brief_seed.py` returns, for each page, the page, slug, primary keyword, secondary keywords, audience, intent, H1, template and section. Save that mapping, with the sitemap path and version, in the brief and tracker.

Use the mapped primary keyword as the one visible H1 (capitalisation may follow the site's style). Secondary keywords, abbreviations and locations appear naturally in the eyebrow, supporting copy and metadata; do not stuff every location into the H1. Derive title and description from the same mapping and page facts. The template controls layout; the page's sitemap mapping controls its SEO wording. If the sitemap row is missing, duplicated or conflicting, name the exact row, ask which mapping to use, and hold that page's brief, copy and integration. Do not invent keyword research or overwrite the sitemap.

## Orchestrate each page

Read [agent handoffs](references/agent-handoffs.md). Use separate subagents for research and comparison, brief, copy, anti-AI edit, healthcare review and integration when delegation is available. Writers and reviewers produce artifacts, not concurrent website edits. One integration agent owns repo changes. Keep each page's dependent stages sequential and parallelise independent pages only within capacity. If delegation is unavailable, perform the stages separately and say independent review was not performed. Never describe sequential self-review as independent review.

Save per-page outputs under `pages/<page-key>/` in the work root: `research.md`, `brief.md`, `copy.md`, `editor-review.md`, `compliance-review.md`, `integration.md`. Update state after each stage. Send each agent the template contract, source pack, sitemap row, the brain's Content Rules and the current artifact rather than relying on conversation history.

1. Compare the current live page, existing new-site copy and the brain's positioning. Verify live pages instead of trusting saved URLs. Record retain, change and remove decisions with sources, gaps and conflicts.
2. Produce the brief with `seo-page-brief` from the template contract: the selected template, a section-by-section component map, sitemap row, primary keyword and exact H1, goal, intent, outline, substantiated facts, permitted claims, media and practitioner mapping and confirmed links.
3. Write from the accepted brief with `seo-content-writer` through the 8-pass engine ([8-pass writing engine](../../references/8-pass-writing-engine.md), [anti-AI guidelines](../../references/anti-ai-writing-guidelines.json)). Australian English, no em or en dashes, no invented credentials, locations, availability, testimonials, prices, evidence or outcomes.
4. A fresh editor applies the writing guidelines and `brain/Content Rules.md` while preserving factual meaning, and returns edits with rationale. No formulaic word count or identical prose across pages.
5. For healthcare advertising, a separate reviewer verifies current official AHPRA and National Board guidance and relevant evidence: titles and credentials, clinical testimonials, misleading claims, unreasonable outcome expectations, unnecessary treatment encouragement. "May help" does not substantiate a claim. Apply profession-specific rules; do not imply every allied-health profession is AHPRA-registered. Return issues, sources and a publishability status, not a legal certification. Run `content-quality-auditor` on the exact copy version as the independent editorial QA.
6. Return failures to the writer, then recheck changed text. Do not integrate unresolved material claims. After two unsuccessful correction cycles, document the blocker and continue unaffected pages.
7. Integrate passing copy into `site/` using the existing Astro renderer and content schema, current booking routes and URL conventions. Use real, verified practitioner media only; never infer a practitioner treats a condition from a video title; no fake play button.
8. `npm run build` from `site/` and run the relevant existing checks. Inspect desktop and mobile rendering, images, headings, internal links and booking navigation. Compare section order, forms, card counts, spacing, grids and CTA placement against the template, including sparse and single-card layouts. Verify exactly one visible H1 matching the primary keyword, and metadata and schema against the same mapping. Unresolved drift is a failed technical review.

## FAQ format

Every page with an FAQ uses exactly this, or the accordion and FAQPage schema will not render:

- `## Frequently Asked Questions`
- `<!-- component: accordion -->` on the next line
- a blank line
- each `**Question?**` followed immediately by its answer on the next line, with no blank line between them

Use the number of questions the template has, with answers grounded only in the page's own text. Add no facts. Confirm the built HTML contains the accordion items and `FAQPage` schema. If the site's own FAQ component differs, copy the template page's format and keep the same checks.

## Internal links

Every new page needs all of these:

1. **Up link:** linked from its parent hub or listing. Replace an older link to the same destination; do not add a second.
2. **Sideways:** listed with its sibling pages wherever the template lists siblings (cards, related services).
3. **Own links only:** every link goes to a page that exists in `site/` or is in this round, or to a confirmed route (booking, contact, hubs). Check each before committing.
4. **Do not add** extra links beyond the hub entries and replacements the round needs. Check the diff for added links, not only changed ones.
5. Navigation and footer change only when the user asks.

`npm run build` must pass, including any internal-link check the site has.

## Images

Every card needs an image. Look in the site's existing image folders for a fitting image first and reuse it, recording each one. If generation is needed, try the image tool once; if it is unavailable, reuse the closest existing image and list it in the email as a weak fit. Never use images of real identifiable people unless verified practitioner media, and never third-party logos.

## Publish and verify after the deploy (do not skip)

1. One commit per page or batch, message listing the pages. Push to `main`.
2. Wait for the Cloudflare Pages deploy for that commit to complete with success (for example via the commit's check runs with `gh api`, or the Pages dashboard). A 404 before the deploy finishes is not a bug.
3. Only then curl every new URL on the preview domain. Confirm 200, the expected FAQ items, every card image URL returning 200, and the parent links resolving.
4. If a URL still fails after a successful deploy, fix it and push again. Never email a broken link. Report queued or failed deploys accurately and verify the remote SHA.

A checked draft is not client approved. Publication to the staging preview is allowed before client approval when the user has asked for it, while client status stays pending.

## Client review and learning

Read [project state](references/project-state.md) for approval semantics. The client reviews through `review-website` in their repo; their edits and feedback come back as commits, and `update-content-brain` learns from them into `brain/Content Rules.md`. Learning mode never starts a content round. Capture general preferences separately from page-specific factual corrections. Client approval of wording does not override compliance findings. Changed reviewed content invalidates approval.

Keep private records out of public assets and route generation. This skill does not provision a client portal or authentication.

## Complete or resume

Read the tracker and artifacts before resuming, and verify repo and deployment state instead of assuming earlier agent output landed. Report drafts, client approvals, integrated pages and deployed pages separately. For a new chat, hand off the work-root record paths and the next task.

## Return the round to project coordination

Return exact page revisions and preview URLs, the draft, checked, client-approved, integrated and deployed state of each, verified checks, brain gaps raised, blockers, the next round and the next review owner. Save durable decisions in the internal vault under the routing contract. Do not mark the website complete from a finished round or send client messages without authority.

## Known pitfalls

- A background agent stopped when the session restarted. Check repo state before rerunning, and rerun the whole step rather than assuming it landed.
- A dispatch that blocks on a hash check or a file-sync stalls the whole run. Verify with a local hash and the deploy result instead.
- Writers sometimes run the multi-model passes themselves when that tool is unavailable. Say so in the email and do not count it as a full pass.
- Image generation can fail with a model-not-found error. Check once, then fall back to existing images and flag them.
- Registering a page in the wrong list or collection can render the wrong hero or schema. Copy the template page's registration.
- Duplicate links creep in. Check the diff for added links.
- A page URL must follow the site's trailing-slash setting everywhere, in links, canonical and sitemap.
