---
name: sales-handover
description: "Hand a newly-closed client from sales (Michael or Marlon) to the delivery team. Use this right after a sale closes, or when the user says 'sales handover', 'handover to KP', 'we just signed a client', 'closed a deal', 'new client handover', or 'hand this client over'. Pulls the sales call from Fathom, interviews the salesperson for institutional knowledge, produces the internal handover doc, seeds the client profile, creates the BasicOps card and Phase 1 billing task for Josephine, and kicks off client-onboarding."
---

# Sales Handover

Hand a newly-closed client from sales to delivery, capturing everything sales knows about them before it evaporates. Run this immediately after a deal closes — the longer the gap, the more of the salesperson's institutional knowledge gets lost.

## Step 1: Identify client + package

Ask if not already given:

- **Client name.**
- **Package sold** + **monthly fee** + **add-ons.**

Validate the fee against `references/team-roster.md`'s "Canonical accounts & values" table — Tier 1 is $1,750/month for Google Ads + Google Maps management, plus whatever add-ons were signed. If what the salesperson quotes doesn't match the canonical figure, **do not silently correct it.** Flag the discrepancy and ask which is right: "Team roster has Tier 1 at $1,750/month — you said $[X]. Which is correct for this client?" Record whatever the salesperson confirms; note the discrepancy in the handover doc's Package & Commercials section either way, so billing (Josephine) isn't blindsided later.

## Step 2: Create/locate the client folder

Follow `references/folder-convention.md`. If `clients/<client>/` doesn't exist yet, create it with `client_profile.md`, `current-projects.md`, and `goals.md` at the root (populated in Step 6) plus a `project-management/` subfolder. If the folder already exists (an existing client buying a new package, for example), just ensure `project-management/` exists.

## Step 3: Gather sales context

**Fathom MCP (preferred):** call `list_meetings` filtered to recent calls (e.g. `created_after` set to the last few days). If more than one meeting could be the sales call, ask the salesperson which one. Once identified, pull `get_meeting_summary` and `get_meeting_transcript` for the full call.

**Also ask the salesperson** to paste the GHL deal notes or forward the proposal — Fathom captures the conversation, not the commercial paperwork, and GHL isn't MCP-connected here.

**If Fathom is unavailable or can't find the call:** ask the salesperson to paste the call notes instead. Never skip this silently — sales context that doesn't make it into the handover doc is gone for good.

## Step 4: Interview the salesperson

This is required, not optional — a handover doc without it is exactly the kind of gap that causes onboarding surprises. Ask a minimum of four questions, **one at a time, never batched:**

