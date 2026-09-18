# Fresh evidence and regression checks

## Research contract

Use the agreed brief as a comparison baseline, not a frozen truth or independent source. Include Michael's later corrections (including no immediate Jaimee work unless newer evidence proves it). Read all pages of both core boards, but prefer targeted current-task/child/discussion reads over dumping entire personal boards. Follow replies and cross-board handoffs. A pagination cap, repeated cursor, missing current reply chain or unresolved read failure means incomplete coverage, not success.

Read relevant Gmail message bodies for every active project (start with 30 days; extend for missing approval/scope history). Carry their IDs, date, URL and relevant content into the evidence pack. Search results alone and previous Lily emails are not primary evidence. Read relevant recent Fathom transcript passages, particularly meetings since the last substantive project note. A canonical project note defines identity and durable scope but can be superseded by later explicit client/team decisions about that same scope.

Keep discovery separate from reporting: a historical open card is a cleanup candidate, not proof of current blocking work. Do not resurrect completed work, make an unknown status red, or add actions to a person solely because an old checklist mentions them. Preserve separate website versus LP scopes without duplicating the same work. Keep the approved concise main portfolio; additions require evidence of active work, not a quota or fixed client list.

Approval anchors: resolve the original CLIENT approval and scope from its primary evidence. If two dates might refer to different prototypes/page batches, record the conflict and use "Approval date to confirm"; do not silently move the deadline. Retain an agreed revised-date-needed state rather than promoting an old unverified field into a new missed commitment.

## Comparison contract

Save comparison.json with baseline path/hash and one entry per unchanged, added, removed or changed project. Each entry records prior state, proposed state, current evidence IDs and disposition. Explain any backward stage, completed task becoming open, new red blocker, changed owner, earlier target or newly assigned work. No change is valid merely because its older source was retrieved later. Carry over the factual meaning of Michael's corrections; newer contrary evidence must be explicit.

The 19 September failure provides acceptance cases, not permanent project facts:
- IPB: the August interview hold must not erase September V1 approval and revised-homepage feedback.
- EHP: a September design-review meeting must not disappear in favour of the older five-page gate.
- Heel Centre: an email reporting forms added must be reconciled before assigning that form build again; don't assume it closes unrelated hosting/Caulfield scope.
- mhealth: preserve the latest named follow-up and actual hold; old assignee titles cannot replace it.
- Jaimee: don't revive historical QA without a current unmet action.
- Alpha: conflicting approval dates require scope reconciliation, not an unexplained earlier estimate.

## Run files and delivery gate

Required files are brief.json, email.json, preview.html, research-receipt.json, comparison.json, access-receipt.json and quality-review.json. Keep primary evidence in the run folder (or stable paths), never in Git.

access-receipt.json: `worker` must be `codex-cli`; `skill_path` and `skill_sha256` identify the actual SKILL.md read; `sources` has gmail, obsidian and basicops entries, each `{status: "passed", evidence: "successful read ID/path and time"}`. Include meetings as passed or not_required with a reason. Record real worker reads, not controller-only probes.

research-receipt.json: include the normal per-project research fields from SKILL.md; additionally `coverage` contains gmail, obsidian, basicops and meetings, each `{status: "complete"|"not_required"|"incomplete", reason: "..."}`. Only meetings may be not_required. Gmail complete means relevant bodies read, BasicOps complete means both core boards and required current discussions/replies are covered (no unresolved cap). `material_gaps` is a list, empty to send. `evidence_files` is a nonempty list of `{path, sha256}` covering retained primary evidence. Do not mark complete merely to pass validation.

comparison.json: `baseline: {path, sha256}`, `projects: [...]`, `unresolved_regressions: []`. Baseline file must be the supplied human-approved brief/corrections, not the failed email. Scope additions and unchanged projects must be explicit.

The controller independently checks coverage, current facts and comparison against the primary sources, then writes quality-review.json: `accepted: true`, nonempty `reviewer`, `email_sha256`, `research_sha256`, `comparison_sha256`, `access_sha256`, and `issues: []`. The researcher must not self-author the controller's acceptance. SHA-256 values hash file bytes, not a reserialised object.

Run `python3 scripts/quality.py <run-directory>`. It verifies coverage, access, evidence/baseline hashes, no material gaps/regressions and review binding. This mechanical gate supports semantic review; it cannot itself prove that a writer interpreted evidence correctly. The normal send command calls it before any network submission. Keep failed attempts and original receipts; do not bypass the gate or erase dedup state.

Check actual body content after every Gmail read. Nested multipart messages can produce metadata with an empty body in the shared helper; use the read-only adapter in runtime.md before declaring the email missing. Record the body extraction route. Do not replace an unread primary message with an older summary.

When a temporary per-minute Gmail limit interrupts research, pace and retry within runtime.md's bounded policy before stopping. A failed attempt remains in the audit trail; mark coverage complete only after the affected reads actually succeed. Do not abandon an otherwise healthy source after one recoverable minute-limit response.
