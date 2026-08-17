# Campaign source runtime review

## Pass 1 — Capability Researcher
Used native CAP009 container queue, root host validation, durable callback, work-control and bounded publisher patterns. The prior state machine supplied blocker/receipt semantics. No third-party integration was added.

## Pass 2 — Platform Engineer
Added executable helper, host runtime, exact run registration enforcement, authenticated adapter commands, worker profile, production child, registered Drive publisher read-back, schemas and install/systemd assets. Also quoted the systemd path containing spaces and enabled `--untracked-files=all` in dispatcher/publisher status.

## Pass 3 — QA Tester
Isolated fixture evidence only: bounded fake connector tests cover Drive failure, one incident/no delivery, exact restoration/duplicate no-op, healthy Fathom+Drive receipts, production child, read-back, arbitrary-ID rejection, least privilege and both outage regressions. No live authenticated smoke read was performed in this branch workspace.

## Pass 4 — Security/Reliability Reviewer
Hermes has only queue/status access. Tokens, credential files, SSH, Docker, host shell, unrestricted filesystem and direct BasicOps mutation are denied. Exact registration, closed fields, content hashes, durable atomic JSON and full read-back fail closed.

## Pass 5 — Plugin Release Manager
Prepared version 0.4.0 assets only. Remaining deployment: Michael reviews and merges; separately approves installation; provisions root-owned per-run registrations; maps the four adapter commands to existing authenticated Claude/Fathom/production/Drive capabilities; runs a bounded authenticated smoke; then enables the path unit with rollback evidence.
