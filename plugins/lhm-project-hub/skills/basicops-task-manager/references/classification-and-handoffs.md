# Task Classification and Handoffs

Read this file when creating or classifying a task, changing urgency, or preparing a completion,
review, blocked or waiting transition.

## Metadata

Use this exact first description line:

`LHM metadata: work_type=<type>; service=<service>; source=<source>; urgent=<true|false>; handoff_trigger=<trigger>; next_handoff=<person-or-role>; handoff_channel=<channel>; last_touchpoint=<YYYY-MM-DD|unknown|none>; touchpoint_cadence=<cadence>; next_touchpoint=<YYYY-MM-DD|unknown|none>; orchestration_owner=<owner>; workflow_state=<state>; approval_status=<status>`

Allowed values:

- `work_type`: `recurring-client-delivery`, `project-task`, `support-request`, `internal-business`
- `service`: `website`, `seo`, `google-ads`, `gmb`, `client-comms`, `admin`, `lhm-growth`, `none`
- `source`: `meeting`, `email`, `client-request`, `recurring`, `internal`, `team-request`, `unknown`
- `handoff_trigger`: `complete`, `ready-for-review`, `blocked`, `waiting`, `none`
- `handoff_channel`: `basicops`, `whatsapp`, `client-email`, `none`
- `touchpoint_cadence`: `weekly`, `fortnightly`, `monthly`, `quarterly`, `one-off`, `custom`, `none`
- `orchestration_owner`: `hermes`, a canonical person name, a confirmed role, or `none`
- `workflow_state`: `prepared`, `waiting-on-human-via-hermes`, `waiting-on-michael-via-hermes` (legacy), `approved`, `executing`, `waiting-on-agent`, `ready-for-review`, `blocked`, `complete`, `none`
- `approval_status`: `not-required`, `pending-human`, `pending-michael` (legacy), `partially-approved`, `approved`, `changes-requested`, `none`

Use a canonical person name or confirmed role for `next_handoff`. Use `unknown` or `none` when the
source does not establish a value; do not invent one. Preserve approved working URLs beneath the
metadata line.

Existing lines without the orchestration extension remain valid legacy metadata. Backfill it only
when an approved workflow transition requires it; do not churn unrelated tasks. For work that is not a client touchpoint, use
`last_touchpoint=none; touchpoint_cadence=none; next_touchpoint=none`.

## Hermes-prepared review contract

Use this contract when an overnight or on-demand marketing review has been prepared for an
accountable human reviewer and Hermes will manage the next conversation and specialist dispatches.

- Create or reuse **one review parent task**. Google Ads monthly reviews use Michael's governed
  approval queue: `Michael Tasks` (`49020`) / `Google Ads Flow` (`106309`), assigned to Michael
  (`36398`). Other services use the client's established `*Client Flow` mother task unless their
  own governed approval queue is recorded. Use a stable key shaped like
  `basicops:<client-slug>:<service>:monthly-review:<yyyy-mm>` and search the destination, client
  mother task and materially equivalent open titles before creating.
- The initial metadata state is
  `handoff_trigger=waiting; next_handoff=<verified-reviewer> via Hermes; handoff_channel=basicops; orchestration_owner=hermes; workflow_state=waiting-on-human-via-hermes; approval_status=pending-human`.
- Assign the review parent to the authorised canonical human reviewer. The fixed Michael Google Ads
  queue above is one governed workflow instance, not the engine default. Hermes is the orchestration
  owner, not a fabricated BasicOps person or assignee.
- Description contains only the exact metadata line and verified working URLs, normally the Google
  Workspace report and client dashboard. Put the human overview, evidence confidence, top five
  proposed actions, recommendation order and approval request in Discussion.
- Proposed actions are **not authorised execution work**. Do not create executable subtasks, mutate
  ad accounts, publish, deploy or dispatch specialist execution from the prepared state. If a
  visible proposal register is operationally necessary, keep it in the parent Discussion with
  stable action labels (`A1`–`A5`), explicitly marked `Proposed — not approved`.
- A message such as “let's tackle Align Health” resumes the review but does not approve all actions.
  Hermes must read the parent, summarise what is waiting, and obtain explicit action-level direction.

