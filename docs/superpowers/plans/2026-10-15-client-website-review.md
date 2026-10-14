# Client Website Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Native execution proposed; no delegation until selected by Michael.

**Goal:** Ship a reusable LHM review-release skill with an installable client toolkit and verified release/approval handling.

**Architecture:** One WordPress Hub skill owns setup and repeat review releases. A dependency-free Python utility owns inventory/register generation and approved-plan application; thin Claude/Codex adapters share client workflow instructions. GitHub/Cloudflare actions remain agent-orchestrated with explicit authority and provider evidence.

**Tech Stack:** Python3 standard library, JSON, Markdown, Astro repository inspection, Git, existing authenticated GitHub/Cloudflare routes.

**Spec:** ../specs/2026-10-15-client-website-review-design.md

## Global Constraints
- Canonical source is /Users/michaelcolman/Documents/LHM Plugin V3; origin michaellhm/lhm-skills.
- Preserve unrelated edits and use an attached isolated worktree from verified remote default base.
- No forced Git reset, fabricated page coverage, credentials in files or implicit approval.
- Finish saves review work; production publication requires its own explicit approval.
- Client email is draft-only; Issues require creation authority and deduplication.
- Record supported versus untested Mac/Windows and Codex/Claude environments accurately.
- Source commit/push authorised; merge, installation and live client rollout remain separate.

## Review Focus
1. Dynamic routes cannot be discovered reliably by filename: unresolved patterns must remain visible and prevent full-coverage claims.
2. Shared content changes affect multiple pages: include verified dependency hashes or invalidate conservatively.
3. Dirty/concurrent local edits must survive start and register application.
4. Release reruns must preserve approvals, answers and outstanding old-release work.
5. A failed deployment or denied push must never produce a fabricated preview URL or sent-email claim.

## Files and responsibilities
All toolkit files below are under plugins/lhm-wordpress-hub/skills/client-review-release/.
- SKILL.md: LHM operator workflow and approval gates.
- scripts/review_release.py: inventory, proposal, guarded apply and rendered project checklist.
- references/register-contract.md: schema, fingerprints, explicit approval evidence and reconciliation rules.
- references/client-workflows.md: portable client start/review/share/finish behaviours.
- assets/client-config.example.json: documented configuration without real client data.
- assets/README-client.md: bootstrap instructions, first-use prompt and troubleshooting.
- assets/skills/{start-website,review-website,share-preview,finish-review}/SKILL.md: thin discoverable client entry points.
- tests/test_review_release.py: temporary-repository acceptance fixtures.
- agents/openai.yaml: operator skill discovery metadata.
Catalogue/version changes: README.md, plugins/lhm-marketing-hub/agents/marketing-assistant.md, plugins/lhm-wordpress-hub/.claude-plugin/plugin.json and .claude-plugin/marketplace.json. Inspect validators for any additional generated manifests. Repository instructions mention absent .Codex-plugin paths; use existing .claude-plugin manifests, do not invent duplicate metadata.

### Task1: Inventory and review proposal
**Interfaces:** inventory(root: Path, config: dict) -> dict; propose(inventory: dict, register: dict, release: dict) -> dict. CLI `scan --root PATH --config PATH --output PATH` writes a proposal without changing the client register.
- [ ] Read Astro route/content conventions and repository-local skill instructions. Build fixtures for staticAstro pages, Markdown content, collection-generated routes and explicitly mapped dependencies.
- [ ] Write failing tests named test_static_routes, test_dynamic_routes_report_gap, test_shared_dependency_change and test_exclusions_visible. Use temporary directories and real bytes, not network calls.
- [ ] Run `python3 -m unittest discover -s plugins/lhm-wordpress-hub/skills/client-review-release/tests -v`; confirm failures before implementation.
- [ ] Implement deterministic inventory, SHA256 content/dependency fingerprints and proposed release selection. Dynamic/unmapped files are explicit gaps requiring operator mapping; never silently omit them. Proposal lists source paths, routes, reasons, exclusions and questions.
- [ ] Rerun tests; check new15-page batch selection contains exactly configured scope while reports retain uncovered pages.

