# Working on your website

These instructions belong to this repository. Use Codex with local repository access or Claude Code; an ordinary web chat may not have the required local tools. Read repository instructions and CLIENT-REVIEW.md first. The site itself, release questions and explicit client decisions are the sources. Do not import private LHM context. Never expose credentials or send form/booking tests that create real enquiries or purchases without permission.

## Skill discovery and sessions
Use the Codex app or Claude Code with the website folder open and local file access. Ordinary ChatGPT/Claude chat does not run this local workflow. Cloning the prepared repository brings `.agents/skills/` and `.claude/skills/`; the setup prompt verifies all four entry points and `.lhm-review/workflows.md`, rather than installing an LHM plugin or claiming missing files exist. Reopen the session/project after cloning if discovery does not refresh. Claude Code uses `/start-website`; Codex uses `$start-website` or the skill picker (not an asterisk). For each new chat in the same website project: start-website, review-website, then finish-review.

## start-website
Check the working directory, Git remote/branch and local changes. If unfinished changes exist, preserve them and explain them; never reset/clean, overwrite or hide them in an automatic stash. Fetch via existing authenticatedGit route when allowed. Fast-forward a clean current branch only when its upstream is verified; stop and explain divergence/conflicts. Do not switch from a review branch with unfinished work to main just to sync.

Inspect package.json, packageManager, lockfile and Nodeengine. Use the declared package manager and frozen/locked install appropriate to that manager. Missing Node/Git/Python or authentication: give OS-specific steps, never install system tools or change permissions silently. Start the documented devscript and confirm the actual localhostURL responds before opening it. Use a browser chosen by the client when available, otherwise return the URL. Do not assume a browser tool or editor exists. If installation or preview fails, report the actual error and next step. Never call a server started until verified.

## review-website
Offer current release or allpending pages if multiple releases exist. Read client-review.json and use its verified config as authoritative; .lhm-review/client-config.json is its installed configuration view. An example-only configuration is incomplete setup. Show one pending page at its actual route; preserve unanswered questions from earlier releases. Ask the configured questions together where they concern the same page. Offer:
- Tell me what to change and I will suggest wording, show the change and update it after your direction.
- Open the verified source file in the editor supported here so you can change it yourself.
- Approve this page, revisit it, or ask LHM for help.

Do not invent facts, service claims, fees or practitioner information. Verify source mapping before editing; an Astro page may have content in Markdown, JSON or the component itself. If the editor cannot open the file, give its full path and how to open it. Wait for manual saves, check changes and show the refreshed local page. Ask for an explicit approval of current content. Do not infer it from “next”, editing, an answer or silence.

Use the bundled .lhm-review/review_release.py utility. For a revised page:
```sh
python3 .lhm-review/review_release.py fingerprint --root . --page-id PAGE_ID
```
Preview the content, obtain the decision, prepare answersJSON from actual answers and record it:
```sh
python3 .lhm-review/review_release.py review --root . --page-id PAGE_ID --status approved --person CLIENT_NAME --evidence ACTUAL_DECISION_REFERENCE --answers ANSWERS_JSON --fingerprint REVIEWED_HASH
```
Use the verified Python command for this machine; quote arguments correctly and never interpolate client wording into shell code. Prefer structured arguments or a temporary data file. Read back the register/checklist. If any unanswered question remains, resolve it or record needs-lhm. The tool refuses stale fingerprints. Do not manually mark Markdown checkboxes as a substitute for register decisions.

## share-preview
Default mode uses a review branch. The only direct deployment-branch exception is authoritative register config `sharing` with `mode: "prelaunch-main"`, `site_stage: "prelaunch"`, `branch` equal to the verified deployment branch, a verified `deployment_url`, and `operator_evidence` explicitly authorising that route. Verify the repository's actual deployment workflow, production domain and branch protection before using it. Missing, inconsistent, live or uncertain state falls back to the review-branch workflow. Never bypass protection or carry pre-launch authority into launch.

For the authorised pre-launch mode, explain that the named branch push updates the prototype, show the scoped diff, obtain/reuse explicit client sharing authority and run required checks. Fetch and reconcile remote changes safely; never force push. Commit only authorised files and review progress, push the configured branch through the client's own account, read back the remote SHA and verify deployment evidence and its exact URL. No PR is required for this explicitly approved direct branch route. A push without a successful deployment is reported as pushed, not deployed. Keep draft/unshared work local. Once launched, return to review-branch sharing and separate live-publication approval.

The following review-branch procedure applies by default:
Explain the exact changed files and obtain authority to commit/push the review branch and open/update its PR. Keep unrelated client changes out of the commit. Verify actual remote, production branch, current base and Cloudflare project. Never derive a CloudflareURL from a guessed project name. Use an existing session review branch or create a unique client-review branch from the verified appropriate base. Check remote updates, inspect the complete diff and run package scripts for build/type/content checks. Keep forms, bookings and analytics verification honest.

Push through the client's authenticatedGit route, read back remoteSHA, open/update the PR if authorised and check Cloudflare deployment evidence. Verify the exact deploymentURL serves the expected revision. If provider access or previewbranch configuration is missing, return branch/commit/PR evidence and the missing capability. Do not switch identities or bypass denied access. A failed build/push/deployment is incomplete, not a preview. No main push or production merge in the default review-branch workflow.

If the client asks LHM for help, prepare a specific GitHubIssue with the page, observed issue, requested decision and relevant commit/preview. Search existing issues first; create only with authority. Link the issue in the handback. Internal delivery remains in BasicOps; no automatic staff assignment or duplicate task board.

## finish-review
Review explicit decisions and saved file changes. Compare current fingerprints with approved fingerprints, reopening changed approvals. Summarise approved pages, edits not approved, unanswered questions and items needing LHM. Never count ten edited pages as ten approved pages. Preserve unfinished work and exact restart step. Offer the configured share-preview step when they want LHM to view their changes. In explicitly configured pre-launch mode it can push the verified prototype branch, including main, after actual sharing authority; finishing alone never authorises a push. Do not describe finish-review as automatically publishing. Record handback after sharing so it contains the observed branch/commit/deployment state.

Prepare a copyable email to the verified LHM contact supplied in configuration. Include what changed, approved pages, outstandingquestions, precise blockers and verified preview/PRlinks. Omit a previewURL if unavailable. Email is draft-only; client sends it themselves unless they separately authorise an available sendtool. Do not mark sent without provider evidence. Record handback evidence under the current release without rewriting approval history; read back changed records. Keep local-only, pushed, deployedpreview and livepublication distinct.
