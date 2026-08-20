# Work-control incoming-directory repair — recorded role passes

Parent: `RELEASE-PUBLISHING-ENGINEER-20260820`  
Incident: `work-control-incoming-directory-20260820`  
Branch: `cto/work-control-incoming-directory-20260820`

## 1. Capability Researcher

The supplied authoritative native Hermes producer restore statement writes
`BASE / 'incoming' / <event_id>.json`. Repository inspection found the consumer and path unit
alone invented `events`; no third-party or custom capability is needed. The established LHM
work-control schema, transition and handoff contracts remain the native solution.

## 2. Platform Engineer

The persisted consumer now selects `BASE / 'incoming'`, and the persisted path unit watches the
exact corresponding host glob. The deployment contract records the producer's literal restore
path expression. Parity validation parses that expression rather than normalizing or independently
naming a directory. No live Hermes file, directory, service, event or parent state was accessed or
mutated.

## 3. QA Tester

The deployment test derives `incoming` from the parsed producer expression and proves producer,
consumer, contract and path unit equality. A negative fixture changes both deployment and watcher
to the nonexistent `events` alternate and confirms validation rejects them. The exact legacy
false-marker fixture verifies its event is requeued into `incoming`, consumed once, transitions its
waiting parent once, and does not invoke the agent on replay. Full result: `102 passed, 29 subtests
passed`; system-ops validation reports 11 skills.

## 4. Security/Reliability Reviewer

The change does not alter event schema, validation, idempotency keys, claim processing, strict
transition evidence, uid/gid ownership, handoff modes, service write boundaries, or false-marker
audit preservation. The deployment validator now fails closed when the consumer, contract glob or
path unit differs from the producer's literal directory. No credential or permission surface was
added.

## 5. Plugin Release Manager

The reviewed feature branch contains only persisted plugin assets, contract, validator, tests and
this review record. It remains uncommitted and undeployed for the bounded root-owned publisher.
Commit, push, merge, installation, systemd reload, live reconciliation and restoration remain
outside this CTO build and under Michael's standing release authority.
