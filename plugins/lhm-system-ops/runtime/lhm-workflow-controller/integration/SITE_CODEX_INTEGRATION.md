# Site/Codex governed-dispatch candidate

`/tmp/lhm-site-dispatcher.live` is an offline candidate. It does not alter the
legacy site request schemas. A request remains a standalone legacy request when
there is no root-owned contract named `controller-outgoing/<request_id>.json`.

For a governed Astro request, the dispatcher now fails closed unless the issued
contract selects the Codex worker, the fixed Astro stage, the two fixed Astro
skills, both fixed capabilities, amber branch mode, and the exact normalized
input-artifact IDs, SHA-256 hashes, and media types issued by the preceding
stage. Immediately before the
real `systemd-run` route it writes `governed-envelope.json` and calls:

```text
hermes_workflow_hook.py admit <controller-contract> <child-run-id>
```

The dispatcher deliberately does **not** emit skill, capability, or terminal
events. It cannot observe those facts at its current boundary.

## Required launcher/publisher integration

`/usr/local/libexec/lhm-site-change-launcher` must receive the child run ID (or
read it from the root-authored envelope) and make these calls at the actual
boundaries:

1. After the host skill loader has resolved and supplied the exact
   `lhm-wordpress-hub:start-astro` instructions to Codex:
   `hermes_workflow_hook.py skill <child> lhm-wordpress-hub:start-astro`.
2. After the host skill loader has resolved and supplied the exact
   `lhm-wordpress-hub:astro-build` instructions:
   `hermes_workflow_hook.py skill <child> lhm-wordpress-hub:astro-build`.
3. The root-controlled feature-branch publisher—not Codex—calls
   `capability <child> git.feature_branch_write` only after independent Git
   readback proves the expected branch and commit.
4. The root-controlled preview verifier calls
   `capability <child> cloudflare.preview_readback` only after provider
   readback, URL/alias binding, noindex, and expected revision checks pass.
5. Only the root launcher, after successful worker exit and successful
   publisher/verifier readbacks, normalises the legacy Codex response into the
   controller's candidate result schema and calls
   `complete <child> <trusted-result-path>`.

Worker-written `events.jsonl`, prose claiming a skill was used, an exit code by
itself, and a submitted preview URL are not valid observations.

Admission is intentionally earlier than worker launch, so a launch failure
leaves a non-terminal protected stream and cannot be promoted. The current
legacy dispatcher also leaves the already-created run directory behind; its
ordinary retry will therefore fail duplicate-request validation. Before a
canary, add a root-only reconciliation command which verifies the admitted
contract, confirms that no systemd unit/worker is alive, archives the abandoned
run directory, and then retries the same child idempotently. Do not delete or
silently replace the protected admission stream.

The hook's Codex result allow-root must include the actual site run root
`.../dispatch/site-runs`; its current generic `.../dispatch/runs` value does not
cover this dispatcher. Do not enable the bridge until that path is reconciled
and tested under the real Codex UID.
