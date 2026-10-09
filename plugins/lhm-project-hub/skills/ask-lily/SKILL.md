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

## 5. Keep the handback focused

Default to one decision at a time; honour a requested small batch. Overwhelmed requests use staff
flow's shortlist and help/pushback handling, not a full-board dump or mandatory client interview.
Return: answer/recommendation, dated evidence, coverage gaps, exact next action and next owner.
Escalate a genuine human scope/approval/capacity decision with a concise recommendation and links.
For an access/capability gap identify the system owner/repair need rather than telling staff to
keep retrying or bypass a denial.

An ordinary lookup is read-only. On an authorised save or settled operational handback, use the
owning workflow to update the existing shared client record and relevant task, verify read-back,
and distinguish proposed/saved/sent/applied states. Reusable learning goes through `lhm-learn:learn`
when requested; do not self-modify skills or expose private founder/staff context.

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
