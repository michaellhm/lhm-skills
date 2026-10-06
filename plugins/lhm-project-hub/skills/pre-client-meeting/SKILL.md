---
name: pre-client-meeting
description: "Prepare short, evidence-backed speaking bullets before an existing client's meeting. Use when asked to 'prep for the client meeting', 'pre-client meeting', 'sweep the meeting wrap, emails and boards', 'give an update then what is next', or summarise campaign wins and losses for a meeting. Reconciles client correspondence, BasicOps, Obsidian and implementation evidence; not a post-meeting wrap or full account audit."
---

# Pre-client meeting

Give Michael a brief he can read directly in the meeting: what the client sent, what LHM has done about it, what is underway, what comes next and what needs a decision. Use short, sharp bullets throughout the speaking notes. The evidence sweep supports the conversation; it is not the conversation itself.

## Resolve the client and meeting

- Use the confirmed client and meeting from the conversation; do not repeat answered questions. Resolve ambiguous acronyms against canonical client records before searching broadly.
- Read [the knowledge/work routing contract](../../references/obsidian-context-contract.md) and [folder convention](../../references/folder-convention.md). Resolve the existing shared LHM Knowledge client root and separate verified Claude Workspace / Current Clients work root. Preserve existing names/case; do not create a client root or use the private vault as client knowledge.
- Read the overview/profile, Goals.md, Current Projects.md and relevant project notes. Find the last meeting record/wrap and subsequent decisions.
- Verify the upcoming date/time and attendees from the available calendar when needed. Flag a material calendar conflict internally; do not change events or let it derail preparation once attendance is confirmed.
- Start from the last relevant meeting through today. Follow older threads only for carried decisions, unresolved delivery or source conflicts. Avoid a lifetime inbox sweep by default.

## Sweep and reconcile

Use available read-only connectors or verified local sources. A missing source does not block useful preparation from the others; identify the gap precisely.

### Meeting wraps and client email

- Read the latest meeting-wrap email and relevant client replies, including named contacts requested by the user. Search by verified identities and client context rather than first names alone.
- Read complete relevant threads, including later replies and HTML bodies where plain text is absent. A search preview or old message does not establish the latest decision.
- Extract requests, feedback, approvals, supplied assets, promised follow-ups, holds and client dependencies. Check attachments or linked documents only when their contents affect a claim.
- Preserve prior approvals. Do not ask the client to approve a sitemap or budget again because an older note still says pending.

### BasicOps across boards

- Verify current user, team roster and actual board names/IDs. Sweep Client Flow, relevant delivery/project boards and personal boards containing this client's work. Include Michael, Jaimee, Kristalyn and Aiya when relevant or requested; do not hard-code their IDs or assume every client uses the same team.
- Paginate task inventories or use an equivalent complete client-filtered search. Match aliases, linked project parents and delivery-specific titles, not only the client acronym. Inspect relevant archived/completed work when needed to establish a recent outcome.
- Read task descriptions, discussions, relevant replies and linked subtasks. Follow evidence links to the delivered work where completion matters.
- Accepted means assigned/accepted, not finished. A completed card without an artefact may still need verification; an open card may have documented implementation. Reconcile dates and delivery evidence rather than copying status labels.
- Deduplicate the same work spread across boards. Separate current work, completed work, awaiting client input, paused work and stale internal administration. Keep internal runtime/connector failures out of client-facing bullets unless they materially affect delivery; never imply work happened when it did not.

### Obsidian and Claude/Cowork work evidence

- Read affected project notes, recent meeting records and reports. Use targeted reads to avoid treating truncated notes as a complete sweep.
- Inspect relevant saved implementation logs, monthly reviews, change records and deliverables under the verified work root. These can contain completed changes missing from task cards or Obsidian.
- When the user asks about Claude/Cowork, use an available authorised conversation route if useful. If only saved Claude files are available, identify them as saved logs; do not claim to have read the chat itself.
- Resolve conflicting facts by recency, source purpose and actual evidence. Client correspondence establishes approval; implementation logs establish reported execution; direct platform or artefact inspection verifies current state. Preserve unresolved differences and source dates.

