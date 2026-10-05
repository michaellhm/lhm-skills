---
name: email-drafts
description: Draft an email or reply in Michael's voice from the evidence-based voice profile. Use when the user says 'draft a reply to', 'write an email to', 'reply to this', 'draft this in my voice', 'email the client about', or when another skill needs a Michael-voice draft. Creates a Gmail draft, never sends.
---

# Email drafts

Write it the way Michael writes it, then save it as a Gmail draft on the right thread.

Read `${CLAUDE_PLUGIN_ROOT}/references/voice-profile.md` before writing. Read `routing.md` to pick the register (warm list vs default) and whether Kristalyn is CC'd. Read the "Learned adjustments" section at the bottom of the voice profile last; it overrides anything above it.

## Inputs

Any of: a thread (link or ID), a recipient plus what to say, or a task completed that the client needs to hear about. If the input is a thread, read the whole thread first, including Michael's earlier messages in it; match his register from those before anything else.

## Method

1. Decide the audience: client-formal, client-warm, team, partner, prospect. This sets opener, length band, and close (voice-profile.md, "Register by audience").
2. Decide the shape: quick reply (1 to 4 lines), status (three beats), ask (list with reasons plus a soft yes/no), pushback (constraint then workaround), miss (one-line own, fix, timing), brief (CAPS headings, numbered Please), prospect (price plain, call offered, phone in body).
3. Write the first line as a thank-you or context anchor tied to the thread. Never a generic pleasantry. For a simple client acknowledgement, start directly with the action and timing when sufficient; do not automatically add a thank-you or apology.
4. Write the body in the length band. Bullets past two items. Bold lead-in labels for confirmations. Reasons attached to asks. Use short bullets for client results and tracking updates; omit unnecessary administrative narration and explanatory clauses. Use commas and full stops instead of em dashes, especially for partners, while preserving informal hyphens Michael adds himself.
When reporting enquiries or leads, ask how many became actual appointments or jobs, unless that outcome is already known. Use the client’s business terminology.
5. Close per audience. "Thanks,\nMichael" for asks, "Cheers,\nMichael" for updates.
6. Run the Never list. If any phrase on it is present, rewrite that sentence.
7. If a fact is needed that is not in the thread or the client's Obsidian profile (a price, a date, a decision), leave `[confirm: ...]` in the draft. Do not invent.
8. Save as a Gmail draft on the thread (or a new draft with the subject given). Return the draft link and the full text.

## Review and evidence handoff

Always show Michael the full draft before any email is sent. A general request to reply, hand something over or send it to someone starts draft preparation; it does not skip review. A sending coordinator may send only after Michael explicitly approves the latest reviewed text. This skill remains draft-only. After edits, show the revised draft; approval of an earlier version does not approve a later change.

Record every reviewable draft, including chat-only drafts, in the existing `inbox-log/drafts.jsonl` or verified private-vault `Inbox Briefs/log/drafts.jsonl`. Reuse the established log destination; never write personal email text into the source repository or installed plugin cache. Include date, recipient, audience_register, thread_id when known, draft_id when a provider draft exists, writing_block_id or conversation reference for chat drafts, draft_text and word_count. Use null for unavailable IDs; never invent a Gmail draft ID. Append revisions with the same artifact reference so email-learn can recover the original and latest text without counting one artifact twice.

Hand the artifact reference and latest text to the sending coordinator. After an authorised send, that coordinator records final_text, sent_message_id and outcome `sent` only after provider readback confirms delivery. Until then record `draft-ready` or `approved`, not sent. An uncertain send must be reconciled before retrying.

## Client-update emails

When the input is "we did X for client Y", use `lhm-project-hub:client-update-email` for the substance (plain-language explanation of the work) and this skill for the voice. Do not restate the technical detail; Michael's clients get the outcome and what it means for them.

## Do not

- Do not sign as anyone but Michael.
- Do not send.
- Do not add a signature block; Gmail appends it.
- Do not exceed the length band to seem thorough. Michael's long emails have headers; his thorough emails are still short.
