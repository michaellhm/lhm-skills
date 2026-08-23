---
name: seo-page-brief
description: Create bounded implementation-ready SEO page briefs from accepted upstream keyword, intent and business evidence. Use after research has passed SEO Lead acceptance, when planning one page or an explicitly scoped page batch, or when an SEO content writer needs an approved brief before writing.
---

# SEO Page Brief

Create page briefs only. Do not perform new keyword research, write finished page copy, implement code or choose the next production action.

Read and follow the plugin-wide context, delivery artefact, anti-AI writing and SEO departmental delivery contracts. Read `${CLAUDE_PLUGIN_ROOT}/learnings/seo-learned.md`.

## Inputs

Require:

- parent, action and action-version IDs;
- parent goal, department goal and bounded objective;
- accepted keyword and intent evidence with verified references;
- approved page scope and known existing-page overlap;
- target audience, geography, offer and brand context;
- confirmed internal URLs or explicit unknowns;
- exact Drive folder ID, relative path and output filename;
- permission ceiling and completion test.

Return `needs_context` rather than inventing missing business facts, keyword metrics, URLs, claims or destinations. Do not silently expand the page set.

## Produce the brief

For each approved page, include:

- proposed route and page purpose;
- primary query theme, supporting terms and observed search intent;
- target audience and stage of awareness;
- relationship to existing pages, including cannibalisation risks;
- angle, value proposition and evidence boundaries;
- recommended title, H1, meta direction and heading outline;
- section-by-section purpose and required facts;
- confirmed internal links and recommended anchor context;
- external evidence requirements where relevant;
- CTA goal and any approval-dependent claims;
- FAQ opportunities only when supported by search or customer evidence;
- schema, media or implementation notes when justified;
- writer acceptance criteria.

Keep research claims traceable to the accepted evidence. Professional judgement is welcome, but label assumptions and do not fabricate volume or difficulty values.

## Save and verify

Save the submitted brief to the exact registered Google Drive parent and relative path. Read back its name, parent and content or metadata, then return the observed file ID and URL. Do not claim completion from a temporary local file.

## Handback

Use `seo_worker_handback` from the departmental contract. Set `next_owner: SEO Delivery QA`. Include the accepted source references, limitations, exact pages covered, Drive parent readback and whether any business or regulated claim requires human approval.
