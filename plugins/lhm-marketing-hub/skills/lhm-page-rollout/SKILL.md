---
name: lhm-page-rollout
description: Build LHM website pages end to end (research, brief, copy, FAQ and schema, internal links, images, build, staging push, verification, review email). Use this when the user mentions 'page rollout', 'build the pages', 'SEO pages', 'AHPRA pages', 'modality pages', 'stage the pages', 'staging review', 'rollout batch', or asks to build and publish website pages to staging for review. Stages to the staging branch only; merging to main needs the user's explicit say-so in chat.
---

# LHM page rollout

Goal: finished, linked, verified pages on the staging branch, then one review email. the user reviews the staging links and decides on merge to main.

## Guardrails (read first)

- Staging only. Push to `rollout/phase-2-2026-10` (or the next month's `rollout/phase-<n>-<yyyy-mm>`). Never merge to `main` or publish to production unless the user says so in chat for that merge.
- Approval gates are waived for staging work inside this rollout. Do not stop to ask for approval on research, briefs, copy, FAQs, links, images, builds or pushes. Make the call, record it in the email.
- No `[Needs human input]` markers or visible gap notes on any page. Use the brief's fallback wording. Open questions go in the email as recommendations.
- LHM is a digital marketing agency that works with allied health practices. LHM's own copy carries no AHPRA or NDIS compliance framing. AHPRA guides explain the rules to clinics and must be accurate about them.
- No invented proof, client results, testimonials, statistics, pricing figures, CPCs or offers.
- No em dashes or en dashes in customer copy. No "Needs human input". Every URL unslashed (`trailingSlash: never`).
- Do not use Google Drive as a handoff. Work from the repo, the scratchpad and the local rollout folder. Drive writes and Drive hash checks have stalled runs before.

## Repo facts

- Repo: the Astro site repo `local-health-marketing-astro` on the machine running the routine
- Page content: `src/content/seo/<slug>.md`
- Page registry: `src/data/remainingPages.ts`. `remainingServicePages` gives `Service` schema (SEO service pages). `standalonePages` gives `WebPage` (AHPRA guides, resources). Do not put a slug in two lists.
- Page renderer: `src/pages/[slug].astro`. Its FAQ schema comes from `src/lib/seoContent.ts` (`extractFaqSchema`).
- Hub and nav: `src/content/seo/seo.md` (SEO hub, "Modalities We Serve"), `src/content/seo/ahpra-compliance.md` (AHPRA hub).
- Build: `npm run build` runs the internal-link check (`scripts/check-internal-links.mjs`). It must pass.
- Local research folder (synced from Drive): the LHM rollout folder (the `LHM Website SEO Growth Rollout` folder in the LHM Knowledge shared drive, synced to the local machine running the routine). Keyword research files are `<modality>-seo-keyword-research-v1.md`. Read them from here, not from Drive.
- Working scratch: `/private/tmp/claude-501/<session>/scratchpad/` with `pages/` and `briefs/`. Writers put files here first.

## Stage 0: decide the batch

1. Read `rollout-state.md` (LHM Knowledge rollout folder) for the phase, the open decisions and the last run.
2. Read the page list for the batch. Keep the batch to what the user has asked for. Do not add pages outside it.
3. For each page, check the slug is not already in `src/content/seo/` or `remainingPages.ts`. If it is, update it rather than duplicate it.

## Stage 1: research (SEO pages only)

- Use `lhm-marketing-hub:seo` (or `keyword-research`). One research file per page, method from `dentist-seo-keyword-research-v3.md`.
- Verify volumes live. Mark any figure you cannot verify. Do not carry plan figures forward unverified.
- Record currency. If the tool returns a bare "$", mark CPC as "currency unconfirmed" and keep CPCs out of the page.
- Run the cannibalisation check against `/seo`, the `-marketing` page and the `-web-design` page.
- Research QA is a light self-check, not a gate: source table, labelled live or saved figures, arithmetic, zero-volume terms excluded.

## Stage 2: brief

- Adapt `physiotherapy-seo-page-brief-v1.md` or `dentist-seo-page-brief-v1.md`. Do not start a brief from scratch.
- Include: one conversion goal (`/strategy-call`), primary and secondary queries, outline, confirmed internal links only, and open questions for the email.
- Brief length is not the goal. Clarity is.

## Stage 3: copy (parallel)

- Run one copywriter agent per page in parallel (`lhm-marketing-hub:content`). Each writes `pages/<slug>.md` and `briefs/<slug>-brief.md` to the scratchpad. Writers do not touch the repo.
- Word counts: SEO service pages 900 to 1,300 body words. AHPRA guides 1,000 to 1,400.
- Each page file starts with frontmatter matching `src/content/seo/ahpra-prohibited-claims.md`: `title`, `seo_title`, `meta_description` (155 characters or fewer), `slug` (with leading slash), `template`, `status: published`, `primary_keyword`, `schema_type`.
- Self-check each file: zero em or en dashes, zero "Needs human input", only allowed links, word count in range.
- Independent QA: run one `lhm-marketing-hub:content` agent per page in a fresh context to check for invented claims, positioning errors (LHM is an agency, not a health provider), unsupported figures and filler. Apply the corrections it lists. One correction pass only, then build.

## Stage 4: FAQ and schema

- Every page with an FAQ must use exactly this format, or the accordion and FAQPage schema will not render:
  - `## Frequently Asked Questions`
  - `<!-- component: accordion -->` on the next line
  - a blank line
  - each `**Question?**` followed immediately by its answer on the next line, with no blank line between them
- Use three questions per page, answers grounded only in the page's own text. Do not add facts.
- Page type: SEO service pages go in `remainingServicePages` so they get `Service` schema. AHPRA guides and resources go in `standalonePages` (`WebPage`).
- Check the built HTML: `dist/<slug>.html` must contain `class="faq-item"` and `FAQPage`.

## Stage 5: internal links (the part that gets pages indexed)

Every new page must have all of these:
1. **Up link:** the page is linked from its parent hub. SEO pages: the `/seo` "Modalities We Serve" list links `/<modality>-seo` (replace the `-marketing` link for that modality, do not add a second link).
2. **Modality link:** the `-marketing` page's "Once Your Site Is Live" SEO tile links to `/<modality>-seo`.
3. **Sideways:** AHPRA guides list every other AHPRA guide as a card (the `ahpra-checklist` format). The AHPRA hub `ahpra-compliance.md` lists all nine.
4. **Own links only:** every link goes to a file in `src/content/seo/`, a slug in `remainingPages.ts`, or one of the confirmed routes (`/strategy-call`, `/seo`, `/google-ads`, `/web-design`, `/google-ads-audit`, `/seo-audit`, `/free-homepage-mockup`, `/how-we-work`). Check each one before committing.
5. **Do not add** extra SEO links anywhere beyond the list and tile replacements. the user asked for replacement, not addition.
6. Nav and footer are not changed in a rollout unless the user asks.

## Stage 6: images

- Every card needs an image. Look in `public/images/` for a fitting existing image first and reuse it. Record it.
- If generation is needed, try the image tool once. If the model is unavailable, reuse the closest existing image and list it in the email as a weak fit.
- Never use images with real identifiable people or third-party logos.

## Stage 7: integrate and build (one agent, once)

1. Copy each page into `src/content/seo/<slug>.md`. Register it in `src/data/remainingPages.ts` (the correct list from Stage 4). Mirror the existing entry format.
2. Add the up links and tile replacements from Stage 5.
3. `npm run build`. Must pass. Confirm each new page is in `dist/` and has the right `faq-item` count.
4. One commit, message listing the pages, ending with `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`.
5. `git push origin <staging-branch>`. Do not merge to main.

## Stage 8: verify after the deploy (do not skip)

- Wait for the Cloudflare Pages check run on the new commit to be `completed` with `success`:
  `gh api repos/michaellhm/local-health-marketing-astro/commits/<sha>/check-runs`
- Only then curl every new URL on `https://<branch>.local-health-marketing-astro.pages.dev/<slug>`. A 404 before the deploy finishes is not a bug.
- Confirm: 200 status, `faq-item` present where expected, every card image URL returns 200, the parent links resolve.
- If a URL still fails after the deploy completes, fix it and re-push. Do not email a broken link.

## Stage 9: review email

- Send via Gmail (`mcp__649fe5e9...__send_message`) to michael@localhealthmarketing.com.au. Gmail has been reliable; the Mailgun connector returned 403 in October.
- Use `htmlBody` with explicit `<a href>` links for every staging URL. Plain-text URLs get wrapped by Gmail's redirect, so do not send them as plain text.
- Body: the staging links grouped by SEO and AHPRA, a short "what's done" list, and the recommendations for open decisions (one line each). Plain English, no em dashes, no jargon.
- State clearly: staging only, nothing merged to main, and what still needs QA or verification.
- Do not wait for a reply before doing the next page. the user's decisions get folded into the next run.

## Stage 10: state

- Append a run entry to `rollout-state.md` between the RUN LOG markers: pages built, branch, commit SHA, staging URLs, decisions left open, and anything that did not pass.

## Known pitfalls (from the October 2026 run)

- The Drive connector cannot overwrite file content. Do not hand off to Drive. Keep the artefact in the repo or scratchpad.
- A background agent stopped when the session restarted. Check the repo state before rerunning, and rerun the whole step rather than assuming it landed.
- A dispatch that blocks on a hash check or a Drive sync stalls the whole run. Verify with a local hash and the deploy result instead.
- Writers ran the OpenRouter multi-model passes themselves when that tool was unavailable. Say so in the email. Do not count it as a full pass.
- Image generation failed with a model-not-found error. Check it once, then fall back to existing images and flag them.
- Modality pages registered as `standalonePages` render the wrong hero. SEO service pages belong in `remainingServicePages`.
- The `/seo` page once got an extra duplicate link. Check the diff for added links, not only changed ones.
