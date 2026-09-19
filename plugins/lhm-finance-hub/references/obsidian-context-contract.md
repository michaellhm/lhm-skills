# Client knowledge and working-file routing

This contract applies to client work in Hermes, Claude/Cowork, Codex and local projects. It takes precedence over legacy examples that use one generic `client folder`. Preserve separate workflow approvals and confidentiality boundaries.

## Resolve two destinations before work

1. **Knowledge:** the active shared **LHM Knowledge** Obsidian vault, `20 Clients/<verified client name>/`. Its physical location is the LHM Knowledge Google Shared Drive on desktops, or a verified mirror on Hermes. Resolve the actual available root; do not hard-code Michael's Mac path on another computer, assume a staging copy is active, or fall back to the retired combined/private vault.
2. **Work:** **Claude Workspace / Current Clients / <verified existing client folder>/** on Google Drive. Resolve the registered folder ID or existing local folder and verify its ancestry. Client display names, slugs and working-folder names may differ. Preserve the confirmed mapping; do not derive a folder from a name alone.
3. Keep `knowledge_root` and `work_root` distinct in the run context and worker handoff. A file being Markdown does not decide its destination. A `.md` copy deck is work; a `.md` client profile is knowledge. The shared vault is itself on Drive, but it is not the deliverables folder.
4. Use the canonical client overview's verified Systems and files links or registered mapping first. If a registered client work folder is outside Current Clients, report the stale mapping and resolve the intended destination before writing; do not silently keep writing to it or move it automatically. Match only within Current Clients when discovering an active client. Multiple candidates, missing mounts or unavailable vault access are explicit gaps, not permission to create a fallback at the workspace root, current directory or plugin folder.
5. Prospect work stays in its verified prospect location until onboarding explicitly promotes it; LHM internal work stays in its verified internal location. Do not invent a paying-client folder for either.

## Knowledge reads and writes

Read the canonical overview, existing profile, Goals.md, Current Projects.md and relevant `project-management/` notes before client work. Legacy `client_profile.md`, `goals.md`, `current-projects.md` and `project-management/` references resolve inside the knowledge client root, with existing case and names preserved. If an overview and profile both exist, preserve their distinct purposes and reconcile affected facts without making another copy. Existing work-folder context is migration evidence, not a parallel source to keep updating; surface conflicts instead of overwriting newer facts.

After authorised client work, update the existing appropriate knowledge record with evidenced changed facts, decisions, goals, targets, status, constraints, next action/owner and verified deliverable links. This routine context handback is part of the client task; do not ask a redundant generic “save to Obsidian?” question. Do not fabricate progress, goals or completion. Respect any narrower review-only or hash-bound workflow; preparing a meeting bundle is not applying it. Missing canonical records go to the authorised onboarding, kickoff or client-update owner; do not create blank profiles in working folders.

## Deliverables

Save briefs, copy, audits, reports, research exports, designs, code/build files and assets under the verified work root using the existing service structure and applicable `skill_name/YYYY-MM/` convention. Temporary local/VPS output is staging until its durable destination is verified. Do not create `Claude Workspace/<client>/`, `Current Clients/Current Clients/`, or a new alias alongside an existing client. Do not duplicate complete deliverables in Obsidian: save a concise durable result and the verified working link there. Detailed executable task state stays in BasicOps.

## Meeting completion

For an approved meeting capture, explicitly assess the meeting record, client overview/profile, Goals.md, Current Projects.md and each affected service/project note. Apply only evidenced changes, record source meeting/date and report each item as updated, unchanged or blocked. Missing context or a failed vault application must remain visible; a drafted email or created task does not mean client knowledge was updated. Preparation-only workflows propose these changes and apply them only through their existing separate approval operation. Sending mail, distribution, live account changes and publication retain their own authority rules.

## Verify and hand off

Read back every changed canonical record and material deliverable destination. Return the knowledge paths, work links and any unresolved routing/record gaps. Never silently claim a two-root workflow works when one root is unavailable. Do not copy private founder planning, personal finance, credentials, or staff-private material into shared client records. Access to a private vault does not authorise disclosure to a team vault. Folder moves, merges, bulk reconciliation, sharing changes and deployment are separate from this routing contract.
