---
name: weekly-social-carousel
description: "Turn useful practice-owner conversations, recurring operational questions, Google Search or Ads changes, and practical AI developments into a prioritised editorial backlog and concise Local Health Marketing carousel packages. Use this when the user mentions 'weekly social carousel', 'Fathom conversations into posts', 'content idea backlog', 'carousel from meeting notes', 'Friday social content', or asks for an LHM HTML carousel preview. Do not use it for client-facing clinical social posts or automatic social publishing."
---

# Weekly Social Carousel

Create one reviewed LHM carousel package from a supplied topic or from the strongest safe idea found in a weekly source sweep. The skill prepares content and durable artefacts. It does not publish to social platforms.

## Required context

Before writing content:

1. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.
2. Read `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md`.
3. Read this skill's `LEARNED.md`.
4. For client-derived material, read `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`, resolve the canonical client record, and keep knowledge and work destinations distinct.
5. Read [editorial strategy](references/editorial-strategy.md) and [privacy rules](references/privacy-rules.md).
6. When creating the visual package, also read [carousel design system](references/carousel-design-system.md) and [input and output contract](references/input-output-contract.md).
7. When delivering to the LHM Social review site, read [LHM Social delivery](references/lhm-social-delivery.md).
8. For weekly or historical source sweeps, read [editorial backlog](references/editorial-backlog.md).

Never create a fallback client folder or store a material deliverable inside the plugin source tree.

## Modes

### Manual

Use when the user supplies a meeting, question, transcript excerpt, or topic. Preserve the meaning of a client question, but paraphrase it unless the user explicitly approves a quote.

### Weekly

Use when asked to review a date range, commonly the previous seven days.

1. Search the available Fathom meeting source for that period.
2. Review summaries and the relevant transcript passages, not titles alone.
3. Extract candidate questions, misconceptions, shortcuts, recurring problems, or decisions that another allied-health practice owner could learn from.
4. Apply the privacy gate before scoring. Discard unsafe candidates rather than attempting cosmetic anonymisation.
5. Add timely Search, Ads, or AI candidates only when they have a practical clinic-owner implication.
6. Add every safe, distinct candidate to the editorial backlog before selecting posts. Do not discard a strong idea merely because it was not chosen in the week it appeared.
7. Score backlog candidates using the editorial strategy, including audience frequency. Select the requested number from the full ready backlog, not only from that week's meetings.
8. Mark selected ideas in the backlog and keep unused ideas available for Michael's review. If too few candidates clear the quality floor, report the shortfall; do not manufacture filler.

### Historical backlog

Use when asked to recover older ideas or build an idea bank. Sweep the authorised date range in manageable batches, deduplicate recurring themes and update the same editorial backlog. A historical sweep prepares and scores ideas; it does not create carousels unless the request also authorises production.

## Research

- Use Last30Days selectively for a shortlisted trend, news, or AI candidate. Prefer a narrow query over a broad trending sweep. Follow the installed Last30Days skill rather than reimplementing it.
- Verify Google Search and Google Ads announcements against a current first-party Google source before presenting them as facts.
- Verify AI product capabilities against the vendor's current documentation or release notes.
- Treat engagement as evidence of audience interest, not proof that a claim is true.
- Record private source URLs, meeting timestamps, publication dates, and verification notes in the private source receipt.

## Create the carousel

1. Select one lane: `practice-question`, `practical-shortcut`, `search-ads-update`, or `ai-experiment`.
2. Write a 5-7 slide sequence. Each slide should communicate one idea and remain useful when skimmed on a phone.
3. Use the editorial pattern for the selected lane. Translate news into what changed, why it matters to a clinic, and what to do or watch.
4. Keep the first-slide hook short. Do not place paragraphs on the cover.
5. Use the typography cover unless the current test plan calls for an image cover. An image must add context and use a dark LHM overlay; generic AI or cyber imagery is not acceptable.
6. Build a caption that adds context instead of repeating every slide.
7. Keep public copy source-blind. Never say that a client asked, a clinic said, or the idea came from a meeting. Present the useful issue directly. Meeting provenance belongs only in private source records. A public source note is appropriate for a verified product or platform announcement, not for a meeting-derived idea.
8. Run the privacy check again on the final slide copy, caption, HTML, filenames, image metadata, public source note and backlog entry.
9. Create the input JSON described in the input and output contract.
10. Save the durable package under `<work_root>/weekly-social-carousel/YYYY-MM/YYYY-MM-DD-slug/` unless the verified destination has an established equivalent structure.
11. Run `node scripts/build-carousel.mjs <input.json> <output-directory>`.
12. Run `node scripts/render-carousel.mjs <output-directory>` when a compatible browser renderer is available. If PNG rendering is unavailable, preserve the verified HTML and return `needs_review` with the exact limitation.
13. Open or otherwise inspect `carousel-preview.png` when rendered. Also read back `manifest.json`, `caption.md`, and the HTML metadata before reporting completion.

