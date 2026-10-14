# Client website review toolkit — proposed design

Status: design for Michael review; not implemented, published or installed.
Source: Michael's 15 October daily-flow design discussion.

## Outcome
Let Alpha Sports Medicine and Essential Health Physio review actual website content locally with Codex or Claude Code, edit conversationally or in the underlying content file, explicitly approve pages and share verified preview changes and a concise LHM handback. Give the LHM team one reusable release-preparation skill rather than client-specific implementations.

## LHM release workflow
Proposed owning skill: lhm-wordpress-hub:client-review-release. It has initial setup and repeat release modes. Inspect actual repository instructions, route/content structure, Git status, package manager and deployment mapping. Resolve client identity and repository from verified context. Never force-reset local changes or guess production mappings.

An operator may request a specific batch, for example the next15 service pages, and supply questions per page or across the release. Scan actual publishable routes and compare with the existing review register. Identify new pages, modified approved pages, still-pending pages, renamed/removed pages and explicit exclusions. Dynamic routes, shared components, data sources and images must be included in the content dependency assessment; uncertain dependencies require review rather than claiming unchanged approval. Do not assume every page is Markdown.

Show a proposed release before applying it: exact page URLs and source files, reasons for inclusion, existing approval state, questions, missing mappings, explicit exclusions and proposed client invitation. Obtain operator approval for this concrete batch. Preserve pending work from previous releases; never overwrite it with the new batch. Excluded/unresolved pages remain visible in the operator report.

After approval, update the client review register, save the approved release scope and prepare the client notification email with a copyable launch prompt. Email remains draft-only until explicit sending approval. Never mark a notification sent from draft creation.

## Client toolkit
Proposed workflows: start-website, review-website, share-preview and finish-review. Use tool-specific discovery adapters for Codex and Claude Code with shared canonical instructions and tested behaviour. Natural-language prompts are supported as a fallback. Do not claim ordinary web chat can operate a local repository. Initial bootstrap must work before repository skills are discovered: README instructions and a copyable installation prompt.

Start checks prerequisites and authenticated repository access, preserves unfinished changes, safely syncs and starts the correct local site. Open the selected browser when supported; otherwise return the working URL. Provide tested Mac/Windows instructions, dependency versions and troubleshooting.

Review opens the next pending page, asks the release's specific questions and offers conversational edits or direct editing of the verified content source. Preview local changes before requesting approval. Keep page approval distinct from unresolved question answers and live publication permission.

Finish reconciles explicit user statements and saved changes, records approved/unfinished/needs-LHM states, saves authorised work to a review branch and prepares a concise copyable email. If sharing was not authorised or failed, preserve local state and report the exact next step. Never infer approval from edits, silence, elapsed time or a model's summary.

## Approval register
Use a machine-readable register as canonical client review state with a generated human-readable project/checklist view. Include schema version, stable page ID, route, content-source mapping, relevant dependency fingerprint, review state, release membership, explicit approver evidence, approved fingerprint, specific questions/answers and handback references. Keep client-facing records free of private LHM notes and credentials.

Approval applies to reviewed content, not merely an entire repository commit. Changed relevant content invalidates approval; unrelated changes do not. Question answers alone do not approve a page. Renames must preserve identity only when verified; deletions and conflicts require deliberate reconciliation. Repeated release generation is idempotent.

## GitHub and Cloudflare
Pilot default: review branch and pull request, verified Cloudflare preview, LHM review before production merge. Publishing to main is a separate explicit action; finish does not imply live publication. The actual GitHub-to-Cloudflare connection, production branch and allowed preview branches must be verified per client. Wait for successful deployment and verify the returned URL/content before claiming a shared preview exists. Preserve deployment failures as incomplete.

GitHub Issues capture concrete blockers/change requests, deduplicated against existing issues and created only with authority. They are not the approval register. BasicOps retains internal execution owners/status; link external issues without creating a competing task board. No automatic new permissions, account sharing or schedules.

## Pilot scope and acceptance
Implement reusable source toolkit first; rollout to Alpha/EHP is a separate application step against their verified current repositories. Exercise one page and one question in Alpha, then EHP. Demonstrate clean setup, safe resume with local edits, conversational/direct content edits, explicit approval, changed-page invalidation, selected15-page release discovery with omitted-page reporting, preview success/failure, repeat-run deduplication and accurate unsent email handback. Test both supported operating systems/apps before claiming that coverage; report unavailable environments explicitly.

## Delivery boundaries
Canonical LHM skill source: /Users/michaelcolman/Documents/LHM Plugin V3. Preserve unrelated local edits. Source delivery includes scoped validation, catalogue/version checks, feature-branch commit/push and verified GitHub evidence under Michael's standing authority. Merge/install/client-repository application and production publication remain distinct. No live client changes have been authorised by this design document.
