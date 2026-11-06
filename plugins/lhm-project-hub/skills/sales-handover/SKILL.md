---
name: sales-handover
description: "Hand a newly closed client from Michael or Marlon into LHM delivery. Use after a sale closes or when the user says 'sales handover', 'handover to KP', 'we signed a client', 'closed a deal', 'new client handover', or 'hand this client over'. Starts with Fathom and email evidence, reconciles canonical Obsidian records, reviews client and internal emails before creating one client-level card on the BasicOps *Client Onboarding board assigned first to Josephine, adds seven top-level checks, and hands the detailed workflow to client-onboarding."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Sales Handover

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the handover-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Capture what sales knows and start the approved Obsidian-first client-onboarding flow. Ask interview questions one at a time.

## Run order — evidence before communication before tasks

Follow this order, resuming existing work rather than repeating completed steps:

1. Read all supplied Fathom links and relevant client email threads/attachments.
2. Reconcile and save the evidence, decisions and open questions in canonical Obsidian records.
3. Draft the client welcome/introduction and internal team handover in editable email blocks for Michael's review.
4. Incorporate Michael's edits; send only when explicitly authorised. Record verified sends and final owner/scope decisions in Obsidian.
5. Create or update the deduplicated BasicOps cards from the reviewed brief, with clear owners, completion conditions, handoffs and confirmed due dates.
6. Read back the tasks and update Obsidian again with actual card URLs, boards, owners, dates, sent-email links and unresolved blockers.
7. Provide a short human-sent team announcement.

Do not create the task tree before the communication briefs have been reviewed unless Michael explicitly requests earlier creation. Sending is a separate decision: reviewed drafts can support authorised task creation even if sending is deferred. Do not stop at a draft when the user has already authorised sending. Do not claim the handover is complete while required evidence or package confirmation is still outstanding.

## 1. Confirm the sale

Confirm the client name, purchased services, fee, add-ons, payment arrangement and whether the client is genuinely new to LHM. Validate standard recurring pricing against `references/team-roster.md`; preserve explicitly agreed exceptions and flag contradictions rather than silently correcting them.

If an existing client has bought a new project, do not run new-client onboarding. Create an internal project handover and route to the applicable service kickoff.

## 2. Create or locate canonical Obsidian records

Follow `references/folder-convention.md`. Use the LHM Obsidian vault, not Google Drive Markdown, for durable context and state:

- `20 Clients/<Client>/<Client>.md`
- `20 Clients/<Client>/Current Projects.md`
- `20 Clients/<Client>/Goals.md`
- `20 Clients/<Client>/project-management/Handover YYYY-MM-DD.md`
- `20 Clients/<Client>/project-management/Onboarding.md`

Google Drive remains the asset, working-file and deliverable store. Never copy credentials; reference the approved password-manager entry.

## 3. Gather sales evidence

Start with every Fathom link Michael supplies: original sales calls, subsequent discovery/onboarding calls and any later scope discussion. Retrieve summaries/transcripts as available and preserve source links/dates. Reconcile later decisions against earlier sales claims; do not overwrite their provenance.

Search relevant client and salesperson email correspondence, including sent mail, proposal/signature threads, scheduling, asset submissions and package clarifications. Read full relevant messages and supported attachments, not just snippets. Verify what Marlon has actually sent or arranged before asking him to do it again. A promise to send is not a sent document; a client's statement that they signed is not the retrieved agreement. A tag on a website is not proof of an active advertising campaign.

Obtain the signed agreement/proposal or GHL deal notes when available. Explicitly confirm one-off versus recurring services, fees, GST, payment arrangement, add-ons and whether GBP optimisation includes GBP posts (and frequency, duration, fees and owner if applicable). If unavailable, save the evidence already supplied, record the missing item and assign its confirmation to the salesperson via the reviewed internal handover. Continue independent work without inventing scope or repeatedly asking Michael for an answer he has deferred.

Save meeting records, email evidence, attachment review notes, material decisions and outstanding actions in Obsidian. Originals/assets remain in the verified work folder or their original email location, linked from Obsidian; do not duplicate full deliverables in knowledge notes. Record unread or inaccessible attachments honestly.

Interview the salesperson, one question at a time:

1. What exact promises or commitments were made?
2. What client communication preferences or quirks matter?
3. What risks or sensitivities should delivery know?
4. What has the client tried before, and why did it fail?

Keep important wording close to verbatim. Ask follow-ups when an answer is thin.

## 4. Write the handover

Use `references/templates/handover-doc.md`. Record:

- Package, fee, add-ons and payment arrangement.
- One block per purchased service with an explicit success outcome.
- Client contacts and approval path.
- Promises, risks, preferences and failed prior approaches.
- Access references without secrets.
- The first three dated actions.
- Kristalyn as overall onboarding owner, Josephine as the first operational owner, and Michael's retained decisions.

Merge confirmed facts into the client overview and Goals without overwriting conflicting existing content. Record unresolved contradictions explicitly.

## 5. Initialise the detailed Obsidian onboarding checklist

Create or update `project-management/Onboarding.md` from `references/checklists/client-onboarding.md`.

- Include all universal checks.
- Include only service-specific access, configuration and kickoff checks that apply to the purchased scope.
- Mark confirmed non-applicable branches with the reason; never silently omit uncertainty.
- Record the five top-level phases and the seven top-level gates separately from the detailed checklist. Treat Michael's handover/introduction and Josephine's payment setup as the two parallel checks required to leave Phase 1.
- Set the current phase to `1 — Payment & Billing`, overall owner to Kristalyn and immediate owner to Josephine.