Do not call image generation merely to decorate a cover. Use it only when the user wants a generated image and the concept is specific enough to add meaning.

## Quality gate

Reject or revise a package when any condition is true:

- A client, clinic, patient, staff member, location, metric, or private decision can be inferred without explicit permission.
- The post relies on a medical claim, exaggerated outcome, diagnostic statement, or testimonial-style claim that would breach allied-health advertising rules.
- The cover exceeds the copy limits or the slides read like a mini blog article.
- A news post lacks a current first-party verification source.
- An AI-tool post does not connect to bookings, content, administration, patient communication, reporting, or another concrete practice workflow.
- The design uses a copied HeyTony identity instead of the LHM system.
- The public copy mentions a client, meeting, transcript or private source context without explicit approval.
- A meeting-derived topic scores below 2 for audience frequency unless Michael explicitly selects it from the backlog.
- Required artefacts were not saved and read back.

## GitHub delivery

GitHub versioning is optional and separate from social publishing.

- Push only when the current request or scheduled workflow explicitly authorises repository writes and the private destination repository has been verified.
- Store a package under `YYYY/MM/YYYY-MM-DD-slug/`.
- Never publish the private source receipt through GitHub Pages or another public deployment.
- Use a dated content branch unless the verified repository workflow specifies another branch.
- Do not enable Pages, merge a branch, open a public preview, or publish to a social account without separate authorisation.
- After a push, verify the remote commit and return its URL. A local commit is not a published package.

### LHM Social review site

The governed LHM review destination is the private repository `lhmorg/lhm-social`. Its site builder owns the weekly-row layout, in-page slide navigation, caption copy control and slide ZIP. Do not recreate or manually edit that interface for each post.

When `github.mode` is `commit_push` and `github.repository` is `lhmorg/lhm-social`:

1. Follow [LHM Social delivery](references/lhm-social-delivery.md).
2. Save the canonical package under `content/YYYY/MM/YYYY-MM-DD-slug/` in the verified clone.
3. Add the protected-preview gate file only after the privacy, rendering and artefact checks pass.
4. Run the repository build and verify the weekly row, caption, slide ZIP and private-file exclusion.
5. Push only through the branch and workflow explicitly authorised by the structured input.

Approval for the protected review site is not approval to publish the post on Instagram, Facebook, LinkedIn or another social platform.

## Structured input

```json
{
  "mode": "manual | weekly",
  "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "topic": "optional manual-mode topic",
  "source_scope": {"fathom": true, "last30days": "selective"},
  "requested_post_count": 1,
  "backlog": {"mode": "none | update | historical", "path": "optional verified Markdown path"},
  "cover_style": "typography | image | auto",
  "work_root": "/verified/durable/destination",
  "github": {
    "mode": "none | prepare | commit_push",
    "repository": "optional owner/repo",
    "branch": "optional explicit branch",
    "protected_preview": true
  }
}
```

Ask only for a missing value that changes the result materially. In weekly automation, `period`, `work_root`, and any authorised GitHub destination must already be explicit.

## Structured output

Return one JSON object:

```json
{
  "run_result": "completed | needs_review | no_publishable_topic | blocked",
  "work_state": "prepared | verified | pushed",
  "artefact_state": "verified | partial | not_required",
  "content_lane": "practice-question | practical-shortcut | search-ads-update | ai-experiment | null",
  "topic": "selected topic or null",
  "privacy_review": {"status": "passed | failed", "notes": []},
  "research_review": {"status": "verified | not_required | partial", "notes": []},
  "artefacts": [
    {"type": "html | preview | slide | caption | manifest | private_source_receipt", "path_or_url": "...", "verified": true}
  ],
  "github": {"state": "not_requested | prepared | pushed | blocked", "commit_url": null},
  "review_site": {
    "state": "not_requested | built | pushed | blocked",
    "week_label": null,
    "slide_zip_verified": false,
    "private_files_excluded": false
  },
  "editorial_backlog": {
    "state": "not_requested | updated | blocked",
    "path": null,
    "safe_candidates_added": 0,
    "ready_count": 0,
    "selected_ids": []
  },
  "approval_required": ["human review before social publishing"],
  "next_owner": "Michael",
  "next_action": "Review the carousel package"
}
```

Use `completed` only when the required package has been saved and verified. Social publication always remains a separate approval.
