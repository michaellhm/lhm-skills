---
name: client-meeting-email
description: "Turn a Fathom meeting summary and transcript into a polished, client-ready follow-up email for Local Health Marketing, and capture the meeting for follow-up. Use this after a client meeting when the user says 'client meeting email', 'meeting follow-up email', 'post meeting client email', 'client wrap email', 'draft the client follow-up', or 'send the client the meeting summary'. Pulls the Fathom summary, transcript, and recording link, verifies decisions and action owners against the transcript, and produces one Gmail-ready email: meeting summary by topic, key decisions, action items grouped by owner, next steps, next meeting, and the recording link. Also saves a structured meeting-notes file, creates or moves the client's BasicOps card to Follow Up, and posts one meeting-summary discussion note close to the email. This is the capture step; the separate follow-up triage pass — state-file updates, the propagation sweep, and turning action items into assigned subtasks — is `lhm-project-hub:post-meeting-review`, which reads what this skill saves instead of re-pulling Fathom."
---

# Client Meeting Email

Turn a Fathom meeting transcript, meeting summary, or both into a polished client
follow-up email for Local Health Marketing. The email must clearly explain what was
discussed, what was decided, who is responsible for each action, what happens next,
when the next meeting is scheduled, and where the recording can be accessed. The
final output must be professional, concise, client-friendly, and ready to paste
into Gmail.

## Step 1: Gather inputs

Collect whatever is available. The Fathom MCP is the preferred source:

1. `list_meetings` (filter by `created_after` for the last few days) to find the
   meeting; ask which one if ambiguous. If the user pasted a Fathom URL or call ID,
   resolve it directly with `get_recording_by_url` / `get_recording_by_call_id`.
2. `get_meeting_summary` for the summary and action items.
3. `get_meeting_transcript` for the full transcript (pass the meeting URL so
   timestamped deep links are available).
4. The meeting/share URL doubles as the recording link for the email.

If Fathom is unavailable, ask the user to paste the summary and/or transcript —
never silently proceed with less than they could give you.

Also collect from the user when not evident from the transcript:

- Meeting title, date, client name, attendees
- Next meeting date and time (only if confirmed — see Dates and Scheduling)
- Additional internal context
- Instructions about anything that should not be included (internal-only items)

Use all available information, but treat the full transcript as the most reliable
source. If both a Fathom summary and transcript are provided:

1. Use the summary to identify the main themes.
2. Use the transcript to verify decisions, responsibilities, dates, numbers, and context.
3. Resolve conflicts in favour of the transcript.
4. Do not copy the Fathom summary word-for-word.

## Step 2: Draft the email

Create a client-ready follow-up email using this structure:

1. Subject line
2. Greeting
3. Short opening paragraph
4. Meeting Summary
5. Action Items grouped by owner
6. Next Steps
7. Next meeting details, if confirmed
8. Meeting recording
9. Professional sign-off

Add a **Key Decisions** section when the meeting contains important approvals,
scope changes, strategic decisions, or agreed exclusions.

### Writing style

Write in the voice of Local Health Marketing. The tone should be professional,
warm, clear, direct, collaborative, confident without sounding corporate, and
detailed enough to be useful but not transcript-like. Use Australian English.

Avoid:

- Generic AI language
- Excessive enthusiasm
- Marketing clichés
- Repeating the same information in multiple sections
- Overly long paragraphs
- Reporting every minor comment
- Making the email sound like formal meeting minutes
- Mentioning that AI was used
- Em dashes
- Unsupported assumptions

Do not refer to attendees by first name unless it is clear and appropriate.

### Meeting Summary rules

The Meeting Summary should explain the major discussion areas in plain English.
Organise it using short descriptive subheadings, such as: Website Rebuild, Google
Ads Performance, CRM Workflow, Content Strategy, Reporting and Tracking, AI and
Automation, Staffing and Capacity.

Under each subheading:

- Summarise the issue or opportunity
- Explain the agreed direction
- Include important reasoning where useful
- Mention material performance figures
- Leave out casual conversation and unrelated tangents

Do not turn the summary into a chronological transcript. Focus on decisions,
direction, risks, and outcomes.

### Key Decisions rules

Include a Key Decisions section when appropriate. Use it for clear outcomes such
as: a service was approved or removed; a website direction was agreed; a campaign
budget will remain unchanged; a workflow was accepted; a tool or platform was
selected; a project was paused; a responsibility was assigned; a naming or scope
decision was finalised.

Keep this section concise. Do not repeat every decision again in the Action Items
section unless a task is required to implement it.

