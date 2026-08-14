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
- `workflow_state`: `prepared`, `waiting-on-michael-via-hermes`, `approved`, `executing`, `waiting-on-agent`, `ready-for-review`, `blocked`, `complete`, `none`
- `approval_status`: `not-required`, `pending-michael`, `partially-approved`, `approved`, `changes-requested`, `none`

Use a canonical person name or confirmed role for `next_handoff`. Use `unknown` or `none` when the
source does not establish a value; do not invent one. Preserve approved working URLs beneath the
metadata line.

Existing lines without the orchestration extension remain valid legacy metadata. Backfill it only
when an approved workflow transition requires it; do not churn unrelated tasks. For work that is not a client touchpoint, use
`last_touchpoint=none; touchpoint_cadence=none; next_touchpoint=none`.

## Hermes-prepared review contract

Use this contract when an overnight or on-demand marketing review has been prepared for Michael and
Hermes will manage the next conversation and specialist dispatches.

- Create or reuse **one review parent task**. Google Ads monthly reviews use Michael's governed
  approval queue: `Michael Tasks` (`49020`) / `Google Ads Flow` (`106309`), assigned to Michael
  (`36398`). Other services use the client's established `*Client Flow` mother task unless their
  own governed approval queue is recorded. Use a stable key shaped like
  `basicops:<client-slug>:<service>:monthly-review:<yyyy-mm>` and search the destination, client
  mother task and materially equivalent open titles before creating.
- The initial metadata state is
  `handoff_trigger=waiting; next_handoff=Michael via Hermes; handoff_channel=basicops; orchestration_owner=hermes; workflow_state=waiting-on-michael-via-hermes; approval_status=pending-michael`.
- Assign the review parent to Michael unless an authorised canonical workflow names another human
  approver. Hermes is the orchestration owner, not a fabricated BasicOps person or assignee.
- Description contains only the exact metadata line and verified working URLs, normally the Google
  Workspace report and client dashboard. Put the human overview, evidence confidence, top five
  proposed actions, recommendation order and approval request in Discussion.
- Proposed actions are **not authorised execution work**. Do not create executable subtasks, mutate
  ad accounts, publish, deploy or dispatch specialist execution from the prepared state. If a
  visible proposal register is operationally necessary, keep it in the parent Discussion with
  stable action labels (`A1`–`A5`), explicitly marked `Proposed — not approved`.
- A message such as “let's tackle Align Health” resumes the review but does not approve all actions.
  Hermes must read the parent, summarise what is waiting, and obtain explicit action-level direction.

After Michael responds through Hermes:

1. Record the approved, deferred and rejected action labels in a new parent Discussion message.
2. Set `approval_status=partially-approved` when only some actions are approved, otherwise
   `approval_status=approved`; set `workflow_state=approved` until the first approved action starts.
3. Create only approved execution subtasks, each with its own outcome, dependencies, completion
   condition, specialist route and next handoff in Discussion. Link verified native task URLs back to
   the parent. Do not create subtasks for deferred or rejected actions.
4. Ask whether Michael wants the created subtasks moved to individual assignee boards. Never move
   them automatically. Agent execution does not require pretending an agent has a BasicOps board.
5. Dispatch **one approved action at a time**. While active, set the parent to
   `workflow_state=executing`; the active subtask may use `workflow_state=waiting-on-agent` and name
   the specialist route in Discussion.
6. After the agent returns, verify the promised artefact or account result, add a concise evidence
   message to the subtask and parent, and only then complete the subtask. If the result needs human
   review, use `ready-for-review` instead of complete.
7. Release the next approved action only after the prior action is verified or Michael explicitly
   changes the order. On a blocker, use `workflow_state=blocked`, name the missing input and return
   the handoff to `Michael via Hermes` when his decision is required.
8. When no approved action remains, set the parent to `workflow_state=ready-for-review` if Michael
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

## Examples

- Aiya completes Jaimee's website fix: `support-request`; `website`; `team-request`;
  `ready-for-review`; `Jaimee`; `basicops`.
- Aiya completes a project design stage: `project-task`; `website`; source as verified;
  `ready-for-review`; `Kristalyn`; `basicops`.
- Jaimee completes scheduled SEO delivery: `recurring-client-delivery`; `seo`; `recurring`;
  `complete`; confirmed account owner; `basicops`.
