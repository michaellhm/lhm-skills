# Prototype feedback host runtime

This is a scoped host component, separate from a plugin-wide install. It uses the existing authenticated Ted BasicOps connector, saved native Codex conversations, registered client workspace, shared prototype publisher and root router supervisor. It does not send client email or add a notification service. Michael's existing app handles computer notifications automatically when the checked work returns for review.

## Runtime paths and boundaries

| Item | Fixed location |
| --- | --- |
| Current immutable component | `/opt/lhm-prototype-feedback/current` → `releases/<exact-commit>` |
| CLI compatibility projection | `/usr/local/libexec/lhm-prototype-feedback` → `/opt/lhm-prototype-feedback/current/scripts` |
| Root site registration | `/etc/lhm-prototype-feedback/sites.json`, root-owned `0600` |
| Existing pilot queue | `/var/lib/lhm-prototype-feedback/state/queue.sqlite` |
| Existing owner and pilot records | `state/owner.json`, `state/pilot.json`; preserve their exact contents |
| New uncertain-write journal | `state/effects.sqlite` |
| Root-promoted feedback evidence | `evidence/<site>/<message-id>/` and `inbox/<site>/<message-id>.json` beneath the component state root |
| Root source provenance | `sources/<batch>/source-manifest.json`, `fetch.json` and private exact archive |
| New worker-readable images | Registered worker root / `feedback-assets/<batch>/` |
| New immutable worker source | Registered worker root / `feedback-source-snapshots/<batch>/source/` |
| Existing independent QA state | `/var/lib/lhm-prototype-feedback/qa-runs/` |
| Root authority source | `/opt/lhm-plugin-releases/prototype-feedback-authority/authority.json` |
| Read-only authority projection in Hermes | `/opt/data/immutable-plugin-releases/prototype-feedback-authority/authority.json` |
| Dedicated root-only source object store | `/srv/lhm-prototype-publisher/feedback-source.git` |

The existing pilot's `feedback-source` folder is a separate worker-owned input snapshot. Never rename, replace or change its ownership. New snapshots use the new path above. The top-level feedback audit directory may retain its existing root-owned `0755` mode; private queue, owner, inbox and raw evidence remain in `0700` directories with `0600` files.

Only the currently registered Luminary prototype is enabled by this release. Its repository directory is `luminary-counselling/homepage/`; `/prototypes/` is part of the public URL, not a repository directory. Other sites require a separately verified registration and an extended authority verifier, rather than silently sharing this pilot's route.

## Registration and source evidence

Keep real client addresses, message/thread IDs and registration JSON outside Git. The closed registration envelope is `schema_version=1` plus `sites`, keyed by the registered site ID. Each site contains exactly:

`enabled`, `account`, `senders`, `threads`, `review_start`, `cockpit_id`, `stage_id`, `client_id`, `client_label`, `canonical_note`, `work_folder_url`, `repository`, `subtree`, `preview_url`, `reviewer_id`, `worker_root`.

Resolve every field from the canonical client record, live BasicOps readback and authenticated Gmail source. Use the original prototype email's actual timestamp for the review window. Preserve the earlier manual pilot record; refining the future registration does not rewrite its history. Never infer a client folder or repository from the public brand name.

Scanner promotion requires complete raw MIME, every image, an actual extraction-session ID and reviewed interpretation. Root admission re-reads the MIME, sender, timestamp, Content-IDs, hashes and full attachment inventory. Both scanner and host require the first receiving `Authentication-Results` header to belong to `mx.google.com` and report aligned DMARC **and** DKIM passes for the registered From domain. Lower injected passing headers cannot override a missing or failing first header. Ambiguous authentication is held without consuming the message as a no-op. This policy relies on raw source fetched through the authenticated Gmail transport; an arbitrary uploaded `.eml` is not Gmail provenance.

Root source preparation reuses the existing publisher's transport internally, fetches the exact main commit into a separate private bare object store, and archives only the registered homepage subtree. It never resets the shared publisher checkout. Static paths, sizes, symlinks, hashes and root manifests are checked. The worker copies the immutable homepage into `drafts/revised-source/luminary-counselling/homepage/` before editing. Private revision notes stay outside that public subtree. No publisher credential reaches the worker.

## Prepare and install a reviewed commit

1. Reconcile live source hashes with the approved candidate. Preserve independent repairs and every active worker/session. Verify the candidate's remote commit, affected tests, plugin versions and catalogue checks.
2. Build a **Git archive of that exact committed revision**, containing the explicit selected paths listed in `install_runtime.py`. Retain its SHA-256. The installer checks both the reviewed archive digest and Git's archive commit marker; it does not extract arbitrary archive members.
3. Verify the task QA root is root-owned, group `10001`, mode `0750`. The pilot reconciliation was nonrecursive and retained its prior metadata at `/var/lib/lhm-prototype-feedback/qa-root-metadata-before-runtime.json`; child diagnostics were preserved. The installer creates a missing task QA root with the correct metadata but refuses to silently repair an existing mismatched directory. Transfer the archive, exact committed installer and private registration to the existing root administrator route. No credentials belong in the archive or registration.
4. Run the installer without `--apply` to prepare a report. Capture a fresh root-private live baseline with `--capture-baseline`. Apply using that exact baseline only after current source/readback and runtime prerequisites are satisfied. Source drift aborts; do not substitute a whole plugin/router install.