Example fixture assertion to pin the interface:
```python
with TemporaryDirectory() as folder:
    root = Path(folder)
    (root / 'src/pages').mkdir(parents=True)
    (root / 'src/pages/index.astro').write_text('<h1>Home</h1>')
    result = inventory(root, {'pages': []})
    self.assertIn('/', [p['route'] for p in result['pages']])
```

### Task2: Guarded apply and persistent approvals
**Interfaces:** apply_proposal(root: Path, proposal: dict, approval: dict) -> dict; render_project(register: dict) -> str. CLI `apply --root PATH --proposal PATH --approval PATH` requires matching proposal digest and explicit operator decision.
- [ ] Write failing tests test_unapproved_apply_refused, test_stale_proposal_refused, test_repeat_release_idempotent, test_changed_approved_page_reopens and test_unrelated_change_keeps_approval.
- [ ] Reject missing approval/digest mismatch, changed content since proposal, unsafe paths and concurrent register changes. Use atomic writes after validation. Record approval source and selectedrelease; preserve prior answers and pending items.
- [ ] Define schema1 with stable page IDs, routes, content sources, fingerprints, explicit approver evidence, states, questions and release membership. Generate CLIENT-REVIEW.md from canonical client-review.json.
- [ ] Test deleted/renamed pages and unresolved dependency mapping; preserve history and report reconciliation rather than guessing identity.
- [ ] Rerun the complete fixture suite and inspect readable checklist output.

### Task3: Installable client workflows and release handback
**Interfaces:** operator consumes verified inventory/config and approved proposal; client workflows consume client-review.json and actual repository/deployment state. Shared instructions are canonical; tool-specific adapters only handle skill discovery/invocation.
- [ ] Write SKILL.md setup/release modes, routing, approval list, preview-first policy and draft invitation with a ready-to-copy launch prompt.
- [ ] Add four client skills and shared instructions: safe start; onepage/question at a time; conversational versus verified source-file editing; explicit approval; sharepreview through branch/PR; finish reconciliation and copyable email.
- [ ] Add README bootstrap before skills exist, Mac/Windows prerequisite guidance, actual package-manager detection, browser fallback, authentication troubleshooting and unsupported ordinary webchat explanation.
- [ ] Ensure setup installs only approved client-facing files, preserves existing AGENTS.md/CLAUDE.md/README content and records toolkitversion. Maintain one canonical register across tools and reopen skills after installation when required.
- [ ] Define deployment handback fields: branch, commitSHA, PRURL, provider result, verified previewURL, changes, approvals and blockers. Denied/failed actions retain incomplete status; uncertain writes checked before retry.
- [ ] Add acceptance fixtures for existingfile preservation, no private source leakage, deploymentfailure handback and skilladapter parity. No credentials or client data in templates.

### Task4: Validation and source publication
- [ ] Review all LEARNED.md entries as repository instructions require; preserve unrelated learnings and present any additional absorption scope for approval before modifying it.
- [ ] Update WordPress Hub patchversion in existing manifests, READMEcounts/tree/catalogue and marketing-assistant catalogue. Count actual shipped operator skills separately from embedded client templates.
- [ ] Run the affected unittest suite, `python3 scripts/validate-plugin-versions.py` and `python3 scripts/validate-script-parity.py`; validate frontmatter and generated kit paths.
- [ ] Inspect complete diff, check secrets/private-context leakage and verify unrelatedfiles are absent from staging.
- [ ] Commit only reviewed allowlistedfiles; push featurebranch via existing authenticatedGitHub route; verify remoteSHA. Open/attach PR if supported by existing route. Do not merge/install.
- [ ] Return verifiedGitHublink, checks, actual platform coverage and exact installation/pilot nextstep. Alpha/EHP application must inspect each current repository, content mappings and Cloudflareconnection first.

## Execution and pilot handoff
Recommended native execution in this chat because the register utility and client instructions share a small, tightly coupled contract. Review the plan before implementation. Alpha/EHP live setup is subsequent approved work, not evidence that the generic toolkit works on their current sites. No automatic email, issue creation, production merge or schedule.
