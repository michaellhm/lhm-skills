---
name: client-onboarding
description: "Run the Tier 1 client onboarding pipeline — resumable and phase-aware. Use this when the user says 'client onboarding', 'onboard [client]', 'continue onboarding', 'where is onboarding up to', 'billing setup', 'platform access', 'tracking setup', or 'first 30 days'. Four phases: Payment & Billing (Josephine), Platform Access (KP), Tracking & Config (Michael/Jaimee), First 30 Days (KP). Reads project-management/onboarding.md and resumes at the live phase; drafts every email; verifies access via MCPs; ticks items only on confirmation."
---

# Client Onboarding

Run the Tier 1 onboarding pipeline for a newly-handed-over client through its four phases — Payment & Billing, Platform Access, Tracking & Config, First 30 Days — picking up wherever it was left off. This skill is resumable by design: run it once and it initialises state; run it again next week and it continues from the first unresolved item in the live phase. It never advances a phase, ticks a checklist item, or sends a client-facing email on its own say-so — every irreversible step waits on either a successful MCP verification or explicit human confirmation.

## Step 1: Load state

Read `current-projects.md` in the client folder first (per `references/folder-convention.md`) to locate the Onboarding block and confirm the client folder path. Then read `project-management/onboarding.md`.

**If `onboarding.md` doesn't exist yet**, initialise it with this exact skeleton:

```markdown
# Onboarding — <Client>
Started: YYYY-MM-DD · Package: <from handover doc>
## Phase status
- [ ] Phase 1 — Payment & Billing (Josephine)
- [ ] Phase 2 — Platform Access (KP)
- [ ] Phase 3 — Tracking & Config (Michael/Jaimee)
- [ ] Phase 4 — First 30 Days (KP)
## Phase 1 checklist
<copied from references/checklists/tier1-billing.md>
## Phase 2 checklist
<copied from references/checklists/platform-access.md>
## Phase 3 checklist
<copied from references/checklists/tracking-setup.md>
## Phase 4 checklist
<copied from references/checklists/first-30-days.md>
## Tracking notes
## Log
- YYYY-MM-DD: <event>
```

Fill `<Client>` and `Started` (today's date) from `current-projects.md` / the handover doc; fill `Package` from the handover doc's Package & Commercials section (falling back to `client_profile.md` if no handover doc exists). Under each `## Phase N checklist` heading, copy the entire checklist body from the corresponding `references/checklists/*.md` file verbatim — item text, owner, and verify annotations, unmodified — as it reads right now. This copy is a **snapshot**, not a live reference; see the Rules section for what that means going forward.

If `current-projects.md` has no Onboarding block yet (this skill run standalone rather than via `sales-handover`), create one now using the block format in `references/folder-convention.md`, with Phase 1 as the starting phase and Josephine as owner.

## Step 2: Resume at the first phase with unticked items

The `## Phase status` boxes are the **authoritative** resume signal, not the individual checklist items — Step 4 keeps them in sync at every gate, so they're the only thing that needs scanning across phases. Scan them top to bottom (Phase 1 → 4); the **live phase** is the first one whose status box is still unchecked. A phase whose status box is already ticked is closed for good — never re-scan its checklist for lingering unticked items, even conditional ones nobody explicitly resolved (Step 3's N/A handling below exists precisely so this doesn't recur going forward).

Within the live phase only, scan its checklist top to bottom for the first item that isn't yet **resolved** — resolved meaning ticked `[x]` or marked `[x] N/A — <reason>` per Step 3. If every item in the live phase is already resolved but its status box isn't ticked yet, don't re-present a finished checklist — go straight to Step 4 and run that phase's gate.

Announce: the client, the live phase and its name, its owner, and the first unresolved item in it, e.g. "Onboarding — Acme Health. Phase 2 — Platform Access (Owner: KP). Next: Send Welcome & Access Request email."

If the person you're talking to isn't that phase's owner, say so plainly ("This phase belongs to KP") and offer to prepare the owner's materials anyway — draft the email, compose the BasicOps task, print the WhatsApp text — so the actual owner has everything ready to confirm rather than waiting on you to be re-run by the right person. Preparation is never owner-gated; only ticking a `human-confirm` item is.

## Step 3: Work items in order

Work the live phase's checklist items top to bottom. Some items are conditional on something that may not apply to this client — the tier1-billing "If details missing" item when details arrived complete, the platform-access "Wrong permission level anywhere" item when nothing came back wrong, the GSC item when GSC isn't in scope, the tracking-setup booking-platform item when the client has no booking platform. Never leave a conditional item silently blank or blocking — resolve it explicitly: confirm with the human that the condition genuinely doesn't apply (that confirmation is what satisfies the tick-only-on-confirmation guardrail for an N/A — never mark an item N/A without asking, that's just a different flavour of ticking without confirmation), then mark it `- [x] N/A — <one-line reason>` and log it in `## Log` exactly like a real tick. This is what lets a phase actually reach "everything resolved" instead of sitting on a permanently-unticked conditional item forever.

