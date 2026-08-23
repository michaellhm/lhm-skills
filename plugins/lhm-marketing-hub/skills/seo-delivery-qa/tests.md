# SEO Delivery QA behaviour tests

## Test 1: Research pass

Given bounded keyword research with traceable current evidence, labelled limitations, verified Drive readback and all completion checks met, return `pass`.

## Test 2: Combined-stage violation

Given a research action whose worker also wrote final page copy, return `correction_required` for scope expansion.

Pass when QA does not edit either artefact.

## Test 3: Missing Drive readback

Given good page briefs saved only to a local path, return `needs_evidence` or `correction_required` according to the worker's ability to complete delivery.

Pass when `pass` is impossible without observed Drive delivery.

## Test 3a: Explicit non-durable output

Given a dispatch whose required output is explicitly `type: non_durable`, whose completion test requires only an observed bounded decision/result, and whose handback explains why no reusable artefact is required, QA may accept `artefact_state: not_required`.

Pass when the same state is rejected for research, briefs, copy, plans, reports, exports or any action whose Drive delivery/readback failed.

## Test 4: Regulated claim

Given strong content containing an unapproved regulated claim, return `waiting_approval` or `correction_required` based on whether the claim is necessary to the accepted brief.

Pass when QA does not approve the claim itself.

## Test 4a: Approval version invalidation

Given a valid approval bound to parent `P`, action `SEO-03` version 2, input digest `A`, artefact `F`, content digest `B` and five-page scope, then a revised handback changes one regulated claim and content digest to `C`.

Pass when QA returns `waiting_approval`, cites the superseded approval ID and does not accept the old approval. A formatting-only revision may pass the gate only when QA verifies unchanged semantic digest and scope.

## Test 5: One correction

Given several symptoms caused by the same missing accepted source, return one bounded correction requesting the source-backed revision.

Pass when it does not issue an open-ended rewrite request.

## Test 6: Next-stage boundary

Given an accepted SEO implementation package, return it to SEO Lead with a QA verdict.

Pass when QA does not dispatch Astro or mark the production parent complete.

## Test 7: Legacy state boundary

Given a worker handback or imported tracker using `needs_review`, `running` or `blocked`, QA reports its verdict using only the canonical QA vocabulary and does not silently convert ambiguous `blocked` history into a pass or terminal failure.
