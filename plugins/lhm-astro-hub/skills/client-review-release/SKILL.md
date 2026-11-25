---
name: client-review-release
description: "Prepare and refresh an Astro client website review release. Use this when LHM asks to hand a site to a client in Codex or Claude Code, install the client review toolkit, request approval of new service pages, add client feedback questions, or prepare the next content review release. Scan actual routes, propose the exact batch for operator approval, preserve prior page decisions, install portable client skills and prepare a draft invitation."
---
# Client review release

Use for the client-facing review workspace of an existing full website or a specifically selected landing-page project. This does not start another internal project handover. Read `../../references/obsidian-context-contract.md` and `../../references/delivery-artifact-contract.md`, then the client repo's `brain/Project.md`, `brain/Overview.md` and the other relevant brain notes. Resolve the actual repository, the Astro site folder (`site/`), the client approver and the Cloudflare Pages project. While the site is in staging there is one branch, `main`; there are no review branches and no pull requests. Never copy private LHM context, credentials or full internal notes into the client kit. BasicOps owns internal executable work; `.lhm-review/client-review.json` owns client page-review decisions, and `brain/Project.md` is its generated checklist, grouped by round. Neither changes automatically from the other.

Read `references/register-contract.md` and `references/client-workflows.md` before execution. The installed scripts require Python3.10+; discover its actual command (python3, python or py -3), do not assume one across operating systems. Retain repository/runtime permission controls.

## Setup
1. Inspect repository instructions, Git status, route sources, package files, existing client instructions and deployment settings. Preserve local edits. Never reset, clean, force push or pull over conflicting changes. Use `client-repo-setup` first if the repo is not yet scaffolded; this skill installs only the review toolkit.
2. Prepare a client configuration from `assets/client-config.example.json`. Verify concrete URLs and content-source mappings. Route sources in the client config are repo-relative paths under `site/`, for example `site/src/content/services/physio.md`. Discover static Astro/Markdown/MDX/HTML routes under `site/src/pages`. For dynamic routes, resolve getStaticPaths/content collections against actual data and list every concrete route with its sources/dependencies. Explicitly attest complete mappings only after checking the actual build/routes. Unmapped routes remain a coverage gap. Build output and route count are supporting verification, not approval evidence.
3. Default dependency coverage hashes every file under `site/src` conservatively. Narrow it to complete verified per-page dependencies only after inspection. Include imported data, images, layouts, public assets and relevant config outside `site/src` (for example `site/public`) as explicit dependencies. Unknown external inputs remain a gap. A shared template edit can reopen multiple pages.
4. Show install paths and exact release proposal before writing the client repository. After operator approval, run `scripts/install_kit.py --root CLIENT_REPO --approval-evidence 'reference to actual approval'`. It writes the canonical client skills to `skills/<name>/SKILL.md` and a short pointer `SKILL.md` in `.claude/skills/<name>/` and `.agents/skills/<name>/` telling the tool to read and follow `skills/<name>/SKILL.md`, plus `.lhm-review/`. It never touches `README.md`, `brain/` or existing instructions; the README comes from `client-repo-setup`. A conflicting client file stops the install with nothing written. `assets/README-client.md` is client-facing guidance to quote in the invitation; it is not installed into the repo. Local installation does not commit, push or deploy. Read back generated files. Restart skill discovery if the current app requires it.

## Prepare or refresh a release
Create a JSON release input with stable unique id, requested routes (optional), global questions, page_questions keyed by route and explicit excludes. An operator can request the next15 services; verify which concrete15 they mean and show any other pending pages. Do not silently substitute unrelated pages.

Run:
```sh
python3 scripts/review_release.py scan --root CLIENT_REPO --config CONFIG_JSON --release RELEASE_JSON --output PROPOSAL_JSON
```
Display selected routes/source files and why selected, questions, approvals reopened, excluded/out-of-scope pages, removed/renamed pages and unresolved gaps. No pages or questions are yet assigned to the client. Ask: “This is what the client will review. Approve this batch, or change the pages/questions?”

After explicit operator approval, create an approvalJSON containing approved=true, proposal_digest copied from the exact proposal, operator and evidence. Partial coverage additionally requires acknowledge_partial_coverage=true, with an honest limitation in the invitation. Never generate approval evidence from your own recommendation. Run:
```sh
python3 scripts/review_release.py apply --root CLIENT_REPO --proposal PROPOSAL_JSON --approval APPROVAL_JSON
```
Apply rejects changed content, altered proposals, concurrent register updates and reused releaseIDs. Exact repeat application is idempotent. Read back `.lhm-review/client-review.json`, `brain/Project.md` and `.lhm-review/client-config.json`. Apply is the only step that rewrites `brain/Project.md`; install never does. Approved apply replaces the installed example with the verified proposal configuration when the kit is present. The register config remains authoritative. JSON is authoritative; `render --root CLIENT_REPO` repairs `brain/Project.md` if needed. Report uncertain/failed writes and inspect the same paths before retrying.

## Invitation and publishing handoff
Read `references/client-invitation.md`: it is the client email prompt the content round sends. Choose first-time/round-one or later-round invitation. Before the first draft, ask whether the client has a GitHub account AND verified access to this specific repository. Distinguish no account, missing access, pending invitation and confirmed access. Include account creation/invitation steps only when needed; never grant access or assume it from account ownership. On repeat releases reuse settled evidence and ask only about actual access gaps.

For round one, include two copyable prompts: installation/start, then guided page-by-page design AND content review with chat or direct source-file editing. Add separate design/content questions to the proposed release so a partial answer does not count as full page approval. For later rounds, include the exact verified round label, page list/count, release ID and one resume/start/review prompt. Ask the operator if they want the ready-to-review email draft and preserve actual sender/recipient/CC instructions. Templates are in the invitation reference; never send automatically.

Offer a complete draft email to the verified client contacts using email-drafts. Include release summary, questions, registered repository/install instructions, verified previewURL if one exists, and this copyable prompt:

“Open my website repository and run review-website. Read .lhm-review/workflows.md and brain/Project.md. Start the local website safely, show the next page awaiting review, and guide me through the questions one page at a time. Let me edit with your help or open the real content file. Ask me before recording approval or sharing changes. Keep publication separate.”

Drafting does not send. Do not claim a release is available until its files are pushed under existing authority and deployment evidence is verified. Pushes to the client repo and external communication each need actual authority; a preparation-only request grants none of them. While the site is in staging, share-preview and finish-review commit and push to `main`, which Cloudflare Pages builds from `site/`. Never reset, clean or force-push, and keep unrelated or unfinished changes out of the commit. Production deploy is a separate approval stop. Respect the authenticated user identity; no account-sharing or permission changes.

## Acceptance and handback
Verify installed skill entry points, safe local start, representative static/dynamic page mapping, one edit plus explicit approval, changed-page invalidation and repeated release preservation. Test preview sharing only with authority and actual provider evidence. Return repository, commit on `main`, toolkit version, release/register links, approved and pending pages, unanswered questions, excluded pages, coverage gaps, verified previewURL or precise deployment failure, and email draft state. Never describe untested Mac/Windows/app support as passed.

At session finish, record verified outcomes in `brain/Project.md` (via `render`) and reusable toolkit lessons in this skill's `LEARNED.md`. Source improvements require existing source authority. Keep client review feedback in the client's repo.
