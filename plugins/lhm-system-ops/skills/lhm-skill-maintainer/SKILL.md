---
name: lhm-skill-maintainer
description: Govern updates to LHM skills from a CTO incident or improvement request through canonical source edits, validation, Git branch and pull-request delivery, approved merge, deployment, and live verification. Use when asked to fix, change, publish, install, or reconcile an LHM skill; do not use for ordinary execution of the skill.
---

# LHM Skill Maintainer

Turn one authorised skill change into a tested, traceable source release. The installed Hermes, Claude or Codex copy is runtime evidence, never the source of truth.

## Authority boundary

The dispatch authorises only the named repository, skills, profiles and acceptance test. Keep credentials and permission grants outside the skill.

- Diagnosis and read-only comparison need no publication authority.
- Source edits, tests, a feature-branch commit and a pull request are allowed when the CTO dispatch explicitly requests the change.
- Merge, release publication and production installation require explicit publication/deployment approval that names this change or immutable commit.
- Direct pushes to protected `main` are forbidden.
- Credentials, tokens, private profile state, client data and live `.env` files must never enter Git.
- Permission, identity, authentication, billing or infrastructure-boundary changes require separate consequential approval even when ordinary publication is approved.

For exact repository, version and release rules, read [references/release-contract.md](references/release-contract.md).

## Intake contract

Require or derive without guessing:

- incident or improvement ID and originating business parent;
- canonical repository and base branch;
- affected skill/plugin and destination profiles;
- observed failure with reproducible evidence;
- intended behaviour and observable acceptance test;
- permission ceiling, publication authority and return point.

If canonical source cannot be found, stop before editing. Report `source_provenance_missing` and propose where it should be governed; do not treat a live installation as a publishable repository.

## Workflow

1. **Reconcile source and installation.** Locate the canonical skill, inspect repository instructions, compare the relevant installed copy, and identify drift. Preserve unrelated changes.
2. **Create a bounded branch.** Use a `cto/<incident>-<short-name>` branch from the verified base. Record the base SHA. Never work on protected `main`.
3. **Make the smallest durable change.** Update instructions, supporting resources and tests needed for the acceptance test. Do not encode credentials or broaden the worker's capabilities.
4. **Complete repository hygiene.** Follow repository-specific version, manifest, catalogue, generated-file, parity and learning-review requirements. Remove scaffolding and generated caches.
5. **Validate behaviour.** Run the skill validator plus affected repository tests. Test observable decisions and safety invariants, not only wording. Record commands, results and limitations.
6. **Review security and deployment impact.** Confirm changed paths, secret scan, permission delta, affected profiles, rollback and whether a live hotfix must be reconciled.
7. **Prepare publication.** Commit only allowlisted changed files, push the feature branch through the bounded publisher, verify the remote SHA and open a pull request containing the evidence contract below.
8. **Stop at approval when required.** A pushed branch or open pull request is not permission to merge or deploy.
9. **Release only approved code.** After explicit authority, merge through the governed GitHub route, build from the immutable commit, deploy through the approved installer and verify installed hashes/versions on every named destination.
10. **Prove restoration.** Run the original regression against the live destination. Return evidence to the originating CTO card and business parent; do not close at “merged” or “installed.”

## Live hotfix reconciliation

An emergency live edit may precede Git only when necessary to restore a bounded production capability and authorised by the incident. It creates mandatory reconciliation work:

1. snapshot the exact pre-change file and metadata;
2. record the live diff, destination and verification evidence;
3. reproduce the intended change in canonical source;
4. pass normal review and publication gates;
5. redeploy from the immutable source commit;
6. verify the installed bytes match the release;
7. retain the rollback snapshot until live acceptance passes.

Never declare a hotfix durable while Git and production differ.

## Pull-request evidence

Include:

- incident and originating parent IDs;
- outcome and root cause;
- affected plugin, skill and profiles;
- base and candidate commit SHAs;
- exact changed files;
- validation, behavioural QA and security results;
- authority used and permissions unchanged or explicitly approved;
- rollout, smoke test and rollback procedure;
- live-hotfix reconciliation status;
- requested reviewer and post-merge return point.

## Completion

Complete only when the canonical commit is published under the recorded authority, every named destination is installed from that commit, installed identity is verified, and the original live acceptance test passes. Otherwise return one of: `needs_approval`, `blocked_on_source`, `blocked_on_validation`, `blocked_on_capability`, or `rolled_back`, with the exact next owner and safe return point.