After the authenticated reviewer responds through Hermes:

1. Record the approved, deferred and rejected action labels in a new parent Discussion message.
2. Set `approval_status=partially-approved` when only some actions are approved, otherwise
   `approval_status=approved`; set `workflow_state=approved` until the first approved action starts.
3. Create only approved execution subtasks, each with its own outcome, dependencies, completion
   condition, specialist route and next handoff in Discussion. Link verified native task URLs back to
   the parent. Do not create subtasks for deferred or rejected actions.
4. Ask whether the authenticated reviewer wants the created subtasks moved to individual assignee boards. Never move
   them automatically. Agent execution does not require pretending an agent has a BasicOps board.
5. Dispatch **one approved action at a time**. While active, set the parent to
   `workflow_state=executing`; the active subtask may use `workflow_state=waiting-on-agent` and name
   the specialist route in Discussion.
6. After the agent returns, verify the promised artefact or account result, add a concise evidence
   message to the subtask and parent, and only then complete the subtask. If the result needs human
   review, use `ready-for-review` instead of complete.
7. Release the next approved action only after the prior action is verified or the reviewer explicitly
   changes the order. On a blocker, use `workflow_state=blocked`, name the missing input and return
   the handoff to `<verified-reviewer> via Hermes` when that person's decision is required.
8. When no approved action remains, set the parent to `workflow_state=ready-for-review` if the reviewer
   must inspect outcomes, or `complete` only after the review and all approved outcomes are verified.

Every transition requires an exact metadata update, a separate human Discussion message, read-back
verification, and a returned BasicOps URL. A status change alone never proves dispatch, delivery,
notification or approval.

## Client touchpoint contract

- Set `last_touchpoint` only from verified sent-email, completed-meeting or canonical contact
  evidence. A draft or BasicOps planning comment does not prove contact.
- Record the confirmed rhythm in `touchpoint_cadence`. Use `one-off` plus an exact date for a
  particular follow-up. Use `custom` only when Discussion states the rule.
- Store an exact `next_touchpoint` date whenever another contact is expected, including when the
  date can be calculated from a cadence. This prevents guesswork after missed weeks or across
  unequal month lengths.
- Flag a conflict between `next_touchpoint`, task due date and canonical client commitments; do not
  silently choose one.
- After verified contact, prepare the metadata update and the next exact date, then move a
  reply-dependent task to the person's verified waiting section only after approval.

## Classification

- Scheduled client commitments are `recurring-client-delivery`.
- Finite work contributing to a defined project outcome or stage is `project-task`.
- Reactive client/team work outside planned delivery is `support-request`.
- LHM growth, systems, finance, training and operations are `internal-business`.
- Meeting origin belongs in `source=meeting`; it does not replace the work type.
- `urgent=true` requires an authorised confirmation plus a real deadline or consequence in
  Discussion. A due date alone is insufficient.
- Client follow-up is an action/state, not a separate work type. Keep the underlying work type;
  normally use `service=client-comms`. Use `recurring-client-delivery` only for a genuinely
  scheduled client-contact commitment.

When classifying an existing task, return the proposed line, confidence and short reason. Seek
approval before writing. A low-confidence classification must ask one material question.

## Handoff contract

Resolve four things: trigger, next person, next action and notification channel. Put the human
instruction in Discussion, for example:

> **Next handoff:** When this is ready for review, tell Jaimee in BasicOps and include the completed
> URL so she can verify the fix and continue the SEO work. If blocked, tell Jaimee what is missing
> and the proposed timing.

For a completion, ready-for-review, blocked or waiting request:

1. Verify the current task and handoff contract.
2. Ask what completion releases when the downstream action is missing.
3. Prepare the exact status/list mutation and the exact handoff comment separately.
4. Apply only the operations explicitly approved.
5. Read back the task mutation and notification. Do not claim the handoff occurred merely because
   the task status changed.
6. Offer a WhatsApp or client-email draft only when that channel is confirmed; never send without a
   separate authorised route and approval.

The flow is: `do → verify → notify → release next action → update client when required`.

## Delegated Hermes task baton

