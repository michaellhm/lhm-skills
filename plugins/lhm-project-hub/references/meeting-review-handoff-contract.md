# Meeting review and approved handoff contract

Use this contract for authenticated desktop review of a meeting wrap and for every downstream
Project Hub, BasicOps or Hermes handoff created from that review.

## Evidence and approval envelope

1. Start from the exact Gmail message the reviewer selected under `*** MEETING WRAP`. Record its
   stable message/thread reference in the private operational record, then resolve the matching
   saved wrap, meeting-notes file and linked BasicOps task IDs. Read the original transcript only
   when the saved evidence conflicts or accuracy is disputed. Never commit mailbox IDs, client
   content or transcript text to this repository.
2. Treat the label, unread/read state, opening the message and discussion as intake evidence only.
   None is approval. Before a BasicOps mutation or Hermes dispatch, record the authenticated
   reviewer's exact approval envelope: selected wrap, approved task IDs, approved scope, routing,
   reviewer, timestamp in the reviewer's IANA timezone and a stable idempotency key.
3. Approval binds only those task IDs and that scope. A material scope change, replacement task or
   additional live/client-facing action needs fresh approval. Approval that already names routing
   authorises that move and ordinary internal production; do not ask for the same move again.
   Bare discussion, advice or label changes do not.
4. Before creating work, inspect the linked task and canonical implementation evidence. Existing
   callback or other implemented work becomes verification/correction scope, not a duplicate build.
   Separate recorded decisions from suggestions and client-owned inputs. Suggestions remain
   unapproved until explicitly selected.

## Action register and client-owned inputs

- Keep historical wrap, notes and transcript evidence immutable. Record corrections as dated
  addenda with provenance.
- Consolidate related inputs owed by the same client contact into one human-owned follow-up. Its
  Discussion contains a traceable checklist or linked subtasks for every absorbed ask and one
  copy-ready email preserving the established client email style. The email remains unsent unless
  separately authorised through a verified outbound route.
- Do not dispatch a task whose required client input, access or decision is missing. Keep that item
  with its verified human follow-up owner and state the exact unblock condition. An unaffected,
  input-ready approved task may proceed independently.

## Dates

For review-ready production, default the target to 14 calendar days before the confirmed next
meeting, calculated in the requester's IANA timezone. Use calendar arithmetic, not a fixed number
of UTC hours; month boundaries and `Australia/Melbourne` DST must remain correct. For a confirmed
meeting on `2026-10-14`, the default target is `2026-09-30`.

Preserve an explicit authorised date override. A dependency, client-input checkpoint or internal
handoff may be earlier only when Discussion states the evidence and basis. Flag a target that is in
the past or cannot be met; never silently assign it. This review-ready target is not evidence of a
client-contact cadence and must not update touchpoint metadata.

## Lily routing and execution

Lily is the project-manager actor and verified BasicOps user `82484`. Before routing each approved
item, Lily resolves the named human reviewer from current canonical people records, then resolves
that person's exact BasicOps board and Inbox. A missing or ambiguous reviewer, board or Inbox blocks
only that item. Never guess from a display name, move unaffected items, or broaden approval.

For each input-ready approved item:

1. Re-read the task, approval envelope and current revision. Search the task Discussion and durable
   run records for the idempotency key. If the same approved scope was already routed or dispatched,
   verify and return that result without duplicating it.
2. Move the task to the verified reviewer's Inbox when the approval includes routing, and read back
   task ID, revision, assignee, project, section and Discussion.
3. Dispatch ordinary internal production through the existing chain:
   `Chief of Staff -> Context & Research -> Head of Production -> specialist -> producer QA -> Drive
   artefact delivery -> independent final QA`. Lily verifies that the approved scope, dependencies,
   durable outputs, receipts and handoff are complete; Lily does not substitute for specialist
   clinical or technical judgment.
4. Use `lhm-project-hub:ted-task-ownership` when Ted coordinates the active action. Ted (`82491`)
   claims the exact actionable task before substantive work, then returns it to the verified named
   human reviewer when production and evidence are ready.
5. Verify required outputs in their authoritative destination, including Drive readback where
   applicable. Use BasicOps' native review request, leave the human-owned task open in `Under Review`
   and verify reviewer, status, assignee, board/Inbox, durable links and Discussion. Never
   automatically mark it `Complete`.

A short coaching prompt may help the human inspect or finish the output. It is optional and must not
block ordinary approved production.

## Identity and permission boundary

Prefer the existing authenticated Lily connector and verify the actual sender/actor by readback. If
it is unavailable, use the authenticated account that is actually available and label the message
as AI-written by that actor. Never spoof Lily, Ted or a human, change credentials, broaden OAuth,
send client email, publish a site, launch ads or mutate another live system under this contract.

