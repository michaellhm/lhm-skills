---
name: post-meeting-review
description: "Review a saved meeting wrap, create one top-level Client Flow meeting card assigned to Michael with the reviewed email and proposed actions in Discussion, and correct proposed actions before Lily distributes them on explicit request. Use for meeting wrap, post-meeting review, meeting follow-up, or client call debrief. Distribution is separate from review and never starts TED."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Post-Meeting Review

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the meeting-action payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Review a client meeting's follow-up within the user-authorised scope:
files, BasicOps, and the team. Run this after `lhm-project-hub:client-meeting-email`
has captured the meeting.

## Step 1: Get the meeting record

**Option A. Saved meeting record (preferred)**
Look for `[client-folder]/project-management/meetings/YYYY-MM-DD-meeting-notes.md`
and the matching `-client-wrap-email.md`, saved by `lhm-project-hub:client-meeting-email`
when it ran right after the meeting. This is the primary path — no Fathom call
needed for undisputed items, since approved capture already extracted the
recording URL in the notes header.

**Find the record yourself — don't make the user point at it.** If the user
just said "meeting wrap" without naming a client or meeting, sweep the
shared Obsidian vault's `20 Clients` folders for `project-management/meetings/*-meeting-notes.md`
files from the last 14 days whose header says `Triaged: no` (or has no
`Triaged:` line — older captures predate the marker). Present what you found,
newest first ("Found an untriaged meeting for Raise the Bar captured yesterday —
work through that one?"), and confirm before proceeding. Only ask the user to
identify the meeting when the sweep finds nothing or several equally-recent
candidates.

**Use the saved record first.** Retrieve the original transcript yourself when
an action is disputed, the saved summary is incomplete or the user asks for verification.
Do not ask for a Fathom link or client re-introduction already available in the record. Asking again for what the capture step
already saved is the exact failure this split exists to prevent.

**Option B. Fathom MCP (fallback)**
If no saved meeting-notes file exists for this meeting — meaning
`client-meeting-email` hasn't run yet for it, not that today's meeting is
unusual — use the Fathom MCP tool to retrieve the transcript. Search by client
name or domain; `list_meetings` with `created_after` set to the last few days is
enough to find "the meeting I had today." Then extract the same fields Step 2.5
of `client-meeting-email` extracts: decisions made, action items (LHM vs.
client), client updates, strategic signals, compliance signals, and skill
triggers. Watch for compliance signals in anecdotes and asides, not just stated
decisions — they seldom arrive announced as decisions, and they're often the
most valuable thing in the meeting. Save the result to `meeting-notes.md`, using the exact template in
`client-meeting-email`'s Step 4, so the rest of this skill proceeds the same
way regardless of which option supplied it.

**Option C. Manual (fallback of the fallback)**
If Fathom MCP is not available or cannot find the meeting:
"Please paste the meeting transcript or notes and I'll work from that." Extract
the same fields as Option B and save `meeting-notes.md` the same way.

## Step 2: Update client state files

Resolve all state files below in the shared LHM Knowledge client root. For the hash-bound Josephine capture route, verify the separate vault application receipt first; never bypass its approval by reapplying unapproved proposed changes here. Check the overview/profile, Goals.md, Current Projects.md and affected detailed service/project notes, with each marked updated, unchanged or blocked. Read back applied records and preserve source meeting/date. An email draft or BasicOps card alone is not completion.


Everything below reads from the meeting record established in Step 1 (the saved
`meeting-notes.md`, or the equivalent extraction Step 1's Option B/C just
produced) rather than a live transcript.

### Update `goals.md`

Resolve this as the canonical goals record inside the Obsidian client root. **If it doesn't exist, do not create a blank template in this workflow.** Record the precise missing record, preserve goals explicitly evidenced by the meeting, and route creation through the owning client-onboarding/client-update workflow before a write. Continue the remaining review without inventing targets.

If any KPIs, budgets, or targets changed and the canonical file exists: update the relevant sections. Do not add placeholders for anything the meeting did not cover. Add a dated note:
```
<!-- Updated YYYY-MM-DD from meeting: [one-line summary of what changed] -->
```

### Update `current-projects.md`

Resolve this as the canonical active-project record inside the Obsidian client root. **If it doesn't exist, do not create a blank template in this workflow.** Preserve projects explicitly evidenced by the meeting and route creation through the owning kickoff/project-manager workflow. Continue the remaining review and report the gap.

When the canonical file exists, update it with real projects from this meeting. Do not add placeholder rows.

- Mark completed projects as completed (with date)
- Add new projects from action items
- Update status of existing projects if discussed
- Add new items to backlog if raised but not yet started

### Update `client_profile.md`
If any client details changed (name, services, contacts, business details): update the profile.

Do not trigger `client-update` from here. Propagation beyond the state files is handled in Step 3, which gathers the context `client-update` needs before invoking it.

### Resolve the client acronym

Runs every time, regardless of whether anything else in the profile changed — every BasicOps task title from Step 5 onward needs this.

Check `client_profile.md` for an `Acronym:` field.

- **Present:** use it as-is. No questions asked.
- **Missing:** derive one from the client's display name (first letter of each significant word, uppercase — "Your Story Physio" → `YSP`, "Australian Sports Physio" → `ASP`). Confirm with the user before proceeding (e.g. "Use YSP as the BasicOps short-code for Your Story Physio?"), since a bad auto-derivation is annoying to unwind once it's on ten task titles. Once confirmed, or the user gives a different value, write `Acronym: <value>` to `client_profile.md` so every future run just reads it.
- **`client_profile.md` doesn't exist yet:** derive an acronym for this run only, tell the user it wasn't saved because the profile doesn't exist, and don't block the rest of the skill on it.

## Step 3: Propagation sweep

**Do not skip this.** Updating the state files is not the same as propagating a decision. A service discontinued in a meeting will be sitting in sitemaps, keyword maps, redirect maps, briefs, GBP plans, and landing page copy, none of which Step 2 touches.

This step **detects**. It does not edit. `client-update` owns the editing.

**1. Search both the canonical Obsidian client root and the verified Current Clients working root** for every entity the meeting changed, discontinued, renamed, or added.

**2. Sort the hits into forward-looking artefacts and historical records,** using the pile definitions in `client-update`'s Step 2b. That table is the single source of truth for the split; do not restate it here. Forward-looking artefacts need updating. Historical records stay untouched, because editing them rewrites history and destroys the audit trail.

**3. Check for reversed decisions.** Search the forward-looking pile for anything marked *confirmed*, *signed off*, *decided*, or *approved* that the new decision invalidates. This is the failure mode that matters most, because a meeting can overturn work someone signed off days earlier without anyone noticing. When you find one, capture the original reasoning and who made the call, and carry both into the handoff. Do not resolve it yourself.

**4. For regulated services, check live advertising surfaces too**, not just the website. Google Business Profile categories, service lists, business descriptions and directory entries are all advertising. A compliance breach there is live exposure independent of any rebuild in progress.

**5. Hand off to `client-update`.** Invoke the skill and pass it four things: the change (and whether it is a substitution or a removal), the sorted file list, the conflicts found in item 3, and anything flagged in item 4. `client-update` picks up at its **Step 2e**, presents the whole picture to the user for confirmation, and only then edits. Nothing in the client folder changes until the user has signed off inside `client-update`.

**6. Come back and finish.** The handoff is a detour, not an exit. When `client-update` completes, return here and continue at Step 4. Steps 4 through 7 have not run yet. Hold `client-update`'s downstream implications from its own Step 4 and fold them into Step 5's task list below, alongside the meeting record's skill triggers, so the user gets one set of routed follow-on work rather than two nearly identical prompts.

**If nothing came back from the grep,** say so in a line and move on. No sweep findings is a normal outcome for a meeting that changed no entities.

## Step 4: Save the meeting card and reviewed task register

Read `../basicops-task-manager/references/meeting-wrap.md` in full. It is the
controlling meeting-specific contract, including its exception to generic
Description and client-parent rules. Route all authorised BasicOps writes through
`basicops-task-manager`.

Find or create the client-and-date meeting task at top level on `*Client Flow`.
Assign the single card to Michael. Put the exact reviewed email in Discussion followed
by “Proposed actions — awaiting Michael’s review”; create no action cards during capture;
do not assume `client-meeting-email` already wrote anything in BasicOps. That skill
is preparation-only. Resolve the approved email from the authenticated email source
or its matching saved artifact. If unavailable, report the gap without claiming the
card replicates the email. Preserve approved corrections separately and link actions
by verified IDs. Show proposed owners and disputed/existing work for review.

Keep a compact set of concrete actions with recognisable completion conditions.
Consolidate related client inputs. Resolve explicit meeting owners first, then
current canonical staff responsibilities, asking only for genuine ambiguity.
Owner resolution proposes responsibility; it does not authorise board moves.

## Step 5: Michael reviews and delegates

Reviewing, saving or approving the wrap does not route actions. Stop after updating
the reviewed register unless Michael has explicitly authorised task creation or delegation. Use
`meeting-to-action` for his interactive scope, ownership and existing-work review.
If distribution is already authorised in the same request, honour that authority
without asking again and apply only the reviewed scope.

For distribution follow the numbered procedure in `meeting-wrap.md`: reuse action
IDs, assign the named humans, move to their verified Inbox sections, read back the
result, refresh the Discussion register and stop. Do not invoke Auto-run, research,
production planning, Ted, Chief of Staff or specialist execution from this skill.

## Step 6: Keep email and review state accurate

Reuse the reviewed email; do not automatically generate or send a replacement.
If a new draft is requested, prepare it through the approved email workflow.
Record review and distribution as separate states in the meeting record, with
verified task links and unresolved items. Mark a meeting reviewed only after review,
and distributed only after read-back confirms all approved moves. Neither state
means the actions are complete or production has started.

## Step 7: Self-improvement

Three things to offer at the end of the run:

1. **Client facts.** If the meeting revealed anything about how this client works that isn't in `client_profile.md` (systems they use, who does what, standing constraints, compliance posture), offer to add it.
2. **Skill learnings.** If anything went wrong in this run, or the user corrected you, offer to run `/lhm-learn:learn` so it lands in this skill's `LEARNED.md` rather than being lost. Tool quirks, output format corrections, workflow steps that needed adjusting, and anything the user had to tell you twice all belong there.
3. **Canonical context gaps.** If `goals.md` or `current-projects.md` was missing, remind the user which owning Project Hub workflow it was routed to; do not claim a blank state file was created.

## Rules

- Folder contract: read references/folder-convention.md (lhm-project-hub).
