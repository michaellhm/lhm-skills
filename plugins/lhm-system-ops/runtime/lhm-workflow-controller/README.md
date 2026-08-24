# LHM Workflow Controller

Host-enforced orchestration for the fixed `seo-content-astro-v1` production workflow.

This service owns durable workflow state and accepts only host-derived evidence. Workers cannot
advance parent state or self-verify completion.

## Client preflight release

The `lhm-seo-org-canary-mvp` entry point requires a canonical Obsidian client record before
dispatching research. The required record is:

`_System/Hermes/clients/<client-id>/capabilities.json`

The Google Search Console capability must be `verified`, use the fixed `seo_gsc_readonly` route,
match the workflow property exactly, allow the four bounded read operations, and reference a
passing smoke-test result. Missing or incomplete records stop with `client_onboarding_required`.

This source tree is durable package source only. Copying or building it does not enable the cron,
start a watcher, install a service, or mutate the live vault.

## Universal departmental action state

`lhm_workflow.departmental_state` provides the reusable parent/department/action-goal contract for
department Leads. It keeps an ordered action register, binds every version to the digest of its
accepted inputs, permits only the first incomplete action to run, and advances only after an
independent verifier acceptance. `DepartmentalStateStore.checkpoint()` uses an atomic replace and
mandatory readback before reporting success. Candidate recording, independent QA, Lead acceptance,
and verified business-state/BasicOps projection are separate transitions; downstream inputs are
materialised only after all four complete. The `department-*` CLI commands expose the governed CAS
path. The fixed SEO canary and client-preflight path remain
unchanged until a separately governed pilot adopts this contract.

The source-only SEO-01 pilot envelope in `seo_capability_envelope` pins Marketing Hub 2.2.2 and
admits only `keyword-research` followed by `seo-delivery-qa`. It binds the registered LHM GSC
property, Drive folder, BasicOps hierarchy/task, and corrected canonical tracker path. Keywords
Everywhere and Google Ads are explicitly unavailable and every result must retain the degraded
evidence label. Canonical-state, Drive, and BasicOps projections are separate, ordered exact
readback transitions. `seo-envelope-deployment.json` keeps snapshot and projection services off
until reviewed and separately approved for deployment.

Drive observations, QA acceptance, Lead acceptance, and final projection are closed HMAC-sealed
role receipts. Durable outputs require an exact file/parent/content/readback receipt. Non-durable
actions must declare that contractually and return a structured `not_required` reason. Projection
binds exact tracker bytes and BasicOps task/comment readback to the parent, action, and version.

The controller exposes no receipt-signing CLI. Trusted Drive, QA, departmental-Lead, approval, and
projection adapters must create the closed receipts in their separately privileged service
boundaries; an unsigned or incorrectly signed CLI submission fails closed. The repository tests use
executable fake adapters with isolated test keys. Live pilot enablement still requires installing
and service-testing the real Lead and projection signers plus their BasicOps and Drive readbacks;
this source release does not claim those external adapters are live.

The packaged QA and Lead producer paths are the first real signer lanes. Their request schema
contains identifiers only; receipts are derived from controller-observed candidate/QA state. Drive,
BasicOps, approval, projection and HOP producers remain fail-closed pending a trusted observed-data
adapter. The existing Claude dispatcher references demonstrate available Drive and BasicOps APIs,
but are not promoted here because they do not yet emit the closed departmental receipt schemas.

Internal status vocabulary is `ready`, `worker_running`, `qa_accepted`, `lead_accepted`, and
`department_accepted`. External worker outcomes remain `candidate`; human approval is represented
only by a version-bound machine approval receipt, never by a free-text status.
