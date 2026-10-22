# RTB document and prototype revision pilot

Task: https://app.basicops.com/481630853364967730?l=_805_31C_1BFFC6A44D6 (2212824).

This is a real draft-edit route, not the Wellness saved-context summary. It is pinned to Raise The Bar, Michael Tasks 49020, reviewer 36398 and the verified Current Clients/Raise_The_Bar folder `1VWZkidj1x869sKc2zBxo8IrSb37w337H`. Only `rtb/homepage` in `michaellhm/lhm-prototype` is in scope. The latest captured feedback is Hayley's 18 October navigation/homepage revision list and Kate's 19 October selection of logo 4.

## Outputs and boundaries

Codex works in `/home/codexworker/clients/raise-the-bar` in a persistent native chat. It prepares three Markdown outputs: handbook revision, unsent reply and feedback/check checklist. It may edit the staged homepage HTML, existing `assets/css/style.css` and `assets/js/main.js`; other client files, source snapshots and images are protected. The original shared handbook and existing review draft are inputs, not overwrite targets. The clinical example letter/comment appendix is omitted from the worker snapshot. Surrey Hills is a requested navigation label; no location details or service availability may be invented.

The host verifies output hashes and the exact BasicOps approval again. A dedicated rclone connection creates uniquely named new review files in the fixed RTB folder; `--immutable`, full-content byte comparison and metadata ID/name readback prevent a silent differing overwrite or a false delivery claim. The source publisher creates only `codex/rtb-2212824-vN`, refuses an existing differing branch and verifies its remote commit. The verified source workflow publishes only pushes to main. No shared-site publication, production deployment or client email is part of this route. A review branch is source for review, not a published visual preview.

The BasicOps handback remains `awaiting_delivery` until a root-owned delivery receipt matches both the approval binding and artifact hashes. Then it links the review files and source branch and requests Michael's review. Failure returns a visible blocker rather than Complete.

## Preparation and activation

Stage `install-rtb.py`, `provision-rtb.py`, `activate-rtb.py`, `rtb-delivery.py`, the worker, bridge, TED entry `SKILL.md`, and the selected `context/*.md` snapshots together in a root-only staging directory. Refresh the existing scoped prototype source with its existing publisher credential before provisioning. Run `install-rtb.py`. It backs up the scoped runtime files and creates the client-only workspace, registry entry, delivery units and a service write-path extension. Both readiness switches remain false, and the delivery timer remains disabled.

A normal, separately authorised Google Drive connection named `lhm-rtb` is required. Rclone is already installed on the VPS, but neither the root nor Hermes service account had a configured remote during preflight. The default Claude account is signed in but did not expose a real Google Drive tool; a model answer without a tool receipt was explicitly rejected as proof of connectivity. The alternate Claude repair profile is signed out. Do not read/copy alternate-profile credential files to repair this: use Google's normal consent workflow for a dedicated file-service connection. Google's underlying OAuth grant can be broader than one folder; explain that scope to Michael before connecting. The production adapter itself pins every operation to the RTB folder.

After the normal connection is authorised, run `activate-rtb.py`. It requires a Drive backend, finds both registered source IDs in the exact client folder, refreshes and sanitises the handbook snapshots, seals the baseline, enables delivery monitoring and opens admission. It refuses to replace an already activated workspace or existing outputs. Refresh only TED's idle gateway and verify `codex_session_status` reports `mode=rtb_draft_edit, ready=true`. TED must then post a personally approved draft-edit production plan; a summary-only plan cannot enter the worker. Never enable readiness merely to make a smoke test pass.

## Validation and current evidence

Nineteen focused tests pass across bridge admission/handback, worker binding/readiness and RTB delivery. They cover stale/agent-authored approvals, immutable task/client identity, changed artifact rejection, exact Drive readback, fixed file names/folder, and source-branch request rejection. Runtime sources parse; release-version/parity/system-ops checks are required before push. These are same-session checks, not independent QA.

The prepared integration must remain inactive until the normal Drive connection passes. No RTB Codex production turn, Drive write, review branch push, shared-site update or client send has been performed merely by provisioning this route. Full live acceptance remains: personal plan approval → native chat/file edits → actual syntax checks → verified Drive files and Git branch → same-task native review handback. Browser visual review remains a separate check; Node is present on the VPS, but no headless browser was verified in this preparation.

For rollback, stop/disable `lhm-rtb-codex-delivery.timer`, set the registry readiness false, restore the scoped files from the printed RTB backup, remove the `rtb.conf` service drop-in and reload systemd/TED when idle. Preserve the RTB workspace and receipts; do not overwrite prepared work or remove account authentication. The Wellness route remains read-only.
