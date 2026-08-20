# Work-control resumer store-wiring repair — recorded role passes

Parent: `RELEASE-PUBLISHING-ENGINEER-20260820`  
Incident: `release-resumer-store-wiring-20260820`  
Branch: `cto/release-resumer-store-wiring-20260820`

## 1. Capability Researcher

Repository-native Hermes and LHM paths establish one existing contract: the native producer is
`/opt/data/profiles/lhm_brain/bin/work-control`, its container store is
`/opt/data/profiles/lhm_brain/dispatch/work-control`, and the profile bind exposes that store on
the host as `/home/hermes/.hermes/profiles/lhm_brain/dispatch/work-control`. The installed path
unit already watches the host store. The consumer-only `/var/lib/lhm-work-control` change created
an empty second store, so retaining it or migrating only the consumer was rejected. No third-party
capability is needed.

## 2. Platform Engineer

The resumer BASE now names the established root-owned host store. Persisted path and service units
bind the watcher and service sandbox to that exact store. A closed deployment contract records the
native producer executable, both sides of the profile bind, the watcher glob, consumer executable,
and the handoff mapping through the existing `/home/hermes/.hermes` to `/opt/data` bind. No producer, live state,
systemd instance, installation, credential, BasicOps record, client system, or external repository
was mutated.

## 3. QA Tester

Deployment parity jointly asserts the actual installed producer path, container output directory,
host bind target, path-unit glob, consumer BASE/incoming directory, service write boundary, and
handoff mapping. The legacy fixture begins with a false marker, processed event and waiting parent;
it preserves the marker, records reconciliation, requeues through the authoritative incoming store,
consumes and transitions once, then proves replay does not invoke Hermes again. Existing refusal,
strict-success, interrupted-write, traversal, symlink, mode and unrelated-state tests remain.

## 4. Security/Reliability Reviewer

The repair does not grant Hermes access to the canonical store. The root consumer still copies only
one validated event and its matching parent into an invocation-specific mode-0700 handoff, with
mode-0400 inputs owned by uid/gid 10000, and accepts only an identity- and digest-bound response.
The service writes only the authoritative store and ephemeral handoff. `/var/lib/lhm-work-control`
is explicitly rejected by validation, preventing a silent alternate installation.

## 5. Plugin Release Manager

Release metadata is aligned at `0.7.2`; the new runtime units, deployment contract, tests and this
review are included in release validation. The workspace remains an uncommitted reviewed feature
branch for the bounded publisher. Merge, installation, service reload/start, live reconciliation,
parent resumption and capability-restored publication remain Michael's authority.