Update `Current Projects.md` with separate `Overall owner: Kristalyn` and `Immediate owner: Josephine` fields, plus the current phase, next action and onboarding-note link.

## 6. Review communications before BasicOps creation

Prepare the client welcome/introduction and internal team email as editable drafts in the user's editor/chat, never only as a Gmail draft or saved file. Use the exact latest user-edited text. Resolve recipient addresses from evidence; include Marlon and applicable delivery specialists when requested. Sending requires explicit authorisation; verify SENT and retain the message link when authorised.

- Client email: thank them, acknowledge supplied materials, state the agreed next deliverable and review sequence, introduce the actual coordination/specialist owners and consolidate scope-applicable access requests.
- Internal email: concise client brief, separate owner responsibilities, useful meeting/file/client-email links and a direct request for Marlon to resolve missing signed-package details, including GBP posts when uncertain.
- Keep credentials out of emails/notes; use account invitations and approved access references.
- For a website, preserve Michael's chosen sequence (for example homepage first, approval, further page samples, then Aiya's Astro build). Do not assume this sequence for every client.
- Distinguish access coordination from implementation: Kristalyn coordinates required website/domain/analytics/GBP/booking access and hosting preparation; the applicable specialist owns tracking implementation/tests. Request only applicable systems. Cloudflare, Cliniko, forms, live chat and Ads are conditional, not universal requirements.

After review/send, update Obsidian with final scope/owner decisions and draft-versus-sent status before writing the tasks. A sent introduction clears only that checklist item; it does not prove package, billing, access or full handover completion.

## 7. Create or migrate the BasicOps onboarding card

Use the BasicOps project `*Client Onboarding` (project ID `68921`), not `*Client Flow`.

1. Find a matching onboarding card on `*Client Onboarding` and search older client-flow tasks before creating anything.
2. Reuse or migrate the existing client-level task when one exists; never create a duplicate.
3. Use the shared task-manager title standard: `<CLIENT LABEL>: Onboarding - Coordinate client onboarding`. Do not invent an abbreviation.
4. Place it in `1 — Payment & Billing`, assign it to Josephine and record Kristalyn as overall owner in metadata and Discussion. Keep Description to governed metadata and useful working URLs; put the human brief, canonical path, next action and blockers in Discussion.
5. Link the canonical Obsidian onboarding path and Google Drive client folder.
6. State one immediate next action and exact blocker or `none`.

Create or reuse exactly these top-level subtasks:

- Michael handover and client introduction completed — Michael.
- Invoice and payment setup completed — Josephine.
- Kristalyn welcome email and strategy call completed — Kristalyn.
- Required access and assets confirmed — Kristalyn.
- Tracking and configuration confirmed — Jaimee or the applicable specialist.
- Purchased services kicked off — Kristalyn.
- Client onboarding completed — Kristalyn.

BasicOps carries these top-level outcomes, current phase, immediate owner and next action. Detailed, conditional checklists and evidence remain in Obsidian. Reuse the applicable gate as an actionable owner card when Michael approves a specific brief (for example access/Cloudflare/package coordination or form/chat/Cliniko tracking); preserve the parent link and gate mapping rather than creating duplicate work. Create/reuse a separate Michael sitemap/prototype outcome card when requested. Do not create one task per page or checklist line.

Capture a due date for each actionable owner card from Michael or a canonical commitment. Resolve relative dates using the client's current date/timezone; apply a shared deadline only to the cards explicitly covered. If a date is missing, ask one concise scheduling question after presenting the concrete briefs, or leave it explicitly unset when Michael defers it. Do not silently apply today's deadline, infer dates from a date range or reuse an unrelated card's date. A vague “end of next week” remains an unconfirmed date until reconciled.

Use the verified personal-board Inbox when Michael requests it; otherwise follow the task-manager's separate personal-board movement question. Keep the linked-task history on the parent. Never mark a gate complete from card creation, assignment, sending an access request or a draft email.

If BasicOps is unavailable, print the exact parent card and seven subtasks as manual instructions and leave the intended BasicOps write pending in the Obsidian onboarding log.

## 8. Reconcile final state and hand off

Read every changed task back for title, parent/link, board/section, assignee, due date, metadata, Discussion and URL. Update overview, Goals (or record unchanged), Current Projects, handover, onboarding and affected service notes as applicable. Replace stale “unsent”, “unset” and “not assigned” summaries when verified evidence supersedes them; preserve useful dated history without leaving contradictory active state. Record failed/pending writes, missing agreements, package questions and unverified access explicitly. Do not infer that a salesperson has replied because an email was sent.

Provide the client/internal email and task links plus the immediate next action/owner. Finish with the actual current status: use “Handover prepared — <remaining evidence>” when required confirmation remains, and “Handover complete” only when it is complete. Point to `lhm-project-hub:client-onboarding` and its first unresolved phase; do not always reset it to Payment & Billing.

Offer a short copyable team/WhatsApp announcement naming the client, workstream, immediate owners and next step. It is human-sent unless the user separately authorises distribution.

## Rules

- Obsidian is canonical for detailed state and evidence; BasicOps is canonical for visible assignment, stage and next action; Google Drive holds assets and deliverables.
- Emails start as drafts for review; sending requires explicit user authorisation. Never resend an already verified sent message merely because the workflow resumes.
- Tick items only after explicit human confirmation or successful system verification.
- Never fabricate dates, data, access or completion.
- Never create the same live onboarding or delivery task twice.
- Ask the sales interview questions one at a time.
