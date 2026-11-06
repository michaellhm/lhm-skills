---
name: sales-handover
description: "Hand a newly closed client from Michael or Marlon into LHM delivery. Use after a sale closes or when the user says 'sales handover', 'handover to KP', 'we signed a client', 'closed a deal', 'new client handover', or 'hand this client over'. Captures sales context in canonical Obsidian records, drafts Michael's client introduction, creates one client-level card on the BasicOps *Client Onboarding board assigned to the applicable immediate owner, adds scope-applicable top-level checks, and hands the detailed workflow to client-onboarding."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Sales Handover

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the handover-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Capture what sales knows and start the approved Obsidian-first client-onboarding flow. Ask interview questions one at a time.

## Partner/Marlon clients — finance ownership and applicable tasks

For a client sold by Marlon, Marlon manages the finances. Record `Finance owner: Marlon` and `LHM billing: N/A — partner-managed` in the handover and onboarding note. Do not create or assign Josephine an invoice/payment task, introduce her as billing contact, request payment, or put the parent in Josephine's billing queue. This routing decision does not prove payment was received; keep receipt status unknown unless supported by evidence. Refer commercial questions to Marlon without making them an LHM billing gate.

For this route, start the parent in `2 — Client Contact & Strategy`, assigned to Kristalyn, unless verified progress places it in a later phase. Michael's introduction remains a separate applicable check. Apply this exception wherever the default below says Josephine, Payment & Billing or exactly seven subtasks. Preserve the five board phases and seven reference gates as the general model, but create only applicable tasks. Keep omitted gates in Obsidian with their reason; never mark unperformed work complete.

When Michael explicitly removes the separate `Purchased services kicked off` task, retain service-start readiness in the Obsidian completion checklist and link the actual delivery task instead. Do not recreate the removed card. A website sitemap/prototype task is a distinct delivery outcome owned by the confirmed strategist; it does not reinstate a generic kickoff card.

When reconciling an existing Marlon client, inspect the parent, billing task and discussions. Propose cancellation (not completion or deletion) of unnecessary open LHM billing work and reassignment of a billing-owned parent through basicops-task-manager. Preserve legitimate billing history and unrelated admin work. Do not bulk-change clients whose sales route is unverified.

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

Pull the recent sales call from Fathom when available and obtain the proposal or GHL deal notes. If the call cannot be retrieved, ask the salesperson for the notes and state the gap.

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

## 6. Create or migrate the BasicOps onboarding card

Use the BasicOps project `*Client Onboarding` (project ID `68921`), not `*Client Flow`.

1. Find a matching onboarding card on `*Client Onboarding` and search older client-flow tasks before creating anything.
2. Reuse or migrate the existing client-level task when one exists; never create a duplicate.
3. Title the parent card `[Client] — Client Onboarding`.
4. Place it in `1 — Payment & Billing`, assign it to Josephine and record Kristalyn as overall owner in the description.
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

BasicOps carries only these top-level checks, current phase, immediate owner and next action. Detailed, conditional checklists and evidence remain in Obsidian.

If BasicOps is unavailable, print the exact parent card and seven subtasks as manual instructions and leave the intended BasicOps write pending in the Obsidian onboarding log.

## 7. Draft communications

Prepare but do not send:

- Michael's client introduction email introducing Kristalyn and Josephine.
- Internal handover email to Kristalyn and Josephine, copied to Michael.
- Human-sent WhatsApp team notification.

Do not mark `Michael handover and client introduction completed` until the introduction email is explicitly confirmed sent.

## 8. Hand off

Finish with `Handover complete. Next: run lhm-project-hub:client-onboarding` and name the verified resume phase. For Marlon clients, use Client Contact & Strategy or the evidenced later phase, not the LHM billing queue.

## Rules

- Obsidian is canonical for detailed state and evidence; BasicOps is canonical for visible assignment, stage and next action; Google Drive holds assets and deliverables.
- Client-facing emails are drafts only.
- Tick items only after explicit human confirmation or successful system verification.
- Never fabricate dates, data, access or completion.
- Never create the same live onboarding or delivery task twice.
- Ask the sales interview questions one at a time.
