# Task Classification and Handoffs

Read this file when creating or classifying a task, changing urgency, or preparing a completion,
review, blocked or waiting transition.

## Metadata

Use this exact first description line:

`LHM metadata: work_type=<type>; service=<service>; source=<source>; urgent=<true|false>; handoff_trigger=<trigger>; next_handoff=<person-or-role>; handoff_channel=<channel>; last_touchpoint=<YYYY-MM-DD|unknown|none>; touchpoint_cadence=<cadence>; next_touchpoint=<YYYY-MM-DD|unknown|none>`

Allowed values:

- `work_type`: `recurring-client-delivery`, `project-task`, `support-request`, `internal-business`
- `service`: `website`, `seo`, `google-ads`, `gmb`, `client-comms`, `admin`, `lhm-growth`, `none`
- `source`: `meeting`, `email`, `client-request`, `recurring`, `internal`, `team-request`, `unknown`
- `handoff_trigger`: `complete`, `ready-for-review`, `blocked`, `waiting`, `none`
- `handoff_channel`: `basicops`, `whatsapp`, `client-email`, `none`
- `touchpoint_cadence`: `weekly`, `fortnightly`, `monthly`, `quarterly`, `one-off`, `custom`, `none`

Use a canonical person name or confirmed role for `next_handoff`. Use `unknown` or `none` when the
source does not establish a value; do not invent one. Preserve approved working URLs beneath the
metadata line.

Existing lines without the touchpoint extension remain valid legacy metadata. Backfill active
client-communication tasks progressively. For work that is not a client touchpoint, use
`last_touchpoint=none; touchpoint_cadence=none; next_touchpoint=none`.

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
