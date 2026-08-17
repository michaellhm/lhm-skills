---
name: client-onboarding
description: "Run LHM's resumable new-client onboarding workflow. Use when the user says 'client onboarding', 'onboard [client]', 'continue onboarding', 'where is onboarding up to', 'billing setup', 'strategy call', 'client access', 'tracking setup', or 'service kickoff'. Reads and updates the detailed, scope-aware Obsidian onboarding checklist first, then mirrors only five top-level phases and seven top-level checks to the BasicOps *Client Onboarding board: Payment & Billing, Client Contact & Strategy, Access Assets & Config, Service Kickoff, and Onboarding Complete."
---

# Client Onboarding

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the onboarding-specific payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Resume a newly sold client's onboarding from canonical Obsidian state. This workflow is service-neutral: generate detailed checks from what the client purchased rather than assuming Google Ads, Maps, GoCardless or any other service applies.

## 1. Load canonical state

Follow `references/folder-convention.md`. Read, in order:

1. `20 Clients/<Client>/Current Projects.md`.
2. `20 Clients/<Client>/project-management/Handover YYYY-MM-DD.md`.
3. `20 Clients/<Client>/project-management/Onboarding.md`.
4. The relevant purchased-service project files.

If `Onboarding.md` does not exist, instantiate it from `references/checklists/client-onboarding.md`, the handover and purchased scope. Preserve the instantiated checklist as the client's detailed execution state; future reference changes must not silently rewrite it.

Obsidian is authoritative when detailed state disagrees with BasicOps. Report the mismatch and reconcile BasicOps only after confirming the Obsidian evidence.

## 2. Confirm the BasicOps parent card

Use `*Client Onboarding` (project ID `68921`). Find the client-level card and its subtasks. Search for and migrate an older `*Client Flow` onboarding card before creating a new one.

The parent card must:

- Be titled `[Client] — Client Onboarding`.
- Be assigned to the owner of the immediate next gate while Kristalyn remains overall onboarding owner in Obsidian and the description.
- Sit in the section matching the canonical Obsidian phase.
- Contain one next action, one blocker or `none`, the Obsidian onboarding path and Google Drive client folder.

Create or reuse exactly seven top-level subtasks:

1. Michael handover and client introduction completed.
2. Invoice and payment setup completed.
3. Kristalyn welcome email and strategy call completed.
4. Required access and assets confirmed.
5. Tracking and configuration confirmed.
6. Purchased services kicked off.
7. Client onboarding completed.

Do not copy the detailed Obsidian checklist into BasicOps.

## 3. Resume the first unresolved phase

Use the first incomplete canonical phase:

### 1 — Payment & Billing

Immediate owner: Josephine.

Work the applicable billing checks in Obsidian. GoCardless is conditional, not universal. Michael's handover/introduction check runs in parallel but is also required to leave Phase 1. Advance only when both top-level checks are verified, or an explicit Michael-approved exception is recorded.

Kristalyn may work on her welcome and scheduling actions in parallel, but the parent card remains assigned to Josephine while billing is the immediate blocking gate.

### 2 — Client Contact & Strategy

Immediate owner: Kristalyn.

Draft the welcome email for review. Kristalyn schedules and coordinates the strategy call; include Michael when strategic decisions require him.

Before the call, create or reuse one nested BasicOps preparation task beneath `Kristalyn welcome email and strategy call completed`:

