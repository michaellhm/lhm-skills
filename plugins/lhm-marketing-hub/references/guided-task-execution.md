# Guided Task Execution Protocol

A shared closeout loop for Google Ads work. Once a review (the monthly review or the 90-day adversarial review) has produced its prioritised recommendations and saved its report, hand off to this protocol. It turns recommendations into a simple, one-at-a-time work-through, then closes the session with learnings and an optional scheduled follow-up.

Keep the tone plain and direct throughout. The point of this loop is to make the work feel small and manageable, one step at a time.

## When this runs

Run this after, not instead of, the review's analysis and authority classification. The review decides
*what* matters; this protocol drives *getting it done*. For every governed Google Ads flow, also
follow `references/google-ads-departmental-delivery.md`. For a Hermes monthly flow, resume the monthly
structured handback rather than regenerating discovery.

## Step 1: Lay out the task list in chat

Convert the approved or recommended actions into a clean numbered list written directly in the chat. State the count up front.

- Open with the count: "Here are the N tasks." (Use the real number, e.g. "Here are the 7 tasks.")
- One line per task: a short title plus a one-line plain-English description of what it is and why it matters. Quantify where the review already did (the dollar figure, the campaign name).
- Order by priority, highest-impact or most urgent first.
- No file dumps, no methodology recap, no long reasoning. The full detail already lives in the saved report.

Example shape:
```
Here are the 7 tasks:

1. Kill the "Generic - Broad" campaign — ~$1,400/quarter, zero conversions.
2. Add 12 negative keywords from the search terms waste list.
3. Cut the "Brand" daily budget by 20% — it is capped and over-serving.
...
```

## Step 2: Classify authority and start

The Google Ads Lead marks routine reversible actions `approved` and begins the first
dependency-ready action without asking a generic permission question. Mark consequential actions
`waiting_approval` and ask Michael only for the exact decision required. If no action can progress,
hand back the bounded approval or blocker.

## Step 3: Work through one task at a time

Walk the list in priority order. For each task:

The Google Ads Lead must dispatch only one approved action at a time. Before dispatch, mark that action `running` and the parent `specialist_running`. After the worker returns, send the result to `google-ads-delivery-qa`. Record a QA-passed outcome in canonical Obsidian context and BasicOps before choosing the next action. If the worker or QA reaches a live-mutation approval gate, set `waiting_approval` and stop.

1. **Present only that task.** Keep it simple and straightforward: what to do, where to do it, and the exact change or values. A few short lines, not a wall of text. Show progress like "Task 3 of 7".
2. **If the task maps to an execution skill, run it scoped to just this task**, carrying forward the client profile, the AdPulse zone, and the relevant campaign data:
   - Budget or bid strategy change → `bid-budget-optimizer`
   - Keyword waste, negatives, match types, search terms → `keyword-optimizer`
   - Creative refresh or new RSAs → `ad-copy-generator`
   - Landing page issue → `landing-page-optimizer`
   - Conversion actions, campaign goals, GA4 firing or Ads imports → `google-ads-conversion-audit`
   - PMax-specific issue → `pmax-optimizer`
   - **"Conversion actions are firing"** → run the `google-ads-conversion-audit` slice and use its available Google Analytics connector for the booking event, per "Conversion quality before volume" in `references/lhm-philosophy/google-ads.md`. Present what GA4 shows as the task result; only fall back to asking the client if no GA4 property is on file or GA4 itself shows the event isn't firing.
   Run only the slice that this task needs. Do not run the whole skill end to end if a single change is all that is required.
3. **QA, verify and ask if it is done.** A dispatched worker must return observed evidence, mutations performed (or `none`) and verification. QA must return `pass`, `correction_required`, `waiting_approval`, `needs_evidence` or `blocked`. After a pass, present only the current result:

   For API-observable work, the Lead accepts completion from QA plus the defined live readback; do
   not ask Michael to reconfirm it. For manual Google Ads UI work, wait for Michael's execution
   confirmation and then run the defined verification before closing the action.
4. **Track what happened** for each task: done, skipped (with reason), or deferred. You will need this for the closeout.

Stop the loop early if the user asks to. Whatever is left becomes "deferred" in the closeout.

## Step 4: Session closeout

When every task is handled, or the user decides to stop, close the session in this order.

### 4a. Production acceptance and Learning Steward

Return the departmental completion dossier to Head of Production. After acceptance, send the structured Learning Steward intake. Learning Steward decides whether evidence belongs in client context, Knowledge, an SOP, a skill improvement, a capability incident or `Observe again`. Do not append directly to a generic `LEARNED.md` merely because the session ended.

Update the review's session output with what was actually done: actions executed, actions deferred and why, and any concrete before/after values.

### 4b. Always ask about a follow-up

End every session with this question, without exception:

> "Do you want me to schedule a follow-up?"

- **If no:** done. Nothing further.
- **If yes:** ask which form they want this time:
  1. **A real scheduled run** — set up an actual scheduled follow-up using the `schedule` skill (or the scheduled-tasks capability) at the right cadence: roughly 30 days out for a monthly review, roughly 90 days out for the adversarial review. Confirm the date before creating it.
  2. **Just note the date** — record the suggested next-review date in the session summary file, with no automation.

  Offer both and let the user pick per session. Do not assume a default.

## Notes

- This loop never replaces consequential approval gates. The Lead decides routine reversible
  actions; Michael decides only the consequential classes defined by the departmental contract.
- Keep each task self-contained. The whole value is that the user only ever looks at one small thing at a time.
- Never fabricate completion. A specialist action is complete only when its returned evidence verifies the expected outcome; a manual action is complete only when the user confirms it.