### Action Item rules

Group action items by owner. Typical headings: Local Health Marketing, [Client
Name], Michael, Clinic Team, External Provider.

Each action item must:

- Begin with a clear verb
- Describe a specific outcome
- Include relevant context where needed
- Identify dependencies where relevant
- Avoid vague wording such as "look into" unless no firmer commitment was made

Preserve uncertainty where the meeting was not conclusive. Use: "Review and
recommend", "Confirm whether", "Test and report back", "Prepare a proposal",
"Send the requested information". Do not use "Complete immediately", "Implement",
or "Finalise" unless the meeting clearly committed to that outcome.

Do not assign an action to someone unless the transcript supports it.

### Next Steps rules

The Next Steps section describes the expected sequence of work. This is different
from Action Items: Action Items explain who must do what; Next Steps explain how
the project moves forward. For example:

1. LHM will complete the Google Ads review after access is granted.
2. A Loom walkthrough and recommendations will be prepared.
3. The client will review the proposal internally.
4. The campaign will proceed only after approval.

Keep this section focused on the next phase, not the full long-term roadmap.

### Dates and scheduling

Only include a next meeting date if it was clearly confirmed. Verify the day of
the week, calendar date, month, year, time, and time zone where relevant. If the
transcript contains conflicting dates or an obviously incorrect date, do not
guess — write: "The next meeting timing will be confirmed separately."

If a recurring cadence was agreed, mention it after the confirmed meeting date,
e.g. "Future meetings will move to the first Wednesday of each month."

### Numbers and performance data

Include important numbers when they help explain performance or decisions:
bookings, leads, ad spend, cost per booking, revenue, conversion rates,
month-on-month changes, location performance.

Do not overstate precision — use "approximately" when figures were discussed
informally. Do not calculate new metrics unless the calculation is
straightforward and clearly supported by the transcript.

### Compliance and sensitive information

Do not include:

- Private internal frustrations
- Offhand remarks about staff
- Unconfirmed financial information
- Patient-identifying information
- Passwords, access credentials, API keys, or provider numbers
- Personal comments that are not relevant to the client
- Speculative claims presented as facts
- Anything the user marks as internal-only

When healthcare advertising or regulatory issues are discussed, preserve the
practical decision without giving formal legal advice. For example: "The service
page will be removed to avoid advertising a service that is not currently
available."

### Output format

Produce one polished email only, in this format:

```
Subject: [Client or Project] | Meeting Summary & Action Items

Hi [Names],

Thanks again for your time [today/yesterday/on date].

[One short paragraph summarising the main focus of the meeting.]

Meeting Summary

[Topic]
[Summary]

[Topic]
[Summary]

Key Decisions
- [Decision]
- [Decision]

Action Items

Local Health Marketing
- [Action]
- [Action]

[Client Name]
- [Action]
- [Action]

Next Steps
[Short sequence of what will happen next.]

Our next meeting is scheduled for [date and time].

For anyone who would like to revisit the discussion, the meeting recording is
available below.

Meeting Recording: [link]

Thanks again.

Kind regards,
Michael Colman
Local Health Marketing
```

Only include the Key Decisions section where useful.

## Step 2.5: Extract the structured meeting record

Alongside the email, extract the same structured record `post-meeting-review`
used to pull directly from the transcript. This now happens once, here, so the
follow-up triage pass can work from saved files instead of re-fetching Fathom.

From the same transcript already in hand, extract:

**Decisions made:**
- Concrete decisions the client or team agreed to