Example operator arguments, with independently verified values supplied by the operator:

```text
python3 install_runtime.py --archive <committed-git-archive.tar> --commit <40-char-commit> --archive-sha256 <64-char-digest> --registration <private-sites.json>
python3 install_runtime.py --capture-baseline <private-baseline.json>
python3 install_runtime.py --archive <same-archive> --commit <same-commit> --archive-sha256 <same-digest> --registration <same-private-sites.json> --baseline <private-baseline.json> --apply
```

The scoped installer:

- stages selected code and the complete loop skill in a new immutable release and verifies hashes;
- acquires nonblocking install, poll, queue-runner, scanner, completion and existing supervisor locks; busy work defers installation rather than being stopped;
- backs up every explicitly replaced helper/document, its original mode, QA-root metadata and prior links;
- takes a consistent SQLite **backup**, without changing or migrating the live queue;
- replaces only selected task-router helpers, the one reviewed Ted profile `task-router/router.py` projection, the reviewed publisher, private registration and the loop's Brain/Ted documentation files;
- updates only this loop's Codex skill link and the component projections;
- does not reinstall or reset the central router/profile bundle, replace credentials or change other skills;
- does not install/enable the timer, reload gateways or stop workers.

Installing source is not acceptance. Read back current release, helper/document hashes, profile links, private registration, authority mount and queue identity. Existing ready-for-review pilot messages must remain already processed; never create another task by recognising a similar title. Genuine unmatched existing source tasks require explicit queue adoption.

## Verify before enabling polling

Use the fixed CLI for readback and a zero-remote-write preparation check:

```text
python3 /usr/local/libexec/lhm-prototype-feedback/host_runtime.py readback --site luminary-counselling
python3 /usr/local/libexec/lhm-prototype-feedback/host_runtime.py dispatch --site luminary-counselling --dry-run
```

Then perform an authorised controlled scan and manual host sweep with scheduling disabled. Prove extraction, complete images, task/discussion authorship/readback, actual native request plus saved chat, correct immutable source, unchanged active brief, queued later feedback, restart/timeout recovery, stage exit and no duplicates. A queued router request is `submitted-awaiting-admission`, not a dispatched worker. Independent browser/semantic QA, Drive file readback, exact publisher commit/workflow/public bytes and native Michael review must all pass before the batch becomes ready for review.

The existing router tick owns completion/correction. Do not install a second completion poller. Corrections stay in the original implementation conversation and preserve the original batch; uncertain launches remain reconciling, rather than creating a fresh task/run. Unverified rebate or booking-platform claims remain excluded and explicitly held for review.

The browser uses Chromium sandboxing. The exact AppArmor rule approved during the pilot is `/etc/apparmor.d/lhm-prototype-feedback-qa`, scoped only to:

```text
/opt/lhm-prototype-feedback-qa/browsers/chromium_headless_shell-1254/chrome-headless-shell-linux64/chrome-headless-shell
```

That specific rule was approved and applied separately; this installer does not create it. Verify its loaded state and the unchanged global `kernel.apparmor_restrict_unprivileged_userns=1` before accepting browser QA. Do not use a wildcard rule, disable the global protection or switch off Chromium sandboxing as a shortcut. A browser binary/path upgrade needs a fresh scoped check.

## Prepared two-hour schedule

The committed `systemd/lhm-prototype-feedback.service` and `.timer` are **prepared assets only**. They are not installed or activated by `install_runtime.py`.

The timer is `*-*-* 00/2:00:00 Australia/Melbourne`, with persistent catch-up and one-minute accuracy. The one-shot service calls `poll_runtime.py`, which serializes the sweep, checks live eligibility, invokes the authenticated read-only scanner, imports packets and dispatches through the existing Ted route. Queue operations and scanner promotion retain their own locks. Journal output contains bounded state/IDs/counts, not raw feedback or connector/model output. No separate completion loop or desktop reminder is involved.

Only after the full manual acceptance passes should the operator install these exact units, validate the calendar, enable the timer and record the timer configuration, first-run result and next wake. Read every external change back. Keep status distinct: prepared code; installed component; accepted native dispatch; independently verified preview; enabled and observed polling.

## Pause and rollback

Moving the cockpit out of Prototype Feedback immediately blocks new task/submit admission. It does not interrupt an existing worker or its completion handback. Disable the timer to prevent future wake-ups; stopping a timer does not stop already-running work. Do not stop `lhm-task-*`, the central router, or client workers to pause this loop.

For component rollback, first pause intake. Use the private installation backup's `before.json` and `target-index.json` to restore only recorded replaced helper/document files and their exact modes, remove only recorded previously absent files, and restore the recorded component/Codex links. Verify all restored hashes. Preserve the live queue, original owner, source/QA evidence, remote receipts, saved chats and active runs; the SQLite backup is recovery evidence, not permission to overwrite newer task state. No gateway or plugin-wide rollback is part of this procedure.
