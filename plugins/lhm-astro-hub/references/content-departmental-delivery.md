---
title: Content Departmental Delivery Contract
description: The governed brief, writing, editorial QA and implementation handoff for all customer-facing LHM copy.
---

# Content Departmental Delivery Contract

Use this contract whenever approved work creates or materially changes customer-facing words. The Content Department owns final copy. SEO, Google Ads, CRO, GMB and other channel specialists own diagnosis, evidence and channel requirements. Developers and publishers implement accepted copy but do not rewrite it.

## Non-negotiable content gate

`Channel diagnosis -> accepted content brief -> Content Lead -> writing skill -> editorial QA -> verified copy artefact -> implementation`

- Recommendations, candidate wording and audit examples are not implementation-ready copy.
- A developer must receive an accepted `implementation_ready_copy` artefact, never an audit report or an unselected set of variants.
- Every written output follows `anti-ai-writing-guidelines.json`. Page-level or over-300-word copy also follows `8-pass-writing-engine.md`.
- Short-form specialists may use their own constrained method, but their final output must still pass the anti-AI, factual, brand and channel checks in this contract.
- Research, writing, editorial QA and implementation are separate actions. A Lead dispatches one dependency-ready action at a time.

## Ownership

- **Originating Lead:** owns the business/channel diagnosis, evidence, audience intent and success measure.
- **Content Lead (`content` agent):** validates the brief, selects the writing skill, owns final wording and accepts editorial QA.
- **Writing specialist:** produces one bounded copy version using the selected skill and supplied evidence.
- **Content Quality Auditor:** independently checks voice, factual support, compliance, conversion intent, channel constraints and anti-AI rules. It does not silently rewrite the artefact.
- **Developer or publisher:** implements the exact accepted copy and reports rendering or platform constraints back to Content Lead.
- **Human approver:** owns offers, subjective brand positioning, consequential claims and production release.

## Skill ownership map

| Capability | Owning role | Final copy authority |
|---|---|---|
| Landing-page audit and CRO diagnosis | `landing-page-optimizer` | Brief only |
| Competitive analysis, content gaps, TAYA and keyword research | Relevant strategy/research skill | Research input only |
| Content strategy | `content-strategy` | Strategy and brief input only |
| Page and conversion copy | `copywriting`, `service-page-generator`, `seo-content-writer` or `content-refresher` | Content Department after QA |
| Comparison pages | `competitor-alternatives` | Content Department after QA |
| Copy revision | `copy-editing` | Content Department after QA |
| Ads, metadata, social and email | Their constrained specialist skill | Content Department acceptance when part of a staged project |
| GEO optimisation | `geo-content-optimizer` | Brief or verification unless explicitly dispatched to revise accepted copy |
| Editorial verification | `content-quality-auditor` | QA verdict, not strategy ownership |

## Accepted content brief

The originating specialist returns this durable object. Populate confirmed fields from accepted evidence. Use `unknown` for a material gap and return `needs_context`; do not interview Michael again for fields already answered upstream.

```yaml
content_brief:
  schema_version: 1
  parent_id: "stable production parent"
  action_id: "stable content action"
  brief_version: 1
  client_id: "canonical client ID"
  content_type: "landing_page | service_page | blog | copy_edit | comparison | pr | ad_copy | metadata | social | email"
  routes_or_placements: []
  objective: "Observable communication outcome"
  audience:
    segment: "Who"
    awareness: "What they already know"
    intent: "What brought them here"
  desired_action:
    label: "Required action"
    destination: "Exact verified URL, form anchor or channel action"
  evidence:
    performance: []
    search_or_campaign_intent: []
    voice_of_customer: []
    approved_research_artefacts: []
  current_content:
    source: "Observed URL or artefact"
    diagnosed_failures: []
  required_message: []
  fields_to_write: []
  preserve_exactly: []
  prohibited_or_unsupported_claims: []
  brand_voice_sources: []
  keywords_or_channel_constraints: []
  internal_links: []
  research_gaps: []
  approval_state: "approved_for_writing | needs_approval"
  delivery_destination:
    drive_folder_id: "Observed registered ID"
    drive_folder_url: "Observed registered URL"
    relative_path: "Governed path"
  completion_test: []
  return_to: "Content Lead"
```

An accepted brief answers the Content Agent interview through evidence. Content Lead may ask only for a material unresolved field. Optional research is a separate action and must update the brief version before writing resumes.

## Content production

Content Lead selects one writing route:

- page-level or over 300 words: the relevant writing skill plus the full eight-pass engine;
- short conversion copy: the relevant specialist skill plus a condensed anti-AI, voice, claims and CTA pass;
- audit or strategy only: no copy production action;
- mixed deliverable: separate the strategy artefact from the final copy artefact.

The writing worker receives the accepted brief and referenced source artefacts. It must not reinterpret the channel strategy, change protected offers, move CTA destinations or select between unapproved variants.

## Implementation-ready copy

After editorial QA passes, Content Lead saves and reads back this artefact in the registered Drive destination:

```yaml
implementation_ready_copy:
  schema_version: 1
  parent_id: "stable production parent"
  action_id: "stable content action"
  brief_version: 1
  copy_version: 1
  approval_state: "review_ready | approved_for_implementation"
  source_brief:
    artefact_id: "Observed ID"
    digest: "Immutable digest"
  placements:
    - route: "/exact-route"
      field: "H1 | subhead | body | CTA | metadata | ad field"
      current_text: "Observed baseline or null for new content"
      replacement_text: "Exact final text"
      destination: "Exact URL or anchor when applicable"
  preserve_exactly: []
  claims_and_sources: []
  checks:
    anti_ai: pass
    em_dash_count: 0
    factual_support: pass
    brand_voice: pass
    compliance: "pass | not_applicable"
    channel_constraints: pass
  editorial_qa:
    skill: content-quality-auditor
    verdict: pass
    verified_version: 1
  delivery:
    drive_file_id: "Observed ID"
    drive_url: "Observed URL"
    observed_parent_folder_id: "Observed parent"
    readback_evidence: "Observed name, version and content digest"
  implementation_completion_test: []
  next_owner: "Head of Production"
```

Multiple alternatives may exist in a workshop draft, but `approved_for_implementation` contains exactly one selected replacement per field. If human selection is required, stop at `review_ready` and do not dispatch development.

## QA and correction

Content Quality Auditor returns one verdict:

- `pass`: Content Lead may accept and persist the exact version.
- `correction_required`: return a bounded issue list to the same writer, then rerun QA.
- `needs_evidence`: route the factual gap to the originating Lead or research owner.
- `needs_approval`: bind the exact offer, claim, positioning or variant decision to a named approver.
- `waiting_on_capability`: preserve the artefact and resume point.
- `failed`: preserve the last accepted brief and evidence.

The anti-AI check is recorded, not assumed. At minimum, scan for em dashes and the prohibited patterns in `anti-ai-writing-guidelines.json`; then perform an editorial read for naturalness, specificity and voice.

## Implementation handoff

Head of Production dispatches the accepted artefact to the developer or publisher. The implementation worker:

1. verifies the copy version and immutable digest;
2. applies exact replacements only;
3. preserves named protected content and destinations;
4. runs platform, build, link and rendering checks;
5. returns any implementation constraint to Content Lead instead of rewriting around it;
6. provides a review URL or other observed implementation evidence;
7. does not merge, deploy, publish or send without the separate production authority.

## Resumption

Persist parent ID, action ID, brief version, copy version, artefact IDs, digests, QA verdict, approval binding and next owner. Resume the first incomplete transition. Never regenerate accepted research or repeat the interview because the conversation changed.
