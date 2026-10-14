---
name: client-review-release
description: "Prepare and refresh an Astro client website review release. Use when LHM asks to hand a site to a client in Codex or Claude Code, install the client review toolkit, request approval of new service pages, add client feedback questions, or prepare the next content review release. Scan actual routes, propose the exact batch for operator approval, preserve prior page decisions, install portable client skills and prepare a draft invitation."
---
# Client review release

Use for the client-facing review workspace of an existing full website or a specifically selected landing-page project. This does not start another internal project handover. Read `../../references/obsidian-context-contract.md` and `../../references/delivery-artifact-contract.md`, then relevant canonical client/project records. Resolve the actual repository, work folder, current branch, client approver and Cloudflare project. Never copy private LHM context, credentials or full internal notes into the client kit. BasicOps owns internal executable work; client-review.json owns client page-review decisions. Neither changes automatically from the other.

Read `references/register-contract.md` and `references/client-workflows.md` before execution. The installed scripts require Python3.10+; discover its actual command (python3, python or py -3), do not assume one across operating systems. Retain repository/runtime permission controls.

## Setup
1. Inspect repository instructions, Git status, route sources, package files, existing client instructions and deployment settings. Preserve local edits. Never reset, clean, force push or pull over conflicting changes. Reuse `repo-install` for installation guidance when available; it must retain these narrower boundaries.
2. Prepare a client configuration from assets/client-config.example.json. Verify concrete URLs and content-source mappings. Discover static Astro/Markdown/MDX/HTML routes. For dynamic routes, resolve getStaticPaths/content collections against actual data and list every concrete route with its sources/dependencies. Explicitly attest complete mappings only after checking the actual build/routes. Unmapped routes remain a coverage gap. Build output and route count are supporting verification, not approval evidence.
3. Default dependency coverage hashes all src files conservatively. Narrow it to complete verified per-page dependencies only after inspection. Include imported data, images, layouts, public assets and relevant config outside src as explicit dependencies. Unknown external inputs remain a gap. A shared template edit can reopen multiple pages.
4. Show install paths and exact release proposal before writing the client repository. After operator approval, run `scripts/install_kit.py --root CLIENT_REPO --approval-evidence 'reference to actual approval'`. It adds client skills for Codex and Claude Code and a managed README section, preserving existing instructions. Local installation does not commit, push or deploy. Read back generated files. Restart skill discovery if the current app requires it.

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
Apply rejects changed content, altered proposals, concurrent register updates and reused releaseIDs. Exact repeat application is idempotent. Read back client-review.json, CLIENT-REVIEW.md and the installed .lhm-review/client-config.json. Approved apply replaces the installed example with the verified proposal configuration when the kit is present. The register config remains authoritative. JSON is authoritative; `render --root CLIENT_REPO` repairs its derived checklist if needed. Report uncertain/failed writes and inspect the same paths before retrying.

## Invitation and publishing handoff
Offer a complete draft email to the verified client contacts using email-drafts. Include release summary, questions, registered repository/install instructions, verified previewURL if one exists, and this copyable prompt:

“Open my website repository and run review-website. Read .lhm-review/workflows.md and CLIENT-REVIEW.md. Start the local website safely, show the next page awaiting review, and guide me through the questions one page at a time. Let me edit with your help or open the real content file. Ask me before recording approval or sharing changes. Keep publication separate.”

Drafting does not send. Do not claim a release is available until its files are pushed under existing authority and deployment evidence is verified. Client-repo pushes, Issues, PRs and external communication each need actual authority; a preparation-only request grants none of them. Preview branch only by default. Do not push main, merge or publish production through finish-review. Respect real branch protection and authenticated user identity; no account-sharing or permission changes.

## Acceptance and handback
Verify installed skill entry points, safe local start, representative static/dynamic page mapping, one edit plus explicit approval, changed-page invalidation and repeated release preservation. Test preview sharing only with authority and actual provider evidence. Return repository/branch/commit, toolkitversion, release/register links, approved and pending pages, unanswered questions, excluded pages, coverage gaps, verified previewURL or precise deployment failure, and email draft state. Never describe untested Mac/Windows/app support as passed.

At session finish, run lhm-learn:learn if available. Capture verified outcomes and reusable gaps in existing records. Source improvements require existing source authority; merge/install remain separate. Keep client review feedback in their client record and reusable toolkit lessons in this owning skill.