**Action items:**
- Who needs to do what by when (note if it's a client action or LHM action)

**Client updates:**
- Any changes to client details, services, branding, contacts
- Any changes to goals, budgets, or targets
- Any problems or complaints raised

**Strategic signals:**
- Anything that changes priorities (new competitor, budget cut, new service launch, etc.)

**Compliance signals:**
- Anything with regulatory consequence (AHPRA, TGA, advertising standards, privacy)
- Watch for these in anecdotes and asides, not just in stated decisions. They seldom
  arrive announced as decisions, and they are often the most valuable thing in the
  meeting.
- A service discontinued, a practitioner departed, a claim the client wants to
  make, a testimonial they want to use: all compliance signals. Record the
  reasoning, not just the outcome — `post-meeting-review` writes this into
  `client_profile.md` as standing posture.

**Skill triggers:**
- Anything that should prompt running a skill later (poor Ads performance → zone
  check, content not ranking → SEO review, etc.)
- A commitment to run a client briefing before content gets written ("we'll do a
  briefly," "we'll brief them on the next post") — flag this separately; it routes
  differently in `post-meeting-review`'s follow-up triage.

This extraction feeds Step 4's `meeting-notes.md` file directly — keep it in note
form here, not prose, since `post-meeting-review` re-reads it as data.

## Step 3: Quality check

Before finalising the email, verify:

- The client and attendee names are correct
- The meeting date is correct
- All major discussion topics are represented
- Decisions are separated from discussion
- Action items are assigned to the correct owner
- No unsupported action items have been invented
- Next Steps describe sequence, not duplicate tasks
- Performance figures match the transcript
- The next meeting date is accurate
- The recording link is included
- The email can be sent without editing
- The tone sounds like Local Health Marketing
- The email is not unnecessarily long

## Step 4: Deliver

1. Present the finished email in chat, ready to paste into Gmail.
2. Offer to create a Gmail draft via the Gmail MCP `create_draft` (draft only —
   never send). If Gmail MCP is unavailable, say so; the pasted version stands.
3. Save a copy to `clients/<client>/project-management/meetings/YYYY-MM-DD-client-wrap-email.md`
   so the follow-up trail lives with the meeting record. Create
   `project-management/meetings/` if it doesn't exist yet — see
   `references/folder-convention.md`.
4. Save the Step 2.5 extraction to
   `clients/<client>/project-management/meetings/YYYY-MM-DD-meeting-notes.md`:

   ```markdown
   # Meeting Notes — [Client Name]
   **Date:** YYYY-MM-DD
   **Attendees:** [if noted in transcript]

   ## Decisions
   -

   ## Action Items
   ### LHM
   - [ ] [action] (due: [date if mentioned])

   ### Client
   - [ ] [action]

   ## Client Updates
   -

   ## Strategic Signals
   -

   ## Compliance Signals
   -

   ## Skill Triggers
   -

   ## Recommended Next Steps
   -
   ```

5. Find the client's BasicOps card: call `list_tasks_in_project` with
   `projectId: 68655` (board `*Client Flow`) and `filter_title` set to the
   client's short/common name. If nothing matches, call it again without
   `filter_title` and scan titles for a case-insensitive match.
   - **No match:** ask the user "No client card found in *Client Flow for
     [Client]. Want me to create one?" If yes, `create_task` with
     `projectId: 68655` and a title matching the client's short name. If no,
     skip to step 9 and note that the BasicOps card step was skipped.
   - **One match:** that's the card.
   - **Multiple matches:** list them (title + URL from `link_to_task`) and ask
     the user which one is the client's card.
6. Check the card's existing discussion (`list_messages_in_task`) for a
   meeting-summary note already posted for this meeting's date — this skill
   may have already run for it, including under the pre-split workflow. If one
   is found, don't move the card or post a second note; tell the user the card
   is already up to date for this meeting and skip to step 9.
7. `update_task` with `taskId: <card id>`, `section: 107750` (`Follow Up`),
   moving the card to Follow Up.
8. `create_message_in_task` on the client card with one discussion message,
   close to the email itself: meeting summary by topic, key decisions, action
   items grouped by owner, next steps, and the recording link — the email's own
   content, minus the greeting and sign-off, not a separately-structured
   internal briefing. Discussion messages take raw HTML — do not escape it to
   entities, because `&lt;p&gt;` renders as literal text. If you get it wrong,
   `delete_message` with the returned id and repost.
9. Remind the user of the 24-hour SLA for meeting-wrap emails
   (references/cadences.md) if the meeting was more than a day ago.
10. Close with: "Meeting notes and BasicOps card are ready. Run
    `lhm-project-hub:post-meeting-review` when you're ready to work through
    follow-ups."

## Rules

- Client-facing emails are drafts only — never send; the human sends.
- Checklist items and claims tick only on transcript evidence or the user's
  explicit confirmation — never invent action items, dates, or figures.
- Missing or unauthenticated MCP (Fathom, Gmail, BasicOps): say what is missing
  and fall back to pasted content or manual steps — never silently skip.
- Credentials by reference only — never reproduce passwords, access details, or
  provider numbers from a transcript.
- No fabricated metrics or client data. The transcript outranks the summary;
  uncertainty is preserved, not resolved by guessing.
- This skill produces the client email, saves the meeting record, and stands up
  the BasicOps card with a meeting-summary note. `lhm-project-hub:post-meeting-review`
  is the separate follow-up triage pass — it reads what this skill saves rather
  than re-pulling Fathom, and turns action items into assigned subtasks.
- Folder contract: read references/folder-convention.md (lhm-project-hub).
