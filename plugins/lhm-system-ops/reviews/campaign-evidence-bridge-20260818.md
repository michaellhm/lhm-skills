# Campaign evidence bridge — iteration 2 recorded passes

Parent `campaign-playbook-flow-20260818-01`; incident `campaign-evidence-bridge-20260818`; return point `head_of_production.release_and_live_test`; resume token `campaign-playbook-flow-20260818-resume-01`.

## 1. Capability Researcher — recommended

Canonical Obsidian overview first, then the existing authenticated Claude Google Drive route, Hermes-owned `fathom-meeting-lookup` MCP route, installed Claude content agent, and authenticated Drive create/read-back route. These native/existing capabilities meet the evidence boundary without a third party, new OAuth owner, copied token, or custom network integration. The supplied gateway, skill, MCP registration, IDs and conflict-policy evidence is authoritative for the bounded implementation. Operational identifiers remain only in root-owned per-run registration and are deliberately absent here.

## 2. Platform Engineer — implemented

Added strict request/result schemas for Drive exact read, Fathom exact-recording read, two-source hash-bound production, and exact-folder publication; a reusable bridge; complete Claude dispatcher/worker and Hermes Fathom wrapper assets; absolute-path preflight and fail-closed installation; canonical folder discovery; mode-0640 content artifacts; metadata-only logging; and exact read-back/idempotency behavior. No live host was patched.

## 3. QA Tester — pass

Executable tests cover schema strictness, overview-first discovery, unique verification/write-back, ambiguity incidents, exact IDs, artifact modes and hashes, two-source production, create/read-back, identical-content idempotency, differing-content refusal, log minimisation, gateway routes, install failure behavior, and rollback preservation. The full system-ops suite and repository validators are the release evidence commands.

## 4. Security/Reliability Reviewer — approved

OAuth remains with the existing Claude worker and Hermes profile. Source bodies are mode-0640 run artifacts and never logs. Requests are exact-field, exact-ID and registration-bound; paths are bounded to one run; subprocesses use argv, fixed executables, reduced environments, timeouts and suppressed connector stderr. Missing/ambiguous capability resumes via the existing incident contract. Publication never overwrites, moves or trashes. Residual risk: live CLI/MCP compatibility and connector authorization must be proven by the separately authorized preflight/live test before enablement.

## 5. Plugin Release Manager — ready for bounded publisher

Plugin version and marketplace entry are `0.5.0`. The supplied `cto/campaign-evidence-bridge-20260818` workspace is prepared for the root-owned publisher after all validation is green. The CTO lane does not commit, push, merge, install, enable, access credentials, or write Michael's review note. Rollback preserves registrations and durable evidence; publication is not capability restoration.
