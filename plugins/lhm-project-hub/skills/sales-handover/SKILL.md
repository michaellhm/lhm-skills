---
name: sales-handover
description: "Hand a newly closed client from Michael or Marlon into LHM delivery. Use when the user says 'sales handover', 'handover to KP', 'we signed a client', 'closed a deal', 'new client handover', or 'hand this client over'. Investigates sales, strategy and existing systems first; prepares the internal handover before the client introduction; then prepares the detailed onboarding process and lean BasicOps tasks for review. Preserves partner-managed finance, existing accounts, separate send/task approvals and verified handoffs."
---

# Sales Handover

Read [client knowledge and working-file routing](../../references/obsidian-context-contract.md) first. Knowledge belongs in the verified shared LHM Knowledge client records; deliverables belong in the separate verified Claude Workspace / Current Clients work folder. Never copy credentials into either. Route every BasicOps mutation through `lhm-project-hub:basicops-task-manager` and email preparation through the matched `lhm-inbox-hub:email-drafts` helper.

## Default order and authority

Use this order unless the user explicitly changes it:

1. Investigate the sale, completed interviews, client records and existing systems.
2. Prepare the internal handover email; open it in the editor and review the wording with Michael.
3. Send the latest approved internal text only on explicit instruction; verify SENT and recipients.
4. Build the client introduction from that approved handover; open it in the editor for separate review and send only on explicit instruction.
5. Prepare the detailed onboarding process and exact BasicOps task proposals for review.
6. Create or update only the approved tasks, then verify them. Agree due dates and board/owner changes separately when not already supplied.

If the user wants preparation only, draft the sequence without sending or writing tasks. Do not require a send just to continue authorised preparation. Approval of one email does not approve the other or the task batch. An explicit send instruction authorises the latest approved text through a supported send tool; do not substitute another unsent draft. Refresh sent history before retrying an uncertain send. Preserve manual edits exactly. Never send a WhatsApp/team notification merely because handover is mentioned.

## 1. Investigate before interviewing

Confirm the client identity, genuinely new versus existing client, salesperson, purchased services, add-ons and relevant promises. An existing client's new project routes to an internal project handover and the applicable kickoff, not duplicate new-client onboarding.

Read the existing overview/profile, Goals, Current Projects, handover, Onboarding and purchased-service records. Follow `references/folder-convention.md` and locate existing records before creating them. Resolve the work folder by verified mapping/ancestry, not client-name guesswork. If unavailable, continue permitted evidence review and show an editor draft, but report temporary staging and the unresolved durable destination; never invent a production folder in Knowledge.

Read sales and strategy/onboarding evidence separately: Fathom, supplied transcripts, proposal and email threads including later client replies. Use the connected call/link resolver and relevant transcript passages, not just an automated recap. If a source is inaccessible, state the gap and use available supplied evidence without claiming playback. Review user-referenced Codex chats with `read_thread` before relying on them, including later edits and send decisions. A later explicit decision supersedes an earlier draft.

If the strategy interview already happened, capture its answers and remaining gaps. Do not repeat discovery or create retrospective meeting-preparation tasks. Ask only genuinely missing questions, one at a time: commitments; communication preferences; risks; previous work and why it failed. Do not ask Michael to repeat an answer available in the sources.

### Existing systems check

Inspect the current public website and booking journey within access authority. Identify installed Google tags/GTM containers, booking provider, and the internal practice system separately. Record snippet IDs and observations without treating them as verified account ownership, GA4 data collection or working conversion tracking. Check available account inventories/access; no matching accessible account means an access gap, not proof no account exists.

Check the existing setup before proposing new Analytics/GTM accounts. Have Jaimee or the applicable specialist reconcile overlapping tags, destinations and booking events; preserve current accounts where possible. Distinguish booking clicks, enquiries, completed bookings and attendance. Platform support must be inspected/tested before promising completed-booking attribution.

