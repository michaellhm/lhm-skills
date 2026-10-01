---
name: weekly-social-carousel
description: "Turn useful clinic-owner conversations, recurring operational questions, Google Search or Ads changes, and practical AI developments into concise Local Health Marketing carousel packages. Use this when the user mentions 'weekly social carousel', 'Fathom conversations into posts', 'client questions into content', 'carousel from meeting notes', 'Friday social content', or asks for an LHM HTML carousel preview. Do not use it for client-facing clinical social posts or automatic social publishing."
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
6. Score the safe candidates using the editorial strategy and select one. If nothing clears the quality floor, return `no_publishable_topic`; do not manufacture a post.

## Research

- Use Last30Days selectively for a shortlisted trend, news, or AI candidate. Prefer a narrow query over a broad trending sweep. Follow the installed Last30Days skill rather than reimplementing it.
- Verify Google Search and Google Ads announcements against a current first-party Google source before presenting them as facts.
- Verify AI product capabilities against the vendor's current documentation or release notes.
- Treat engagement as evidence of audience interest, not proof that a claim is true.
- Record private source URLs, meeting timestamps, publication dates, and verification notes in the private source receipt.

## Create the carousel

1. Select one lane: `client-question`, `practical-shortcut`, `search-ads-update`, or `ai-experiment`.
2. Write a 5-7 slide sequence. Each slide should communicate one idea and remain useful when skimmed on a phone.
3. Use the editorial pattern for the selected lane. Translate news into what changed, why it matters to a clinic, and what to do or watch.
4. Keep the first-slide hook short. Do not place paragraphs on the cover.
5. Use the typography cover unless the current test plan calls for an image cover. An image must add context and use a dark LHM overlay; generic AI or cyber imagery is not acceptable.
6. Build a caption that adds context instead of repeating every slide.
7. Run the privacy check again on the final slide copy, caption, HTML, filenames, image metadata, and public source note.
8. Create the input JSON described in the input and output contract.
9. Save the durable package under `<work_root>/weekly-social-carousel/YYYY-MM/YYYY-MM-DD-slug/` unless the verified destination has an established equivalent structure.
10. Run `node scripts/build-carousel.mjs <input.json> <output-directory>`.
11. Run `node scripts/render-carousel.mjs <output-directory>` when a compatible browser renderer is available. If PNG rendering is unavailable, preserve the verified HTML and return `needs_review` with the exact limitation.
12. Open or otherwise inspect `carousel-preview.png` when rendered. Also read back `manifest.json`, `caption.md`, and the HTML metadata before reporting completion.

Do not call image generation merely to decorate a cover. Use it only when the user wants a generated image and the concept is specific enough to add meaning.

## Quality gate

Reject or revise a package when any condition is true:

- A client, clinic, patient, staff member, location, metric, or private decision can be inferred without explicit permission.
- The post relies on a medical claim, exaggerated outcome, diagnostic statement, or testimonial-style claim that would breach allied-health advertising rules.
- The cover exceeds the copy limits or the slides read like a mini blog article.
- A news post lacks a current first-party verification source.
- An AI-tool post does not connect to bookings, content, administration, patient communication, reporting, or another concrete practice workflow.
- The design uses a copied HeyTony identity instead of the LHM system.
- Required artefacts were not saved and read back.

## GitHub delivery

GitHub versioning is optional and separate from social publishing.

- Push only when the current request or scheduled workflow explicitly authorises repository writes and the private destination repository has been verified.
- Store a package under `YYYY/MM/YYYY-MM-DD-slug/`.
- Never publish the private source receipt through GitHub Pages or another public deployment.
- Use a dated content branch unless the verified repository workflow specifies another branch.
- Do not enable Pages, merge a branch, open a public preview, or publish to a social account without separate authorisation.
- After a push, verify the remote commit and return its URL. A local commit is not a published package.

## Structured input

```json
{
  "mode": "manual | weekly",
  "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "topic": "optional manual-mode topic",
  "source_scope": {"fathom": true, "last30days": "selective"},
  "cover_style": "typography | image | auto",
  "work_root": "/verified/durable/destination",
  "github": {"mode": "none | prepare | commit_push", "repository": "optional owner/repo"}
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
  "content_lane": "client-question | practical-shortcut | search-ads-update | ai-experiment | null",
  "topic": "selected topic or null",
  "privacy_review": {"status": "passed | failed", "notes": []},
  "research_review": {"status": "verified | not_required | partial", "notes": []},
  "artefacts": [
    {"type": "html | preview | slide | caption | manifest | private_source_receipt", "path_or_url": "...", "verified": true}
  ],
  "github": {"state": "not_requested | prepared | pushed | blocked", "commit_url": null},
  "approval_required": ["human review before social publishing"],
  "next_owner": "Michael",
  "next_action": "Review the carousel package"
}
```

Use `completed` only when the required package has been saved and verified. Social publication always remains a separate approval.
