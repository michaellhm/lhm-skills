# Scheduled task prompts

Two prompts. Create each as a scheduled task inside the "LHM Inbox" project so the project files and instructions apply. Whether a scheduled task can use the Gmail connector depends on the current ChatGPT build; test the morning one manually first ("run the morning brief") and only schedule it once it works unattended. If it cannot reach Gmail on a schedule, keep it as the first thing you type each morning instead.

## 1. Morning brief (weekdays 7:15am Melbourne)

```
Build today's inbox brief following brief-format.md and routing.md in this project.

1. Search Gmail: in:inbox, excluding the label "***MICHAEL: PERSONAL" and starred threads. Also pull label "*** 4.  WAITING ON".
2. Classify each thread by tier using routing.md. Tier 4 noise is not listed.
3. For every Tier 1 thread where someone is waiting on Michael, draft a reply in his voice per voice-profile.md and save it as a Gmail draft on that thread. Cap at 10, oldest-waiting first. Leave [confirm: ...] rather than guessing facts.
4. For any Tier 1 thread that needs work beyond a reply, include a work prompt block.
5. Do not change labels, archive, or send anything.
6. Output the brief in full, Reply-today first. Finish with one line: drafts created N, threads needing a decision N.
```

## 2. Corrections check (weekdays 6:45am Melbourne, before the brief)

```
Compare yesterday's drafts to what Michael actually sent.

1. Search Gmail: in:sent newer_than:1d. For each sent message, check whether a draft existed on that thread yesterday (the brief listed it) and whether the sent text differs from the draft.
2. For each difference, write one literal line: recipient, audience, category (opener, close, length, register, removed phrase, added phrase, fact, structure, ask), what changed.
3. Sent emails with no prior draft: note them as cold-written, with word count and audience.
4. If any category repeats three or more times across the last week, propose a one-line rule in the style of voice-profile.md, with the evidence.
5. Output: unchanged N, edited N, unsent N, then the lines, then any proposed rules. Do not edit project files.
```

When a proposed rule is accepted, Michael pastes it into the "Learned adjustments" section of voice-profile.md in the plugin repo (canonical), then re-uploads the file here.