A separate booking front end is not automatically a practice-system migration. Capture practitioner/time selection, slot management, notes and notifications only when evidenced. Keep a discussed future build as FYI until its owner, brief and action authority are confirmed; do not create a speculative build task or change the live booking route.

### Commercial record and finance route

Record agreed scope, fee and payment terms in the appropriate canonical commercial handover, preserving contradictions and later written evidence. Keep client-reported signing, planned payment and verified receipt distinct. Validate standard recurring pricing against `references/team-roster.md` only when applicable; never substitute recurring tiers for an explicit project offer.

For Marlon-sold clients: `Finance owner: Marlon`; `LHM billing: N/A — partner-managed`. Do not introduce Josephine as billing owner, create an LHM invoice/payment task, request payment or make receipt an LHM onboarding gate. Unknown receipt stays unknown. For a direct LHM sale, resolve the applicable billing owner and checks from evidence; do not assume this partner exception applies.

## 2. Prepare the internal handover first

Use the relevant parts of `references/templates/handover-doc.md` for the canonical record, but apply these reviewed communication rules instead of obsolete billing-first/template defaults. Record service outcomes, client contacts, decisions, promises, risks, access references, owners and next steps. Dates require evidence or explicit authority; otherwise leave unset.

Default website handover recipients: verified salesperson/partner, Kristalyn and Jaimee, with Michael copied. Adjust to actual service owners and confirmed scope; do not add Josephine or the whole team automatically. Write in Michael's voice, with short practical sections:

- Website URL near the top, practice location and main contact/email. State the practice's actual time zone and relation to Michael's only after checking it; Sydney/Melbourne is an example, not a global default.
- Selected services in plain language. State the actual GMB/posting scope and duration only if purchased; never copy another client's two-posts/six-month package as universal.
- Omit pricing, payment schedules and payment-confirmation requests from the operational email unless Michael explicitly asks for a commercial discussion. Canonical commercial records retain the facts; omission is not proof of receipt.
- Bold **Kristalyn**: onboarding/access/assets, GBP access, domain manager/current hosting, client-owned Cloudflare where applicable, and later approved nameserver/DNS coordination preserving website and email. Gather logos, practitioner/clinic photos and usage permission.
- Bold **Jaimee**: existing Analytics/GTM access and setup before creating new accounts; duplicate/overlapping tag checks; supported booking-platform tracking and limitations. Say what was observed versus what remains unverified.
- Michael's strategy, sitemap and initial homepage/design role when confirmed; client feedback before expansion and further service interviews as needed. Preserve the confirmed build handoff owner instead of assigning one from habit.
- A short FYI for separately discussed booking work, without converting it into a build assignment. Include useful meeting/handover links.

Show and open the complete editable email. Save an unsent Gmail draft where supported, preserve its ID/latest version, and clearly report unsent versus provider-verified sent.

## 3. Prepare the client introduction second

Use the latest reviewed internal handover and actual client facts. Default to the verified client contact, copying the coordinator, technical specialist and salesperson when relevant. Do not guess another practitioner's email.

- Warm opening tied to the actual meeting; verify the date rather than guessing Thursday/Friday.
- Introduce Kristalyn and Jaimee in plain language and explain who handles coordination/access/assets versus measurement.
- Explain Cloudflare as “website hosting”, under client ownership where applicable. Preserve existing website/email during preparation; no premature hosting cancellation.
- Ask whether they can access Analytics/GTM or whether their existing provider manages them. Use existing accounts where possible. Do not ask whether an account exists when access ownership is the actual gap.
- Explain measurement as understanding discovery, enquiries and bookings; avoid unsupported integration claims and raw container IDs.
- Explain the agreed initial homepage/design and wording review, then further pages and deeper interviews. Michael stays involved in strategy/sitemap/design; describe Marlon's actual continuing role without inventing video or delivery scope.
- Keep immediate asks small, such as domain manager and current host. Kristalyn coordinates the detailed access/assets follow-up.
- Omit prices, billing requests and unnecessary Astro/AI/backend detail unless specifically relevant/requested.

