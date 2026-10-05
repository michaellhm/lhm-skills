---
name: email-session
description: Run a timed, focused email session from today's brief. Use when the user says 'I've got 30 minutes for email', 'let's do emails', 'email session', 'work through my replies', 'what should I answer first', or gives a time budget. Walks Reply-today items one at a time, shows the draft, takes edits, and hands back a send-ready draft. Never sends.
---

# Email session

Turn a time budget into a short list of replies, worked one at a time.

## Setup

1. Find today's brief: `Inbox Briefs/YYYY-MM-DD.md` in the vault, or the most recent one, or the brief pasted in this chat. If there is no brief from the last 24 hours, run inbox-triage first (it takes a few minutes) and say so.
2. Ask for the time budget only if not given. Default 30 minutes.
3. Budget rule: quick replies count as 2 minutes, status or ask replies 5, anything with a work prompt 10 plus the work itself (which does not happen in this session; the work prompt is handed over instead). Pick the set that fits, oldest-waiting first, and say what will not fit so Michael can swap.

## Loop, one item at a time

For each item:

- Show: who, what they asked, how long they have waited, and the full draft text.
- Ask for one of: send as is, edit (take the change, show the revised draft), skip, or hand to work (return the work prompt block for ChatGPT and move the item to "carried").
- On "send as is" or after edits: update the Gmail draft to the final text and confirm it is ready in Gmail. Do not send. Tell Michael the draft is in Gmail ready to go; if ChatGPT with Gmail is his sending surface, the draft text is in the chat to paste.
- Record the original and latest reviewed text using email-drafts' evidence handoff. In the established `inbox-log/session.jsonl` or private-vault `Inbox Briefs/log/session.jsonl`, include date, thread_id, draft_id (null for chat-only drafts), writing_block_id or conversation reference, draft_text, final_text, review_outcome `unchanged|edited|skipped|carried` and delivery_outcome `draft-ready|approved|sent|uncertain`. Review approval or a saved final draft is not a send. Only an authorised sending coordinator with verified provider readback may set `sent` and record sent_message_id; retain the original draft for comparison.

Keep each item to one exchange where possible. No summaries between items.

## Close

At the end of the budget or the list: three lines. Draft-ready N (verified sent N only if a sending coordinator supplied evidence), carried N (with work prompts collected for pasting), skipped N. Preparing a draft does not make its recipient the waiting owner. Set WAITING ON only after verified sending establishes a recipient dependency and filing is authorised; remove ONGOING TASKS only if no underlying task remains. Follow Michael's draft-before-send preference even when the initial request names a recipient and says to send something over.