## Campaign wins and losses, when relevant

If campaign changes or performance are part of the meeting, prepare a quick balanced snapshot rather than a full audit.

- Find what changed, when, approval evidence and verification evidence. Separate completed changes from recommendations and follow-up checks.
- Read fresh platform metrics when available. Confirm the correct account, currency, timezone, conversion definitions and comparable date windows. Use existing reports if access is unavailable, with explicit dates and limits.
- Compare like-for-like periods. Keep full calendar months separate from rolling windows. State spend, meaningful outcomes and cost per outcome; calculate straightforward differences from retrieved figures.
- Split bookings, phone actions and other conversions where the distinction changes the story. Do not label blended conversions as unique leads, bookings or patients. Identify attributed/fractional values and round sensibly for speaking notes.
- Show wins and losses/watch-outs together. Improved blended CPA can coexist with falling online bookings. Account cleanup is a completed improvement in configuration, not proof of more patients.
- Do not attribute a full month's improvement to changes made at month-end. A short post-change window is an early signal; allow for conversion lag and volume before drawing conclusions.
- End with the next monitoring/check action and any decision genuinely needed. Do not change campaigns, bidding, tracking, budgets or live assets during preparation.

## Build the speaking notes

Group by the client's actual priorities, not by source system or staff board. Put the most material progress and decisions first. For each topic, use only the labels that add information:

- **You sent us:** [Feedback, request or supplied input.]
- **You approved:** [Established decision, where relevant.]
- **We've done:** [Evidenced completed work.]
- **We're working on:** [Work actually underway. Use “Next” for accepted but unstarted tasks.]
- **Next:** [Immediate agreed or proposed work; distinguish a proposal when it is not committed.]
- **We need from you:** [Specific delivery input.]
- **Today:** [Decision to resolve in the meeting.]
- **Win:** [Dated positive result.]
- **Watch-out:** [Dated decline, uncertainty or material constraint.]

Use Australian English, one idea per bullet and short sentences. Split multi-part feedback into separate bullets. No narrative scripts, tables, long nested lists or internal task IDs in the speaking section. Avoid mechanically using every label, repeating the same action under several labels or presenting an exhaustive backlog. Keep paused/low-priority work brief and include it only when a decision is useful. Do not revive cancelled tasks or turn client-owned operations into LHM commitments.

Close with the few owner/date decisions needed and the immediate work ahead. Dates are confirmed commitments only when the sources support them; otherwise say working target or proposed review date.

Below a clear **Internal evidence — not for reading aloud** divider, keep compact source links, exact reporting periods/definitions, unresolved evidence conflicts and coverage gaps. Keep private staff/founder information out of any shared/client-facing artefact. Mention incomplete pagination, unread attachments or unverified delivery only where they limit a conclusion; do not claim a complete sweep when it was partial.

## Save and hand back

- Save the meeting-preparation process record beneath the existing canonical client root at `project-management/meetings/YYYY-MM-DD-meeting-agenda.md`, or update the existing agenda for that meeting. Mark it prepared, not meeting outcomes. This process record belongs in knowledge; a separately requested presentation/export belongs under the verified work root.
- Hand back evidenced changes to existing affected project notes and Current Projects.md under the shared routing contract. Preserve historical reports; add dated current facts and supersede stale assumptions rather than erasing provenance. Do not turn preparation into a broad vault cleanup.
- Respect review-only or immutable-snapshot environments: return proposed content instead of bypassing their boundary. If a save fails or a destination is unavailable, deliver the brief in chat and state the precise unsaved gap.
- Read back changed records before claiming they were saved. Return the agenda link and a short list of material gaps, if any. The user should not need to read the internal evidence to use the speaking bullets.
- Preparation does not send email, create Gmail drafts, mutate BasicOps, move calendar events, delegate work or deploy changes. Those actions require their own requested workflow. After the meeting, use `client-meeting-email` for the transcript-backed wrap and `meeting-to-action` for authorised action reconciliation; do not treat pre-meeting proposals as meeting decisions.
