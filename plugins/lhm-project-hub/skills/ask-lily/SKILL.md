---
name: ask-lily
description: Help LHM team members find source-grounded client context, promises, scope, priorities and the right process or skill. Use for "ask Lily", "where do I find help", "what did Michael promise", "has this been discussed", "is this in scope", "which skill should I use", "help me prioritise", or "I am overwhelmed". Routes to existing Project Hub skills, checks actual source access and prepares a BasicOps Lily request when wider evidence is unavailable; never assumes Michael's email or Fathom access.
---

# Ask Lily — Team help entry point

Give the person a useful answer or one concrete next step without requiring them to know the skill
catalogue. This skill can run in Claude, Codex or an authorised Hermes route. Loading it does not
connect to the live Lily bot, inherit her identity or grant access to Michael's mailbox.

Read [client knowledge routing](../../references/obsidian-context-contract.md) before client work
and [agent orchestration](../../references/agent-orchestration-contract.md) when coordinating skills.

## 1. Understand the question and actual access

Reuse the supplied client, task link, question and confirmed context. Do not demand a client for a
general process question. Resolve ambiguous names with one material question. Verify authenticated
identity and authorised scope; read the person's shared People profile when role/authority matters.
Never assume a display name proves identity or that a staff member can read founder-private records.

Identify only sources needed for the question: shared Obsidian, live BasicOps discussions, relevant
email threads, Fathom transcripts, installed skills/SOPs or repository instructions. Verify the
actual available tools and successful reads. A report's access, a connected browser, a file path or
another user's conversation does not prove this session has access. Do not change permissions or
credentials to fill a gap.

## 2. Choose the smallest existing workflow

| Question | Route |
| --- | --- |
| Today's priorities, weekly commitments, overload or "I'm overwhelmed" | `lhm-project-hub:staff-weekly-flow`; preserve its personal identity, saved commitments and overwhelmed mode |
| Website status, next stage, blocker or review/launch handoff | `lhm-project-hub:website-project-cockpit` |
| Rough request, scope clarification, missing inputs or human handoff | `lhm-project-hub:team-work-brief` |
| How to perform/plan an existing BasicOps production task, or identify its SOP | `lhm-project-hub:hermes-production-plan`; planning is not a production launch |
| Task creation, discussion, board changes or completion | `lhm-project-hub:basicops-task-manager`, only for exact authorised mutations |
| General client fact, historical promise or which skill/process to use | Bounded evidence lookup below; recommend the verified existing skill when applicable |

Read/load the relevant installed skill rather than reproducing its workflow. Invoke only the mode
needed by the question; a help request is not permission to start production, send messages, accept
commitments or change tasks. Status-only help returns a recommendation without automatically
executing it. If the target is missing, report `route_unavailable` with its exact identifier;
do not invent a slash command or pretend a recommended skill ran.

## 3. Answer from evidence

Read canonical shared client context and the relevant current task discussion, including replies.
For process questions search shared `60 Knowledge` and `70 SOPs`, then inspect the existing installed
skill/catalogue. Distinguish guidance from executable skill code and ready capability from proposals.

For promises/scope, read dated relevant source email threads or Fathom transcripts when authorised.
Separate a proposal, explicit agreement, later correction, delivered result and current dependency.
Show source dates/links and reconcile later material evidence; silence is not approval. A historical
meeting statement alone does not prove today's project state. Do not trigger a meeting-wrap review
or create a meeting card just to answer a historical question.

When sources conflict or are unavailable, state exactly what was checked and what remains unknown.
"No mention found in the checked sources" is not "never discussed". Do not ask a person to reconstruct
information that an accessible authorised source can answer.

## 4. Use Lily in BasicOps for a wider-context gap

When Claude/Codex lacks required email, Fathom or other evidence, answer the verified portion and
prepare one copy-ready request for Lily in BasicOps: client and task link, exact question, bounded
source/date range, known facts with links, missing evidence, and desired answer with source dates.
Ask Lily to verify her own source coverage; do not promise that her live route is connected.

If the user explicitly asks to post the request, use the verified intended BasicOps task/discussion
and route the exact approved text through basicops-task-manager. Resolve Lily's bot/mention identity
from verified configuration, never invent a user ID. Verify the post and mention where supported.
If route/identity is unavailable, return the draft and exact gap. Preparing/posting a request does
not mean Lily received, answered or completed it. Never post or message another system merely
because this skill recommends asking Lily.