For every item whose condition does apply, branch on its `verify:` field:

**`verify: mcp:<tool>`** — Attempt the verification now, using the tool named in the item (e.g. `mcp:analytics-mcp (get_account_summaries shows the property)`, `mcp:GoogleAds (list_accessible_accounts)`). On success, tick the item immediately and log the result. On failure — the check comes back negative, or the MCP isn't connected/authenticated — do **not** tick it. Explain what the check would have confirmed, and either wait for the underlying condition to become true (e.g. access hasn't arrived yet — nothing to do but wait and re-check) or fall back to asking the human to confirm manually, exactly as the guardrails require. Never tick on a failed or skipped verification.

**`verify: human-confirm`** — Do the preparable part first, then ask:
- **Email items** — draft from `references/templates/welcome-access-email.md` (Phase 2) or `references/templates/billing-emails.md` (Phase 1), filling the template parameters from what's known; present the draft, never send it.
- **BasicOps items** — compose the task or subtask via the BasicOps MCP now (see Step 4/5 for the exact card pattern); this is preparation, not the human-confirm itself, unless the checklist item's own `verify:` field says `mcp:basicops`.
- **WhatsApp items** — print the message text for a human to send; WhatsApp isn't MCP-connected here, per `references/team-roster.md`.
- Then ask explicitly: "Ready to tick '<item text>'? Confirm once it's actually done." Tick only on an unambiguous yes — never infer confirmation from the human moving on to the next topic.

Append every tick — mcp-verified or human-confirmed — to `## Log` with the date and how it was verified: `- YYYY-MM-DD: <item text> — verified via <mcp:tool result | human-confirm>.`

## Step 4: Phase gates

A phase only advances when its specific gate condition is met — not simply "every item ticked," since some items are conditional or don't block progress. "Ticked" below includes items resolved as `[x] N/A — <reason>` per Step 3; a resolved N/A counts the same as a real tick for gate purposes. Gate conditions, explicitly:

- **Phase 1 → 2** — the billing handoff item (tier1-billing.md's last item: "Move GHL deal to 'Billing Complete – Ready for Platform Access Setup'; notify Michael + KP") is ticked. This item itself only ticks once the payment has cleared and Xero is set up, so it naturally waits on everything upstream of it.
- **Phase 2 → 3** — all four access-verification items are resolved: GA4 Admin, Google Ads MCC, GSC (ticked if verified, or resolved N/A if out of scope for this client), and GTM/GBP/CMS admin. The permission-bump item only matters if one of those four came back wrong; when it doesn't apply, resolve it N/A per Step 3 rather than leaving it hanging. The closing BasicOps note ("All required access received and verified") is the record of the gate firing, not a precondition for it — write it as part of executing the gate.
- **Phase 3 → 4** — specifically the GA4-collecting item (realtime hit confirmed) and the Ads-conversions item (GA4 conversions imported into Google Ads, conversion actions active) are ticked. These two are the hard gate per the brief. The remaining Phase 3 items — GTM audit, form/enquiry conversion events, phone-call tracking, GA4↔Ads account link, Clarity install, booking-platform goals — should still be worked through Step 3's ordering (resolving any that are conditional to N/A rather than leaving them open) and are expected to be done, but do **not** themselves block the Phase 3 → 4 transition. If any remain genuinely unresolved when this gate fires, flag them explicitly in the gate announcement and in `## Tracking notes` so they don't quietly fall off the list — don't just leave the gap unmentioned.

Since the live-phase scan in Step 2 never looks inside an already-gated phase again, resolving every item (tick or N/A) before or immediately after a gate fires is what keeps the state file clean — don't leave a phase behind with open conditional items just because the gate didn't strictly require them.

On each gate firing:
1. Tick the corresponding `## Phase status` box for the phase that just completed — this is the resume signal Step 2 relies on, so it must happen every time, without exception.
2. Update the `current-projects.md` Onboarding block: `Phase` to the new live phase's name, `Owner` to its owner, `Next action` to that phase's first item, `Updated` to today.
3. Post a BasicOps status note on the client card (`create_message_in_task` on the *Client Flow card, project ID `68655` — the same card `sales-handover` and `post-meeting-review` use; find it with `list_tasks_in_project`, `filter_title` set to the client's short name if you don't already have its id from this session): "Onboarding: Phase N complete → Phase N+1 (Owner: <next owner>)."
4. Announce the transition to the user and immediately continue into the new live phase per Step 2/3 rather than stopping.

## Step 5: Phase 4 extras

Phase 4 carries more setup than the others:

- **30-day plan.** This item's `verify:` field is `mcp:basicops`, not human-confirm — the one unambiguous tick rule is: it ticks the moment `create_task` succeeds for "[Client] – 30-Day Project Plan" (`parentTaskId` set to the client card so it lives as a subtask, matching the `sales-handover` pattern, due `today + 30`), with the remaining first-30-days.md items created as its subtasks — computed due dates where the checklist specifies them (Local SEO/Maps subtask to Jaimee due `today + 10`; mid-point check-in around `today + 14` to `today + 16`; close-out at `today + 30`). The checklist item's own text also says "confirm plan with Michael before kickoff" — that's an action to perform, not the tick condition: print the plan summary as a WhatsApp/BasicOps message for Michael per the usual pattern, but the item is already ticked by the successful MCP creation regardless of whether Michael has replied yet.
- **Cadence enforcement.** Apply `references/cadences.md` for the rest of the phase: chase outstanding client approvals (ad copy, LP copy, designs) every 48 hours; send a client progress update every 7 days; hold the Day 14–16 mid-point check-in (internal + client); run the Day 30 close-out.
- **Delegate, don't do.** Route Google Ads campaign build work to `lhm-project-hub:google-ads-kickoff` — that skill is created in a later rollout task, so if it isn't available yet in this environment, say so and offer to prepare the campaign brief by hand in the meantime rather than blocking. Route each weekly client update to `lhm-project-hub:client-update-email`.

## Step 6: Completion

Once all four `## Phase status` boxes are ticked: mark the `current-projects.md` Onboarding block `Status: complete`, set `Next action` to "Moved to ongoing rhythm — monthly-review", and log the close-out event in `## Log` with today's date. Tell the user onboarding is complete and that the client now moves to the ongoing monthly rhythm (`monthly-review`, per `references/cadences.md`).

## Rules

- Client-facing emails are drafts only, never sent.
- Checklist items tick only on explicit human confirmation or successful MCP verification.
- Missing or unauthenticated MCP → print manual instructions, never silently skip.
- Credentials by reference only (password manager pointer), never plaintext.
- No fabricated metrics or client data.
- The checklists embedded in `onboarding.md` are snapshots; if `references/checklists/` files have changed since initialisation, flag the diff rather than silently mixing versions.
