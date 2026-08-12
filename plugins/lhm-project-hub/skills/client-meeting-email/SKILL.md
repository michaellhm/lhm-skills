---
name: client-meeting-email
description: "Prepare a review-only client meeting bundle from Fathom evidence. Use after a client meeting to draft the follow-up email, structured meeting record, and proposed client, goal, and project updates. This skill never writes the vault, creates Gmail drafts, sends email, or changes BasicOps; approved mutations run as separate operations."
---

# Client Meeting Email

## Safety contract: preparation only

This skill is the authoritative **prepare** phase for a meeting capture. It may
read the registered client context and read-only Fathom evidence. It must return
a review bundle and proposed mutations only.

It must never, in the same run:

- create or edit vault/client files;
- create a Gmail draft or send mail;
- read or mutate BasicOps;
- invent a client folder or accept an arbitrary path from the request;
- treat the user's voice note as the complete meeting evidence when Fathom is available.

An initial meeting-wrap request authorises preparation only. Vault application
and Gmail draft creation require separate approvals bound to the reviewed
`run_id`, `workflow_version`, and `content_hash`. BasicOps is disabled until a
separate workflow explicitly replaces this rule.

Turn a Fathom meeting transcript, meeting summary, or both into a polished client
follow-up email for Local Health Marketing. The email must clearly explain what was
discussed, what was decided, who is responsible for each action, what happens next,
when the next meeting is scheduled, and where the recording can be accessed. The
final output must be professional, concise, client-friendly, and ready to paste
into Gmail.

## Step 0: Locate the client folder

Do this before touching Fathom and before writing any file. Everything this
skill saves lives inside the client's **existing** folder — creating a stray
new folder splits the client's records in two and breaks `post-meeting-review`'s
pickup.

1. List the workspace's client folders (the directory the team keeps clients
   in — check the current directory and its `clients/` subfolder for folders
   containing `client_profile.md` or `project-management/`).
2. Match the client's name against those folders, tolerating naming variants
   ("Raise the Bar" vs "raise-the-bar-psychology"). One clear match → use it.
3. Multiple candidates or no match → list what you found and ask. **Never
   create a new client folder without the user explicitly confirming that this
   is a brand-new client with no existing folder.**
4. `project-management/` sits **directly inside the client folder root**
   (`<client folder>/project-management/meetings/...` — see
   `references/folder-convention.md`). Never nest it under a subfolder and
   never create it anywhere else.

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

**Use nested sub-bullets whenever an action has parts.** A multi-part
deliverable reads far better as a parent line with indented dot points than as
one long sentence. For example:

```
- Once access is available, perform a complete Google Ads account review and
  record a Loom walkthrough explaining:
   - Current campaign structure
   - Existing keywords
   - Campaign performance
   - Areas for improvement
   - Recommendations moving forward
- Prepare a proposal outlining:
   - Management approach
   - Estimated investment
   - Recommended implementation plan
```

Never bury three deliverables in one bullet's prose — split them into
sub-bullets the reader can scan.

Preserve uncertainty where the meeting was not conclusive. Use: "Review and
recommend", "Confirm whether", "Test and report back", "Prepare a proposal",
"Send the requested information". Do not use "Complete immediately", "Implement",
or "Finalise" unless the meeting clearly committed to that outcome.

Do not assign an action to someone unless the transcript supports it.

### Next Steps rules

The Next Steps section describes the expected sequence of work. This is different
from Action Items: Action Items explain who must do what; Next Steps explain how
the project moves forward. Write it as a short bullet list in sequence order,
one step per line — never a paragraph. For example:

- LHM will complete the Google Ads review once access has been granted.
- A Loom walkthrough and recommendations will be prepared.
- The client will review the proposal internally.
- The campaign will proceed only after approval.

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

Thank you everyone for your time [today/yesterday/on date]. Below is a summary
of our discussion and the agreed action items.

Meeting Summary

[Topic]
[Summary — short paragraphs are fine here; this is the one narrative section.]

[Topic]
[Summary]

Key Decisions
- [Decision]
- [Decision]

Action Items

Local Health Marketing
- [Action]
- [Action with parts:]
   - [Part]
   - [Part]

[Client Name]
- [Action]
- [Action]

Next Steps
- [Step, in sequence order]
- [Step]
- [Step]

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

**Scannability rule:** outside the Meeting Summary, everything is dot points —
decisions, action items (with nested sub-bullets for multi-part work), and next
steps. The reader should be able to find their own name and their own tasks in
under ten seconds. The Meeting Summary is the only section where short
paragraphs belong.

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
- Action items with multiple parts use nested sub-bullets; Next Steps is a bullet list
- Files will save into the client folder Step 0 resolved — not a new folder

## Step 4: Return the review bundle

Return one structured bundle. Do not apply it. The bundle contains:

1. Meeting metadata and a source manifest (Fathom call ID/URL, retrieval time,
   summary/transcript availability and source hashes where the dispatcher supplies them).
2. The finished client email, ready for review.
3. The proposed meeting record content using this template:

   ```markdown
   # Meeting Notes — [Client Name]
   **Date:** YYYY-MM-DD
   **Meeting title:** [Fathom meeting title]
   **Attendees:** [if noted in transcript]
   **Recording:** [Fathom share/recording URL — always include; post-meeting-review and the team read it from here]
   **Client wrap email:** YYYY-MM-DD-client-wrap-email.md
   **Triaged:** no

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

4. `proposed_mutations[]` for the meeting note, wrap-email copy, client profile,
   goals and current projects. Each item includes the canonical registered
   relative path, operation, expected prior SHA-256 (or `null` only for an
   allowed new file), rationale and complete proposed content or patch. Never
   propose creating a client root.
5. A delegation pack and unresolved questions. Do not create BasicOps tasks.
6. Checks, warnings, `run_result`, and `work_state: needs_review`.
7. A deterministic `content_hash` over the reviewable email, meeting record and
   proposed mutations. If the host supplies an output schema, follow it exactly.

Present the human-readable review bundle and stop. State explicitly: no vault
files, Gmail drafts or BasicOps records were created or changed.

## Rules

- This skill prepares email content only; it does not create a Gmail draft and never sends.
- Checklist items and claims tick only on transcript evidence or the user's
  explicit confirmation — never invent action items, dates, or figures.
- Missing or unauthenticated Fathom: say what is missing and stop at
  `needs_context`; accept a dispatcher-supplied, hashed evidence package only
  when it is explicitly labelled compatibility mode. Gmail and BasicOps are
  outside this skill and must not be called.
- Credentials by reference only — never reproduce passwords, access details, or
  provider numbers from a transcript.
- No fabricated metrics or client data. The transcript outranks the summary;
  uncertainty is preserved, not resolved by guessing.
- This skill prepares the client email, meeting record, proposed state-file
  changes and delegation pack. Separate, approval-bound operations apply vault
  changes or create a Gmail draft. BasicOps remains disabled.
- Folder contract: read references/folder-convention.md (lhm-project-hub).
