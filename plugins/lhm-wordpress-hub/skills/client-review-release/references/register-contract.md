# Client review register

The client repository owns client-review.json (schema_version1) and its generated CLIENT-REVIEW.md. The register stores verified client name/config, pages and releases. Every page has stable id, route, sources, dependencies, fingerprint, review status, questions, answers, release membership and explicit approval evidence. Approval records include person, evidence, timestamp and approved_fingerprint. Old approvals/answers remain history when content changes. Do not store full chats, patient data, internal notes or secrets.

States: awaiting-review, changes-underway, approved, needs-lhm, needs-reconciliation. Editing or answering is not approval. Explicit approval applies only to content the person reviewed; all outstanding questions need answers or a needs-lhm disposition. Revisions are fingerprinted over actual source/dependency bytes. Unrelated files outside mapped dependencies do not invalidate approval. Conservative default includes all src files; complete verified mapping permits narrower invalidation. External data changes cannot be proven from file hashes; expose that limitation.

Release input example:
```json
{"id":"services-round-1","routes":["/services/physiotherapy/"],"questions":["Is this description accurate?"],"page_questions":{"/services/physiotherapy/":["Is this appointment length correct?"]},"exclude":[]}
```
Use a new release id for a changed batch. scan does not apply changes. apply requires explicit operator approval matching the proposal digest and unchanged source/register. Release questions merge with prior pending questions. Removed pages remain needs-reconciliation; verify rename identity manually before editing mappings. Approval source must be a real decision, not an assistant assertion.

CLI review uses --page-id, --status, --person, --evidence and --answers (a JSON object keyed by actual question). After local edits, use fingerprint --page-id to obtain current hash, preview that exact content, obtain explicit decision and pass --fingerprint to review. Recheck if bytes change before saving. Changed shared dependencies reopen other affected approvals. JSON is canonical; render repairs only its Markdown view. A lock prevents simultaneous writers; inspect a stale lock and confirm no writer exists before authorised recovery. Do not delete another session's active lock.