Reuse one BasicOps parent as the visible next-action baton for a human-delegated Hermes outcome.
Do not create a new task at approval, execution, review or correction boundaries. Resolve AI owners
only from `${CLAUDE_PLUGIN_ROOT}/references/basicops-ai-user-registry.json`.

| Transition | Assignee | Native status | Discussion marker |
| --- | --- | --- | --- |
| plan ready | authenticated human approver | `Under Review` | `Review type: Plan approval` plus version/hash |
| current plan approved | verified Chief of Staff AI user | `In Progress` | approval receipt plus unchanged version/hash |
| delivery ready | authenticated human reviewer | `Under Review` | `Review type: Delivery review` plus receipts |
| correction requested | verified Chief of Staff AI user | `In Progress` | correction event and resumption point |
| capability failure after one safe retry | verified CTO route | `Blocked` | incident evidence and saved return point |
| accepted and reconciled | final accountable owner | `Complete` | Chief of Staff completion receipt |

Every transition states the current outcome, verified evidence, next owner, next action, trigger,
completion condition, permission ceiling and BasicOps URL. Delivery review also contains `Calls
made` for reversible assumptions and choices, and `Decision required` only for consequential,
irreversible, external-commitment or permission-bound decisions.

Approval binds task ID, revision, plan version and content hash. Reject stale or mismatched
approval. Replays are idempotent and may confirm an existing projection but cannot create another
task, comment or handoff. A transition is not committed until readback confirms the expected
assignee, native status and Discussion record.

On correction, resume the same parent and approved execution. Fix current work first; then send a
durable correction event to the Learning Steward for wider disposition. Ordinary reversible
uncertainty is not a blocker: choose the best-supported option, record it under `Calls made`, and
continue.

## BasicOps attention and decision contract

A BasicOps task remains the governed record regardless of the interface that activated it. When a
material human decision prevents safe continuation:

1. Resolve the respondent from the named decision owner, verified next handoff, current assignee,
   authenticated requester, then verified project or account owner. Do not hard-code Michael.
2. Post one decision-ready question in Discussion with the blocker, reason, recommendation or two
   to three bounded options, consequence and resumption point.
3. Apply the accurate blocked, waiting or review transition through the normal mutation gate.
4. Send the respondent a BasicOps direct message containing the concise question and native task
   link, and verify the Discussion post and message separately.
5. Record the authenticated answer and its local timestamp in Discussion, then release the prior
   workflow to resume without another start approval.

For an outbound DM with no incoming message context, resolve the respondent's verified BasicOps
user ID, list direct chats and reuse the chat whose `user` matches. Create a chat for that user only
when none exists, then call `create_message_in_chat` and verify it by chat read-back. Reserve
`create_reply_in_message` for responding to an existing `messageId`.

Do not send a duplicate direct message when the respondent is already answering the same question
in an active authenticated interface. Do not claim a direct message was sent merely because the
Discussion changed, the task was assigned or BasicOps shows the task as seen. If ownership is
ambiguous, ask to confirm ownership instead of guessing.

If the BasicOps connector cannot send or verify direct messages, keep the Discussion question,
return the unsent notification as a capability gap and route it to the governed capability-incident
workflow. Do not silently substitute Telegram or another channel.

An authenticated instruction to complete a defined outcome authorises its normal reversible
internal steps, including research, briefs, drafts, separate working files, progress notes and
delivery into the verified client working folder. Do not turn a workflow preference with an
established default into an approval gate. Final copy or strategy approval, client contact,
publishing, deployment, launch, spend and meaningful scope or commercial changes retain their
separate approval boundaries.

Use the authenticated person's configured IANA timezone for human-facing dates. Michael uses
`Australia/Melbourne`; do not use server UTC or a permanently fixed offset.

## Examples

- Aiya completes Jaimee's website fix: `support-request`; `website`; `team-request`;
  `ready-for-review`; `Jaimee`; `basicops`.
- Aiya completes a project design stage: `project-task`; `website`; source as verified;
  `ready-for-review`; `Kristalyn`; `basicops`.
- Jaimee completes scheduled SEO delivery: `recurring-client-delivery`; `seo`; `recurring`;
  `complete`; confirmed account owner; `basicops`.