Open the draft in the editor and preserve later edits. Only mark the introduction sent after provider confirmation of SENT and recipients, or explicitly label a user-reported send. Do not mark access, configuration or onboarding complete because the email was sent.

## 4. Prepare the onboarding process and lean task batch

Instantiate or update `project-management/Onboarding.md` from `references/checklists/client-onboarding.md` after the communications review, preserving earlier evidence and version-stable checklists. Read `client-onboarding` for applicable gates and [reviewed-flow acceptance cases](references/reviewed-flow-cases.md) before handback.

Keep detailed, conditional gates in Obsidian: contact/strategy evidence; verified access/assets; measurement/configuration; approved production and purchased-service kickoff; completion/handoff. Marlon billing is N/A, not falsely completed. Completed interviews and sends are evidence in the checklist, not new retrospective tasks.

For a website-led handover with the roles confirmed above, propose this lean five-record pattern instead of automatically making seven gate subtasks:

| Record | Default evidenced owner | Destination |
| --- | --- | --- |
| `[Client] — Client Onboarding` | Kristalyn | `*Client Onboarding` (`68921`), current applicable phase |
| `<CLIENT>: Onboarding - Coordinate access and assets` | Kristalyn | Verified Kristalyn Inbox |
| `<CLIENT>: Website - Check Analytics, GTM and booking tracking` | Jaimee/applicable specialist | Verified specialist Inbox |
| `<CLIENT>: Website - Website rebuild` | Immediate website-stage owner | Enduring `*Web Projects` (`68635`) card |
| `<CLIENT>: Website - Prepare sitemap and homepage design` | Confirmed strategist, normally Michael | Verified owner's personal Inbox |

Use established client labels and actual board/assignee IDs through the task manager. This is a scope-aware proposal, not a universal five-task requirement: omit unsupported branches, preserve needed direct-LHM finance work and reuse existing records. Start a Marlon onboarding card at `2 — Client Contact & Strategy` with Kristalyn unless later progress is verified; direct LHM billing may remain Phase 1. Website overview starts at the evidenced stage, not “in progress” merely because a task was created.

Keep the shared website overview distinct from the personal execution task and cross-link related records in Discussion. Do not create a subtask per page/checklist item, redundant discovery or generic kickoff cards when actual delivery tasks/checklist already carry that outcome. No separate custom-booking build without a confirmed brief/owner. Do not recreate a gate card Michael removed.

Prepare exact titles, owners, boards/sections, status, due date or unset, metadata/working URLs, plain-English Discussion, completion checks, next handoff and stable deduplication keys through `basicops-task-manager`. Put action briefs in Discussion, not Description. Show the complete batch for review before any creation, assignment or move. Due dates stay unset until authorised; calculate relative weekdays in the participant's actual time zone and name the dates. Board movement and reassignment are separate: resolve spoken “AI/Aiya/my board” ambiguity before moving, while applying independent authorised dates. Preserve the same task ID.

After approval, repeat deduplication across onboarding, older client-flow, website and personal-board routes. Create/update only approved records; verify owners, destinations, statuses, dates, metadata, Discussion and links. No requested task is considered posted from a prepared payload or a model claim alone. If writes fail, report partial success and leave exact reconciliation pending; never recreate successful rows.

## 5. Save and hand off

Update/read back overview/profile, Goals where changed, Current Projects, handover and Onboarding with evidenced outcomes, live IDs/links, pending review and exact next owner/action. Keep commercial data out of operational emails, private capacity out of shared records and secrets out of all artefacts. Report unchanged/missing records without inventing facts.

Hand `lhm-project-hub:client-onboarding` the approved lean task map, scope applicability, current phase, verified sends, unresolved account/work-folder gaps and exact resume point. The five/seven reference gates stay in the detailed checklist; resuming must not regenerate a duplicate task tree or undo explicit omissions. “Handover complete” requires the authorised handover outputs actually sent/posted/verified; otherwise report prepared, sent, task-review-ready or partially complete accurately.
