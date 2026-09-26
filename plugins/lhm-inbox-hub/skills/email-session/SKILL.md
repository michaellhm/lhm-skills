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
- Record the final text against the draft ID in `inbox-log/session.jsonl`: `{"date","thread_id","draft_id","outcome": "sent-as-is|edited|skipped|carried","final_text"}`. email-learn uses this.

Keep each item to one exchange where possible. No summaries between items.

## Close

At the end of the budget or the list: three lines. Replied N, carried N (with the work prompts collected in one block for pasting), skipped N. Then set WAITING ON on every thread that got a final draft, and remove ONGOING TASKS from those threads only if no task exists for them.