- Title: `<CLIENT LABEL>: Onboarding - Prepare playbook strategy session`.
- Invoke `lhm-marketing-hub:playbook-strategy-session` to read the client context and create the tailored themed meeting pack and ChatGPT/Hermes meeting-coach prompt.
- Assign Michael when the handover or canonical client record says he owns strategy or will lead the session.
- Assign Kristalyn when preparation or facilitation has been explicitly delegated to her.
- If ownership is not evidenced, do not guess. Make confirming whether Michael or Kristalyn owns preparation the first next step and leave the task uncreated until the owner is resolved.
- Use a confirmed internal preparation deadline when one exists. If only the meeting date is known, do not invent a due date; record that the pack must be reviewed before the call and leave the BasicOps due date unset pending an authorised date.
- Put the meeting pack, coach prompt and useful canonical source links in the task Description only as working URLs. Put the outcome, ordered steps, owner/handoff, dependencies and completion condition in Discussion.
- Treat the task as complete only when the tailored pack and prompt are saved, linked and ready for the session owner to review.
- On completion, hand off to the person leading the strategy call through the confirmed team channel.

Route the task through `lhm-project-hub:basicops-task-manager`. Use stable key `basicops:<client-slug>:onboarding:prepare-playbook-strategy-session`, deduplicate before creating, add its verified native BasicOps link to a clearly labelled linked-subtasks list in the strategy subtask's Discussion, verify the complete record, and ask whether the user wants it moved to the assignee's individual board. Never move it automatically.

Complete the call, record decisions in Obsidian, and create or link the client campaign/project record—the canonical project brief or service record that converts those decisions into delivery scope. Mark the BasicOps top-level check complete only after the preparation task, strategy call, recorded decisions and campaign/project record are verified.

### 3 — Access, Assets & Config

Immediate owner: Kristalyn for coordination; Jaimee or the applicable specialist owns technical checks.

Generate and work only the access, asset and configuration items required by purchased services. Verify access directly where connected tools allow. A request sent is not verified access. Record missing items with an owner and follow-up date. If no tracking/configuration branch applies, complete that top-level gate only after a human confirms and Obsidian records `N/A — no tracking/configuration required for purchased scope`.

### 4 — Service Kickoff

Immediate owner: Kristalyn.

For every purchased service:

- Run the applicable Project Hub kickoff skill.
- Create or identify its destination-board task.
- Confirm delivery owner, initial schedule and next action.
- Connect Obsidian, BasicOps and Google Drive records.
- Record an explicit deferral reason when a purchased service cannot start.

The onboarding card may overlap with destination tasks during this gate, but it must not repeat their delivery checklist.

### 5 — Onboarding Complete

Immediate owner: Kristalyn.

Complete only when every purchased service is underway or explicitly deferred and all earlier top-level gates are verified. Record the completion date in Obsidian, move the parent card to `5 — Onboarding Complete`, complete the final top-level subtask and parent card, and hand first-30-day client success to its follow-on checklist or recurring rhythm.

## 4. Work detailed items safely

For each detailed Obsidian item:

- Prepare drafts or tool actions first.
- Tick only on explicit human confirmation or successful system verification.
- Mark conditional items `N/A — <reason>` only after applicability is confirmed.
- Log the date, result and verification method.
- If a tool fails, leave the item open, record the failed write or verification and name who must retry.

Client-facing emails remain drafts until a human sends them.

## 5. Mirror only top-level operational state

After a verified gate change:

1. Update `Onboarding.md` and `Current Projects.md` first.
2. Update the matching BasicOps top-level subtask.
3. Move the parent card to the new section.
4. Reassign the parent to the immediate next owner.
5. Update the parent description with the new phase, next action and blocker.

If the BasicOps update fails, keep the canonical Obsidian state, record the pending reconciliation and tell Kristalyn.

## Rules

- Rule of thumb: detailed, conditional checklists, evidence and applicability decisions live in Obsidian; BasicOps holds top-level gates, current phase, immediate owner and next action.
- Do not force Tier 1 Ads/Maps checks onto website-only or other differently scoped clients.
- Do not create duplicate onboarding or destination tasks.
- Keep the playbook strategy-session preparation task nested beneath the existing strategy-call top-level subtask; never add it as an eighth top-level onboarding gate.
- Credentials are references only, never plaintext.
- Never fabricate data, access, dates or completion.
- Instantiated client checklists are version-stable; propose reference improvements separately rather than silently rewriting active onboarding files.
