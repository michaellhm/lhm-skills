# Task Classification and Handoffs

Read this file when creating or classifying a task, changing urgency, or preparing a completion,
review, blocked or waiting transition.

## Metadata

Use this exact first description line:

`LHM metadata: work_type=<type>; service=<service>; source=<source>; urgent=<true|false>; handoff_trigger=<trigger>; next_handoff=<person-or-role>; handoff_channel=<channel>`

Allowed values:

- `work_type`: `recurring-client-delivery`, `project-task`, `support-request`, `internal-business`
- `service`: `website`, `seo`, `google-ads`, `gmb`, `client-comms`, `admin`, `lhm-growth`, `none`
- `source`: `meeting`, `email`, `client-request`, `recurring`, `internal`, `team-request`, `unknown`
- `handoff_trigger`: `complete`, `ready-for-review`, `blocked`, `waiting`, `none`
- `handoff_channel`: `basicops`, `whatsapp`, `client-email`, `none`

Use a canonical person name or confirmed role for `next_handoff`. Use `unknown` or `none` when the
source does not establish a value; do not invent one. Preserve approved working URLs beneath the
metadata line.

## Classification

- Scheduled client commitments are `recurring-client-delivery`.
- Finite work contributing to a defined project outcome or stage is `project-task`.
- Reactive client/team work outside planned delivery is `support-request`.
- LHM growth, systems, finance, training and operations are `internal-business`.
- Meeting origin belongs in `source=meeting`; it does not replace the work type.
- `urgent=true` requires an authorised confirmation plus a real deadline or consequence in
  Discussion. A due date alone is insufficient.

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
