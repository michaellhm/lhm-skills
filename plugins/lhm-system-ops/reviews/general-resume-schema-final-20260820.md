# General work-control resume schema parity — recorded role passes

Parent: `RELEASE-PUBLISHING-ENGINEER-20260820`  
Incident: `general-resume-schema-final-20260820`  
Branch: `cto/general-resume-schema-final-20260820`

## 1. Capability Researcher

Native Hermes evidence is authoritative: host producer `/home/hermes/.hermes/profiles/lhm_brain/bin/work-control`, container producer `/opt/data/profiles/lhm_brain/bin/work-control`, and supplied installed SHA-256 `7814ccfba1670b389764222b6d2bfa108b3bdd30af22f2f4a9b40f4a6d9cc35a`. The general producer emits the closed eleven-field event and derives its key from `f"{parent_run_id}\0{resume_token}".encode()` with SHA-256. No third-party capability is needed.

## 2. Platform Engineer

The consumer now accepts exactly the general producer fields, verifies a timezone-aware UTC timestamp, recomputes the byte-exact idempotency key, and binds parent ID, incident, return point and resume token to the waiting parent. Durable agent checkpoints, atomic parent transition and success-marker ordering remain unchanged. Marker paths use the producer idempotency key. Legacy exit-zero markers are requeued only when all five exact fields match, the parent remains blocked and no agent record exists.

## 3. QA Tester

Repository fixtures reproduce the supplied event, waiting parent, legacy marker and exact processed filename. Tests cover the successful reconciliation and one agent invocation, replay without a second invocation, every parent binding mismatch, digest/timestamp/evidence failures, legacy marker identity and exit-code failures, path traversal, symlinks, refusal, false transition, checkpoint recovery and least-privilege handoff modes.

## 4. Security/Reliability Reviewer

The change adds no credential, network, deployment or live-state access. Invalid producer keys, non-UTC timestamps, marker mismatches and parent mismatches fail closed. The privileged consumer continues to expose only one validated event and parent copy to uid/gid 10000 and retains canonical writes.

## 5. Plugin Release Manager

This is a feature-branch-only repair. Michael retains merge, installation, reconciliation and restoration authority. The root-owned publisher may publish only the generated `cto/*` branch after reviewing the recorded test evidence; it must not alter live work-control state or infer capability restoration from publication.
