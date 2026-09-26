---
name: inbox-triage
description: Run Michael's morning inbox pre-work. Classifies every inbox thread by tier, sets working-state labels, creates BasicOps tasks for real work, drafts voice-matched replies in Gmail, walks this week's Obsidian tasks, and writes one brief. Use when the user says 'triage my inbox', 'morning inbox', 'sort my emails', 'what's in my inbox', 'inbox brief', or when a scheduled morning routine runs. Drafts only, never sends.
---

# Inbox triage

Produce today's brief. Everything else (labels, tasks, drafts) exists to make the brief true.

Read first, every run: `${CLAUDE_PLUGIN_ROOT}/references/safety-rules.md`, `routing.md`, `labels.md`, `brief-format.md`. If the Obsidian vault is reachable, prefer `LHM/Operations/email-routing.md` over the bundled routing file.

## Step 0: Tools check

Confirm a Gmail tool that can search threads, read a thread, label a thread, and create a draft is available. Confirm BasicOps is available. If Gmail is missing, stop and say so. If BasicOps is missing, run anyway but write every would-be task into "Needs a call from you" instead of creating it.

## Step 1: Pull the inbox

Search `in:inbox -label:"***MICHAEL: PERSONAL" -is:starred`, page until exhausted. For each thread capture: last sender, last message date, subject, existing labels, snippet. Open the full thread only for threads that survive Step 2 as Tier 1 or 2.

Also search `label:"*** 4.  WAITING ON"` to build the Waiting-on-them section, and `label:"*** !MICHAEL-ONGOING TASKS" newer_than:14d` to catch live threads that left the inbox.

## Step 2: Classify

Assign every thread one tier from routing.md (1 Michael, 2 Josephine, 3 team, 4 noise) and a confidence: high, medium, low. Rules of thumb:

- Last sender is Josephine, Kristalyn, Jaimee, or Aiya, and the client is replying to them: Tier 3.
- Josephine's holding template is the last LHM message: Tier 1, and the wait clock started when the client wrote.
- Sender domain matches a Tier 4 pattern: Tier 4, high confidence, skip.
- Any thread from an active client where confidence is below high: Tier 1 so it lands in front of Michael, and say why in the block.
- Michael was the last sender: Waiting on them, not Reply today.

Low-confidence results never get a label or a task; they go to "Needs a call from you".

## Step 3: Labels (high and medium confidence only)

- Tier 1 with real work behind it: set ONGOING TASKS.
- Tier 3: set FYI, archive (remove INBOX).
- Tier 4: archive. No label.
- A client "Meeting Summary & Action Items" email: set MEETING WRAP and, if an older MEETING WRAP exists for the same client, move the older one to Done.
- Never set Done on an active-client thread in this skill; that belongs to inbox-tidy with approval.

Record every change for the Housekeeping section.

## Step 4: Tasks

For each Tier 1 thread that needs work beyond a reply (a build, an analysis, a change in a client system, a document):

1. Search BasicOps for an existing task: client name plus two keywords from the subject. If found, add a comment with the Gmail thread link and reuse it.
2. Otherwise create one in the client's project (fall back to Michael's task board), title "Client: ask in six words", description containing the ask in one paragraph, the Gmail thread link, and the Obsidian client path. Due date: leave unset unless the client named one.
3. Route the write through `lhm-project-hub:basicops-task-manager` when that skill is present; it is the mutation boundary for BasicOps.

## Step 5: Drafts

For every Reply-today thread, create a Gmail draft as a reply on that thread using `${CLAUDE_PLUGIN_ROOT}/references/voice-profile.md`. Follow the email-drafts skill's rules (register by audience, three-beat shape, "Could you", the close). If the correct reply depends on information Michael has and the skill does not (a price, a decision, a date), draft it with a bracketed placeholder like [confirm date] rather than inventing. Cap at 10 drafts per run; oldest-waiting first.

## Step 6: This week's tasks

Read the current weekly flow note in Obsidian (the note Michael created for this week; it carries the week tag, for example `#week-39`). List each tagged task with its BasicOps link. Where the task description holds a Gmail thread link, fetch the thread's last message date and sender and flag any with an unanswered client message. If the vault is not reachable, write "Weekly flow not reachable this run" and move on.

## Step 7: Write the brief

Follow brief-format.md exactly. Save to `Inbox Briefs/YYYY-MM-DD.md` in the vault when reachable; always also output it in full in the chat. Finish with the Housekeeping section so every change is reversible.

## Step 8: Record for learning

Append one line per draft to `${CLAUDE_PLUGIN_ROOT}/../inbox-log/drafts.jsonl` (create if missing): `{"date","thread_id","draft_id","recipient","tier","audience_register","word_count"}`. The email-learn skill reads this the next day. If the plugin directory is read-only, write it to the vault at `Inbox Briefs/log/drafts.jsonl` instead.
