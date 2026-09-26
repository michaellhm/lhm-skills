# The morning brief

One file per run, Markdown, written to `Inbox Briefs/YYYY-MM-DD.md` in the Obsidian vault (and, until Hermes runs this, also pasted into the chat where triage ran). It is the contract between triage (which writes it) and the email session or ChatGPT (which reads it). Keep the sections and their order fixed so the reader can rely on them.

```markdown
# Inbox brief, Thu 26 Sep 2026

Inbox: 37 threads, 24 unread. Triage touched 19 (labels), created 3 tasks, drafted 6 replies. Personal: 2 unread, untouched.

## Reply today (N)
Sorted oldest-waiting first. One block per thread.

### 1. Heel Centre, Adam: Cliniko conversion issue and Ads budget from 30/9
Waiting: 9 days (last from Adam 17 Sep). Tier 1. Task: BO-1234 (link). Thread: (gmail link)
Ask: what the Cliniko/conversion issue was; wants Ads budget bumped from 30 Sep.
Context: Michael rebuilt the Cliniko sync (thread 12 Sep), review messages not reactivated yet.
Draft: saved in Gmail as draft (link). Preview:
> Hey mate,
> Sorry for the slow reply on this...
Work prompt (for ChatGPT):
> Client: Heel Centre. Ask: explain the Cliniko conversion gap and confirm the Ads budget change from 30/9. Thread: (link). Obsidian: Clients/Heel Centre/client_profile.md, project-management/google-ads.md. Done looks like: reply sent, budget change scheduled in Google Ads, task BO-1234 updated.

### 2. ...

## Josephine has it (N)
One line each: sender, subject, what she will do, whether she has acknowledged yet. Flag any where the holding template went out more than 1 business day ago with no follow-up from Michael.

## Team is running it (N)
One line each: client, subject, who on the team. Labelled FYI.

## Waiting on them (N)
Threads Michael replied to and is waiting on. Sender, subject, days waiting. Suggest a nudge draft for anything past 5 business days.

## This week's tasks (from Obsidian weekly flow)
For each task tagged with this week's tag: task, due, BasicOps link, and, if a Gmail thread is linked, the last message date and who sent it. Highlight any task whose linked thread has an unanswered client message.

## Needs a call from you
Anything triage could not classify with confidence, plus proposed label changes on protected client threads. Nothing here has been actioned.

## Housekeeping done this run
Labels set/removed (thread, from, to), tasks created (title, link), drafts created (thread, link). Reversible.
```

## Rules for writing the brief

- Reply today is capped at 10. If more qualify, the rest go under a "Also waiting" line with count and a pointer to the labels.
- Every Reply-today block has a draft in Gmail. No draft, no block; it goes to "Needs a call from you" instead.
- Waiting time is measured from the last message the other party sent, not from thread start.
- The work prompt is only included when the reply needs work behind it (a build, an analysis, a doc). A pure reply gets no work prompt.
- Never quote more than the first three lines of a draft in the brief; the full draft is in Gmail.
