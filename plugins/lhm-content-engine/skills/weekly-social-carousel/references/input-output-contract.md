# Carousel input and output contract

## Build command

```bash
node scripts/build-carousel.mjs /absolute/path/carousel-input.json /absolute/path/output-directory
node scripts/render-carousel.mjs /absolute/path/output-directory
node scripts/build-story.mjs /absolute/path/story-input.json /absolute/path/output-directory
node scripts/render-story.mjs /absolute/path/output-directory
```

The build step uses only Node standard-library modules. It writes a portable HTML preview even when browser rendering is unavailable.

## Input JSON

```json
{
  "schema_version": "1.0",
  "slug": "ai-and-clinic-seo",
  "title": "AI and clinic SEO",
  "lane": "quick-win-sop",
  "cover_style": "typography",
  "cover_image": null,
  "brand": {
    "name": "Local Health Marketing",
    "website": "localhealthmarketing.com"
  },
  "slides": [
    {
      "type": "cover",
      "kicker": "A common practice question",
      "eyebrow": "The AI question",
      "headline_segments": [
        {"text": "Where are ", "tone": "default"},
        {"text": "websites and SEO", "tone": "accent"},
        {"text": " heading now that patients use AI?", "tone": "default"}
      ]
    },
    {
      "type": "statement",
      "kicker": "The short answer",
      "headline": "AI can only recommend a clinic it can understand.",
      "body": "Your website needs to explain who you help and why you are the right fit.",
      "image": "/optional/local/interface-visual.png",
      "image_alt": "Neutral interface visual showing the relevant control",
      "image_caption": "Illustrative view. Menus may vary by account."
    },
    {
      "type": "labels",
      "kicker": "The problem",
      "headline": "Most clinic websites are too generic.",
      "items": ["Physio.", "Osteo.", "Massage."]
    },
    {
      "type": "checklist",
      "kicker": "What AI needs",
      "headline": "AI needs to understand:",
      "items": ["Who you help", "What you treat", "How you work", "What makes you different"]
    },
    {
      "type": "callout",
      "kicker": "The takeaway",
      "headline": "Your website is not just trying to rank.",
      "body": "It is teaching AI when your clinic is the right answer.",
      "callout": "Would AI know when to recommend you?"
    }
  ],
  "caption": "Caption copy in Markdown.",
  "first_comment": "Optional first comment for the LHM account.",
  "public_source_note": "Inspired by a recurring clinic-owner question.",
  "private_sources": [
    {"type": "fathom", "url": "https://...", "timestamp_seconds": 515, "note": "Question paraphrased."}
  ]
}
```

`headline_segments` supports tones `default`, `accent`, and `blue`. Use it only when meaningful emphasis improves the hook. `headline` is the simpler default.

Allowed slide types: `cover`, `statement`, `labels`, `checklist`, and `callout`. The first slide must be `cover`. Supply 5-7 slides. Public copy must not identify the private source or say that a client or meeting supplied the idea. Use `practice-question` for meeting-derived audience questions.

For `cover_style: image`, `cover_image` must be an existing local PNG, JPEG, or WebP file. The build script copies it into the output directory and never embeds the original path in public HTML.

Any slide may optionally supply `image`, `image_alt`, and `image_caption`. The image must be an existing local PNG, JPEG, or WebP file. The builder copies it into the package as `slide-visual-XX.ext`; no original path is exposed. Use a real first-party interface capture only when it contains no private account data. Otherwise use a clearly labelled neutral interface visual. `image_alt` is required whenever `image` is supplied.

`public_source_note` is retained for compatibility but is stored only in `source-receipt.private.json`. It is never appended to `caption.md`. Captions should contain only publishable post copy, CTA and hashtags.

## Output package

```text
output-directory/
  carousel.html
  caption.md
  first-comment.md                 # when first_comment is supplied
  manifest.json
  source-receipt.private.json
  cover-image.ext                 # image variant only
  slide-visual-XX.ext             # optional internal-slide visuals
  slide-01.png ... slide-N.png    # after render
  carousel-preview.png            # after render
```

The private source receipt is not a public asset. Exclude `*.private.json` from Pages, public websites, social uploads, and client-facing exports.

`manifest.json` records the lane, `content_format: feed-post`, lane-derived accent, cover style, slide count, generated files, and verification state. Orange identifies quick-win SOPs, soft blue identifies question-led content, and seafoam identifies rotating opportunities. Read it back after both build and render.

## Story input and output

The Story builder accepts one queue item containing `id`, `title`, `category`, two to six `frames`, and an optional `interaction` object with `type`, `prompt` and `options`. It writes `story.html`, `story-manifest.json`, `story-01.png ... story-N.png`, and `story-preview.png`. `story-manifest.json` records the ordered upload frames in `export_files`; the Story ZIP must contain exactly those files. The final rendered frame reserves a labelled placement area for Nina to add the native Instagram sticker after upload.
