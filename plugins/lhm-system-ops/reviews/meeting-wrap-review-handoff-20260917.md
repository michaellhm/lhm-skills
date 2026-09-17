# Meeting wrap review handoff — governed release record

Incident `meeting-wrap-review-handoff-20260917`; parent `basicops-2202183`; base
`8f16d06c34cc27c2db4ec195742555a3b7732e90`; branch
`cto/meeting-wrap-review-handoff-20260917`.

## 1. Capability Researcher

The canonical `michaellhm/lhm-skills` checkout already contains meeting capture/review,
`basicops-task-manager`, the Hermes production-plan/dispatch path, native review handling and Ted
ownership. The existing authenticated LHM route is sufficient. A third-party plugin, new mailbox
service, custom credential path or duplicate callback build would add authority without improving
acceptance-test fit, so each was rejected.

## 2. Platform Engineer

Added a shared Project Hub contract for exact selected-wrap/task approval, evidence reconciliation,
consolidated client inputs and unsent email copy, calendar-safe review targets, Lily routing, replay
protection, existing production/QA dispatch, Ted ownership, native review and truthful actor identity.
Existing skill entry points reference the contract. Synthetic executable tests use no client data,
mailbox IDs, credentials or live mutations.

## 3. QA Tester

The candidate must pass the targeted meeting-review contract suite, plugin/marketplace version
parity, script parity, JSON parsing and `git diff --check`. Source QA verifies all stated invariants.
Authenticated Gmail selection, BasicOps/Drive readback, native review, actor verification and a
single approved Wellness dispatch remain post-install smoke tests because this lane may not touch
live systems.

## 4. Security and Reliability Reviewer

Permission ceiling is unchanged: read authenticated intake evidence; mutate only exact approved
BasicOps tasks; run reversible ordinary internal production; write verified durable artefacts and a
native review request. No credential, OAuth, outbound client-contact, ads, publishing, deployment or
live-edit authority is added. The contract fails affected items closed on missing identity, board,
Inbox, input, approval or readback, and uses a stable idempotency key to prevent replay dispatch.

## 5. Plugin Release Manager

- Source plugin: `lhm-project-hub`, candidate version `0.1.83`.
- Marketplace entry: `lhm-project-hub` `0.1.83`.
- Release tooling: `lhm-system-ops` `0.9.77`; Project Hub deployer `1.0.8`, pinned to
  `lhm-project-hub` `0.1.83` with its content digest recorded in
  `references/project-hub-deployer-release.json`.
- Exact installation profile after Michael's approval: `lhm_brain` only, through the existing
  root-owned `lhm-approved-project-hub-deployer`; never edit the generated skills directory.
- Pre-install evidence: record current immutable release, version, digest, ownership and permissions.
- Install verification: exact approved commit/package digest, installed plugin version, catalogue
  audit, and hashes/readback of the affected contract and skill entry points.
- Controlled smoke: select the exact authorised Wellness wrap; prove the `2026-10-14` meeting yields
  `2026-09-30`; dispatch only one input-ready approved preparation item; retain blocked client-input
  work with its human owner; verify Lily actual actor, Ted claim/return when used, durable output,
  native request review and open `Under Review`; do not send, publish, launch ads or complete.
- Rollback: atomically restore the recorded prior immutable `lhm-project-hub` release and its exact
  metadata through the same root-owned deployer, refresh only the affected catalogue, rerun the prior
  healthy read-only smoke and retain receipts for audit.

The bounded root publisher must create the candidate commit, push only this generated `cto/*`
branch, verify the remote SHA and write Michael's review note. Publication is not merge, release,
installation or capability restoration; Michael retains those authorities.
