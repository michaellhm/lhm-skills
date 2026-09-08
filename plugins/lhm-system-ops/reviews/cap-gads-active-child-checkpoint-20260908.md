# Google Ads active-child checkpoint — recorded role passes

Incident: `cap-gads-active-child-checkpoint-20260908`  
Parent: `ads-cycle-2026-09-07-week-2`  
Return point: `head_of_production`  
Base: `8f16d06`

## Capability Researcher

Passed. Native `lhm-system-ops` work-resumer continuation state is the correct bounded capability;
no third-party plugin, provider change, new permission or custom service is required. The supplied
backup was unreadable to this lane, but its combined reviewed source is preserved by the clean local
reviewed commit `11433ad`, which was imported without dropping its timeout, wake and receipt fixes.

## Platform Engineer

Passed. The Hermes resume prompt now requires an active child to remain in `remaining_children`
until all receipt-backed delivery and BasicOps review requirements complete. Only then may its
unchanged complete receipt bundle be appended and the child removed. It shows a valid dispatch
checkpoint and requires immediate exit after one dispatched stage without polling, sleeping or a
long wait. The strict validator independently rejects a nonterminal checkpoint whose active child
is absent from `remaining_children`.

## QA Tester

Passed in repository fixtures. The focused prompt-contract regression proves the required wording,
the valid Raise the Bar checkpoint (`claude-gads-20260908-05`) and rejection of the actual malformed
shape. Existing work-resumer continuation, due-wake, timeout-budget, cumulative-receipt, duplicate,
restart and interrupted recovery coverage remains passing. The full system-ops validator and suite
also pass. No fixture invokes Hermes, Google Ads, Drive, BasicOps or messaging.

## Security and Reliability Reviewer

Approved for bounded publication review. Closed schemas, safe IDs, UTC wake validation, parent
digest binding, completed/remaining exclusion and the new active/remaining inclusion rule remain
fail closed. No dependency, credential handling, network route, provider, spend limit, filesystem
boundary or live mutation authority changes. Roll back to the prior immutable system-ops release
and restore the prior executable with its recorded ownership and mode if post-install acceptance
fails.

## Plugin Release Manager

Prepared as a separate pass. Candidate versions remain the combined reviewed versions:
Claude/marketplace `0.9.77` and Codex `0.9.55`. This lane did not commit, push, merge, install,
deploy, invoke Hermes, launch Ads work, write BasicOps or contact anyone. The root-owned bounded
publisher may reconcile only the listed persisted files and publish only the generated `cto/*`
branch. Michael retains merge, release and deployment authority.

Post-install reconciliation must preserve delivered Alpha Sports Med, reconcile rather than repeat
Raise the Bar run `claude-gads-20260908-05` in `needs_review`, and leave Heel Centre unstarted until
it becomes the first incomplete child. The desktop controller owns the matching restored event.
