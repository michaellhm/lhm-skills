# Landing Page Optimizer routing regressions

## Audit only

Input: "Audit this paid landing page and tell me what is wrong."

Expected:

- returns CRO evidence, scoring and prioritised recommendations;
- labels any sample wording as illustrative;
- does not claim to have produced developer-ready copy;
- does not invoke Content production without approval.

## Approved replacement copy

Input: A staged Hermes action containing an approved landing-page audit, campaign evidence, exact routes, protected offer, CTA destination and registered Drive folder.

Expected:

- returns a versioned `content_brief`;
- sends the brief to Content Lead without repeating confirmed discovery;
- Content Lead selects `copywriting`, not `landing-page-optimizer`, as the writing route;
- final copy passes `content-quality-auditor` implementation-copy QA;
- durable output has `em_dash_count: 0` and a verified Drive readback;
- development receives only `implementation_ready_copy` with one selected replacement per field.

## Unselected variants

Input: Audit proposes headline A and headline B, but no human or governed rule selects one.

Expected:

- state is `review_ready` or `needs_approval`;
- no developer dispatch occurs;
- alternatives are not labelled implementation-ready.

## Missing destination

Input: Brief requests a CTA rewrite but supplies no verified CTA destination or registered Drive folder.

Expected:

- returns `needs_context`;
- identifies the exact missing fields and owner;
- preserves resume point `validate_content_brief`;
- does not guess a URL or client folder.

## Developer constraint

Input: Developer reports that the accepted replacement exceeds a platform field limit.

Expected:

- developer does not rewrite the copy;
- constraint returns to Content Lead;
- revised copy receives a new version and another editorial QA pass.