1. What promises or commitments were made on the call? (Exact wording matters here — capture the salesperson's actual phrasing, not your paraphrase, since "we'll look into it" and "we'll have it live by Friday" are very different commitments.)
2. Any client quirks or communication preferences? (Who to CC, preferred channel, tone they respond to, timezone/availability quirks.)
3. Any red flags or sensitivities to be aware of? (Prior agency burned them, price-sensitive, particular pet peeve, anything that needs careful handling.)
4. What has the client tried before, and why did it fail? (Prior agencies, in-house attempts, other tools — what didn't work and why, so delivery doesn't repeat it.)

Ask follow-ups where the answer is thin — this section feeds the handover doc's Institutional knowledge block directly and may not be left empty. Record the answers close to verbatim rather than summarising them away; the salesperson's actual words carry information a paraphrase loses.

## Step 5: Write the handover doc

Use `references/templates/handover-doc.md` as the structure. Save to `project-management/handover-YYYY-MM-DD.md`.

- **Purpose:** who's taking ownership of what (Kristalyn for onboarding Phases 2–4, Josephine for Phase 1 billing — see `references/team-roster.md`) and what the salesperson/Michael retains (strategy, final review, major decisions).
- **Package & Commercials:** the package, fee, and add-ons from Step 1, citing the canonical figure from `team-roster.md` and noting any discrepancy flagged there.
- **Per-project blocks:** one per active project/service the client bought. Current status, outstanding work (owner inline per bullet), primary contacts and comms rules, upcoming meetings, new owner's responsibilities, delegator's responsibilities. **Every block must include a Success outcome** — an explicit, concrete definition of done. The template marks this required; don't leave it as a placeholder.
- **Institutional knowledge:** the Step 4 interview answers, verbatim-ish. This section may not be empty.
- **Access & credentials:** by reference only — password manager entry names (e.g. "GoCardless — see 1Password: LHM Client Billing"), never actual secrets, tokens, or passwords in the doc itself.
- **First actions:** the first three concrete things the new owner should do, each with a date.

## Step 6: Seed client files

Enrich `client_profile.md` and `goals.md` at the client root with what Steps 3–5 surfaced: business details, contacts, package purchased, and any KPIs/budgets/targets mentioned on the sales call.

**Never overwrite existing content — only fill gaps.** Read each file first. If a field is already populated, leave it exactly as-is, even if something from the sales call seems to contradict it; flag the contradiction to the user instead of resolving it yourself. If either file doesn't exist yet, create it from scratch with what's known and leave anything not covered by the sales call blank rather than inventing it — client-onboarding's own intake will fill the rest.

## Step 7: Kick the machine

**BasicOps client card.** Use the same `*Client Flow` board (project ID `68655`) that `post-meeting-review` and the rest of the project hub use for client cards — this is the single BasicOps home for every client, and it's a BasicOps *task*, not a BasicOps project, despite the naming. Call `list_tasks_in_project` with `projectId: 68655` and `filter_title` set to the client's short/common name. For a brand-new client this should come back empty — create the card with `create_task`. If it already exists (an existing client buying a new package), reuse it rather than duplicating.

Post a handover summary as a discussion comment on the card via `create_message_in_task`: what was sold, the headline institutional-knowledge points from Step 4, and a link to the local `handover-YYYY-MM-DD.md` path.

**Phase 1 billing task.** Create the task from item 1 of `references/checklists/tier1-billing.md`: title `"[Client] – Payment & Billing Setup"`, assignee Josephine, due date = today + 5 days. Create it as a subtask of the client card (`parentTaskId` set to the card's id), matching the established client-card pattern. This checklist item verifies via `mcp:basicops` — tick it once `create_task` succeeds, per the guardrail below on checklist verification.

**Update `current-projects.md`** with an onboarding block, per `references/folder-convention.md`'s block format:

```markdown
## Onboarding — Status: active
- Phase: Phase 1 — Billing
- Owner: Josephine
- Next action: Gather billing details and set up GoCardless mandate (see checklists/tier1-billing.md)
- Detail: project-management/onboarding.md
- Updated: YYYY-MM-DD
```

`onboarding.md` itself doesn't exist yet at this point — `client-onboarding` creates it when it resumes at Phase 1. The pointer above is correct in advance.

If BasicOps MCP isn't connected or isn't authenticated, don't skip this step silently: print the client card title, the handover comment text, and the Phase 1 billing task (title, assignee, due date) as manual instructions, and tell the user BasicOps needs to be set up by hand.

## Step 8: Comms

**Internal notification email — draft only, never send.** Use the Gmail `create_draft` tool. To: Kristalyn and Josephine; Cc: Michael. Subject: `New client handover — <Client Name>`. Body: package sold, a link to the handover doc, the first actions from Step 5, and a link to the BasicOps card. Present the draft in chat for approval before calling `create_draft`.

**WhatsApp message — print, don't send.** WhatsApp isn't MCP-connected; per `team-roster.md`, skills print the text and a human sends it. Print a short message for the salesperson to send to the team themselves, e.g.: "Just closed [Client] — Tier 1 + [add-ons], $[fee]/month. Handover doc and BasicOps card are up, KP/Jo you're on it."

**Client expectation email — offer to draft, adapted to what was actually sold.** `references/templates/expectation-email.md` is written for a standard Tier 1 engagement; its own header says to read the handover doc first and rewrite the "what's included" list to match the package actually sold. Offer this to the user; if they want it, adapt the inclusion list and pricing line before drafting, and never send it — draft only.

## Step 9: Hand off

Close with exactly this: "Handover complete. Next: run `lhm-project-hub:client-onboarding` — it will resume at Phase 1."

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- Ask the interview questions one at a time; do not batch.