## 5. Resolve and retain missing knowledge

Do not stop at "we don't know". Reuse the question and checked-source links to pursue the smallest
missing fact through available authorised sources. Read relevant full discussions, email replies,
meeting evidence and linked canonical records before escalating. Use an existing authorised
research route when available; otherwise return a source-specific request under section 4.
An unavailable source is a coverage gap, not evidence that the answer does not exist.

If the answer requires a person, identify the responsible owner from verified role/task context and
prepare one exact question with evidence, why it matters and what it releases. Ask the current user
only when they are the appropriate source. External contact, posting, task creation or assignment
still requires the owning workflow's authority; missing knowledge does not grant sending permission.
Record the unresolved question under Open questions in its existing shared client/project record,
with date, checked sources, next owner (or owner unconfirmed), pending request state and checkpoint
only if known. Reuse an equivalent open question instead of creating another. Missing canonical
records remain a routing gap for onboarding/client-update, not a new substitute folder.

Michael's standing direction for this skill includes bounded knowledge capture during normal help:
save evidenced client facts and explicit operational decisions in their existing canonical shared
Obsidian home without an extra generic save question. An explicit review-only/do-not-save request
wins. Do not record private reflections, unapproved proposals or speculative answers as facts.

When the answer arrives in this session or a later resumed session, verify its source and authority,
re-read the existing note, reconcile newer facts and save the dated answer with evidence and any
material owner/next action. Mark the existing open question resolved with a link to the answer;
preserve its history. If action is needed, route the exact authorised BasicOps update through the
task manager and read it back. Do not close a task merely because its knowledge question is answered.

For LHM-method questions, use the existing relevant Knowledge/SOP record. A one-off workaround stays
attributed project evidence; a new agency-wide method or skill rule remains a proposal until the
required approval. Do not rewrite executable skills or install updates automatically.

Read back every changed record and show the saved link. If retrieval, authority, writing or read-back
fails, retain the exact unresolved question, destination, next owner and restart step as pending;
never say "learned/saved" for a draft or failed write. Future lookups read the canonical answer first,
check freshness and later corrections, and reuse it instead of asking the same settled question.
No background follow-up or automatic monitoring is created merely by leaving a question open.

## 6. Keep the handback focused

Default to one decision at a time; honour a requested small batch. Overwhelmed requests use staff
flow's shortlist and help/pushback handling, not a full-board dump or mandatory client interview.
Return: answer/recommendation, dated evidence, coverage gaps, exact next action and next owner.
Escalate a genuine human scope/approval/capacity decision with a concise recommendation and links.
For an access/capability gap identify the system owner/repair need rather than telling staff to
keep retrying or bypass a denial.

Normal help includes the bounded knowledge capture in section 5; explicit review-only help stays
read-only. Distinguish retrieved, unanswered, proposed, saved/verified, sent and task-applied states.
Reusable learning goes through `lhm-learn:learn` when requested; do not self-modify skills or expose
private founder/staff context.

## Acceptance scenarios

- Staff asks "I'm overwhelmed": load staff-weekly-flow with verified identity, offer its bounded
  essential/unblock/communication choices; no full backlog, founder-private read or task mutation.
- "What did Michael promise?" with Obsidian/BasicOps but no mail/Fathom: cite checked evidence,
  state the gap and prepare a source-specific Lily request; never claim a complete history search.
- "Is this in scope?" with a later approved correction: show dated agreement and correction;
  if authority is still unclear, prepare a precise decision for the owner rather than inventing scope.
- General "Which skill?" without a client: inspect process guidance and installed catalogue,
  recommend one matching existing skill; do not force client selection or run a kickoff.
- "Ask Lily" without explicit posting: return a draft, no BasicOps write. Explicit posting with
  unknown bot ID: do not invent a mention; surface the exact route gap before claiming delivery.
- Matching skill unavailable: report route_unavailable and its verified identifier, no fake execution.

- Missing client fact: exhaust authorised relevant evidence, save one open question with source
  coverage and next owner, prepare a specific request; no implicit message send or task assignment.
- Confirmed reply resolves the question: save/read back the canonical answer and resolution link,
  preserve history and unrelated edits; a later lookup reuses it after a freshness check.
- Repeated query or interrupted write: re-read and deduplicate by question/source; failed persistence
  stays pending, no duplicate note or claim of successful learning.
- New cross-client method or explicit review-only request: propose the rule without publishing it;
  review-only help writes no note. No task is completed solely because an answer was found.
