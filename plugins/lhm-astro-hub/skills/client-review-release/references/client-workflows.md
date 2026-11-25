# Working on your website

These instructions belong to this repository. Use Codex with local repository access or Claude Code; an ordinary web chat may not have the required local tools. Read repository instructions, `brain/Project.md` and the other `brain/` notes first. The site itself, release questions and explicit client decisions are the sources. Do not import private LHM context. Never expose credentials or send form/booking tests that create real enquiries or purchases without permission.

## start-website
Check the working directory, Git remote/branch and local changes. If unfinished changes exist, preserve them and explain them; never reset/clean, overwrite or hide them in an automatic stash. Fetch via existing authenticatedGit route when allowed. Fast-forward a clean current branch only when its upstream is verified; stop and explain divergence/conflicts. Work on `main`; never discard or hide unfinished work just to sync.

The Astro site lives in `site/`. Inspect `site/package.json`, packageManager, lockfile and Nodeengine. Use the declared package manager and frozen/locked install appropriate to that manager. Missing Node/Git/Python or authentication: give OS-specific steps, never install system tools or change permissions silently. Start the documented devscript and confirm the actual localhostURL responds before opening it. Use a browser chosen by the client when available, otherwise return the URL. Do not assume a browser tool or editor exists. If installation or preview fails, report the actual error and next step. Never call a server started until verified.

## review-website
Offer current release or allpending pages if multiple releases exist. Read `brain/Project.md` first, then `.lhm-review/client-review.json`, and use its verified config as authoritative; .lhm-review/client-config.json is its installed configuration view. An example-only configuration is incomplete setup. Show one pending page at its actual route; preserve unanswered questions from earlier releases. Ask the configured questions together where they concern the same page. Offer:
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
Use the verified Python command for this machine; quote arguments correctly and never interpolate client wording into shell code. Prefer structured arguments or a temporary data file. Read back the register and `brain/Project.md`. If any unanswered question remains, resolve it or record needs-lhm. The tool refuses stale fingerprints. Do not manually tick the checkboxes in `brain/Project.md` as a substitute for register decisions.

## share-preview
While the site is in staging, sharing a preview means committing and pushing to `main`; there are no review branches and no pull requests. Explain the exact changed files and obtain the client's go-ahead to commit and push. Keep unrelated or unfinished client changes out of the commit. Fetch first and stop if `main` has diverged; never reset, clean, force-push or pull over conflicting changes. Inspect the complete diff and run the `site/` package scripts for build, type and content checks. Keep forms, bookings and analytics verification honest.

Push through the client's authenticated Git route and read back the remote SHA of `main`; it must equal the local commit. Then check Cloudflare Pages deployment evidence for that commit and verify the exact deployment URL serves the expected revision. Never derive a Cloudflare URL from a guessed project name. If provider access is missing, return the commit and remote SHA with the missing capability. Do not switch identities or bypass denied access. A failed build, push or deployment is incomplete, not a preview. Never claim a preview is live before both the remote SHA and the deployment are verified. Production deploy is a separate step LHM approves.

If the client asks LHM for help, write the specific page, observed issue, requested decision and relevant commit in the email draft to LHM. Internal delivery remains in LHM's own task system.

## finish-review
Review explicit decisions and saved file changes. Compare current fingerprints with approved fingerprints, reopening changed approvals. Summarise approved pages, edits not approved, unanswered questions and items needing LHM. Never count ten edited pages as ten approved pages. Preserve unfinished work and exact restart step. Offer share-preview when they want LHM to view their changes. With the client's go-ahead, finish-review commits and pushes to `main` the same way share-preview does and verifies the remote SHA and Cloudflare deployment first; finishing alone does not authorise production publication. Never reset, clean or force-push, and preserve unfinished changes.

Draft the email to LHM for the verified LHM contact supplied in configuration. Include what changed, approved pages, outstanding questions, precise blockers and the verified preview link and commit. Omit a preview URL if unavailable. Email is draft-only; client sends it themselves unless they separately authorise an available sendtool. Do not mark sent without provider evidence. Record handback evidence under the current release without rewriting approval history; read back changed records. Keep local-only, pushed, deployedpreview and livepublication distinct.
