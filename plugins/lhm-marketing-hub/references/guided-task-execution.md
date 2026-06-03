# Guided Task Execution Protocol

A shared closeout loop for Google Ads work. Once a review (the monthly review or the 90-day adversarial review) has produced its prioritised recommendations and saved its report, hand off to this protocol. It turns recommendations into a simple, one-at-a-time work-through, then closes the session with learnings and an optional scheduled follow-up.

Keep the tone plain and direct throughout. The point of this loop is to make the work feel small and manageable, one step at a time.

## When this runs

Run this after, not instead of, the review's own analysis and approval gate. The review decides *what* matters; this protocol drives *getting it done*. It applies whether the review was run standalone (skill) or as the full agent.

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

## Step 2: Offer to work through them

Ask one question, plainly:

> "Do you want me to work through each task one at a time?"

- **If no:** leave the list as it stands and go straight to Step 4 (closeout). Do not push.
- **If yes:** start the loop in Step 3.

## Step 3: Work through one task at a time

Walk the list in priority order. For each task:

1. **Present only that task.** Keep it simple and straightforward: what to do, where to do it, and the exact change or values. A few short lines, not a wall of text. Show progress like "Task 3 of 7".
2. **If the task maps to an execution skill, run it scoped to just this task**, carrying forward the client profile, the AdPulse zone, and the relevant campaign data:
   - Budget or bid strategy change → `bid-budget-optimizer`
   - Keyword waste, negatives, match types, search terms → `keyword-optimizer`
   - Creative refresh or new RSAs → `ad-copy-generator`
   - Landing page or conversion issue → `landing-page-optimizer`
   - PMax-specific issue → `pmax-optimizer`
   Run only the slice that this task needs. Do not run the whole skill end to end if a single change is all that is required.
3. **Ask if it is done.** After presenting (or executing) the task:

   > "Is that one done?"

   - The user may confirm, or may have follow-up questions. Answer the follow-ups, then ask again.
   - Move to the next task only once the user confirms done, or explicitly chooses to skip it.
4. **Track what happened** for each task: done, skipped (with reason), or deferred. You will need this for the closeout.

Stop the loop early if the user asks to. Whatever is left becomes "deferred" in the closeout.

## Step 4: Session closeout

When every task is handled, or the user decides to stop, close the session in this order.

### 4a. Write what you learned

Capture anything reusable from this session into the skill's `LEARNED.md` (per the plugin's Self-Learning Protocol — reusable rules only, not session-specific data). If new client facts surfaced (a changed budget, a new target CPA/ROAS, a recurring constraint), offer to save those to `client_profile.md`.

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

- This loop never replaces the review's approval gate. The user still approves *which* actions matter before any of this starts.
- Keep each task self-contained. The whole value is that the user only ever looks at one small thing at a time.
- Never fabricate completion. A task is only done when the user says so.
