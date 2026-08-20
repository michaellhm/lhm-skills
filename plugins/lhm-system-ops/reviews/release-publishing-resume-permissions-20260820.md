# General work-control resume permission repair — recorded role passes

Parent: `RELEASE-PUBLISHING-ENGINEER-20260820`  
Incident: `release-publishing-resume-permissions-20260820`  
Branch: `cto/release-publishing-resume-permissions-20260820`

## 1. Capability Researcher — native bounded handoff selected

The installed smoke evidence showed that event validation and claiming succeeded, but a root-owned
mode-0600 claim and parent were passed by path to Hermes uid/gid 10000. Hermes correctly refused
to invent consumption or a parent transition. Native LHM already has the event producer,
work-control state and root-owned resumer boundary, so no third-party plugin, credential access,
directory ACL or broad group read is needed. The selected design copies only the validated event
and matching parent into an ephemeral uid/gid-10000 handoff. Hermes may write only its response.
The privileged resumer validates and durably applies the result.

Rejected alternatives: making work-control directories group-readable exposes unrelated parents
and claims; making canonical parents group-writable expands authority; treating exit zero or prose
as consumption recreates the incident; copying credentials into the handoff is prohibited.

## 2. Platform Engineer — workspace implementation

Added `lhm-work-resumer`. It validates the closed `capability_restored` producer schema and exact
blocked parent, creates one mode-0700 handoff owned by uid/gid 10000, and places mode-0400 event and
parent copies inside it. The agent response must bind the event ID, parent ID and pre-transition
parent digest; say `transitioned: true`; name an allowlisted continued, terminal or explicit-wait
state; and persist non-empty evidence. Root then stores the exact agent-consumed record, verifies
the parent has not changed, atomically transitions it, and only afterward writes the idempotent
success marker. Exit zero alone, refusal, missing response, missing event ID, digest mismatch,
`NOT transitioned`, empty evidence and unchanged blocked state fail without a success marker.

The durable agent record is a transaction checkpoint: an interrupted run completes the parent
transition without invoking Hermes twice, and an interrupted success-marker write is reconstructed
from the exact persisted agent record and transitioned parent. A non-blocking host lock prevents
concurrent consumers. False legacy markers are reconciled only when the exact
event still has a matching blocked parent and no agent record. The old marker is moved intact into
the reconciliation audit directory, the processed event is requeued, and an idempotent audit
record is written. Interrupted audit finalisation is recoverable without duplicate agent work.

No live parent, event, consumed marker, Hermes installation, BasicOps record, repository, website,
credential or client communication was touched.

## 3. QA Tester — pass

The integration fixture uses the real repository producer event schema and the new resumer
contract with the incident's uid/gid 10000 boundary. It verifies exact handoff contents and modes,
chown targets, no unrelated file in the bundle, and denied reading of an unrelated mode-000 parent.
Positive transition, explicit persisted wait, exit-zero refusal, NOT-transitioned, missing event
ID, duplicate delivery, durable-checkpoint restart, parent-applied/marker-missing restart,
false-marker reconciliation and interrupted reconciliation recovery are covered. The full suite
passed 95 tests and 19 subtests. Validation command evidence is recorded in the
CTO structured handoff; live installation and parent resume remain deliberately untested here.

## 4. Security/Reliability Reviewer — approved for feature-branch review

The change grants no canonical work-control traversal or write permission to Hermes. The handoff
contains exactly two root-selected JSON copies and one response directory, is removed after each
attempt, and contains no credential path. Event, parent, response and transition are identity- and
digest-bound. Parent writes and success markers remain privileged, atomic and ordered. False
markers are preserved as audit evidence, not deleted or trusted as proof.

Residual deployment risk: the bounded installer must map `/run/lhm-work-resumer` into the Hermes
container at `/opt/run/lhm-work-resumer`, install the executable root-owned, and attest uid/gid
10000 before the live regression. Michael's approval is required for merge and installation.

## 5. Plugin Release Manager — bounded publication handoff only

Plugin version `0.7.1` is aligned in the Codex, Claude and marketplace manifests. The persisted
workspace is uncommitted on the required feature branch. The root-owned publisher may reconcile
only the reported files and publish only this `cto/*` branch for Michael's review. It must not
merge, install, resume the live parent, reconcile the live false marker or claim restoration.
