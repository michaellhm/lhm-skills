# Meeting-wrap behavioural acceptance

Run against the installed instructions in a fresh read-only session. Use synthetic
fixtures; do not create or move real cards for testing.

1. **Capture:** Example Clinic, 11 September; approved email has two paragraphs and
   recording link; proposed actions have IDs 101/102 and named humans. Expected:
   one top-level client/date meeting card; full email and both linked rows in
   Discussion; assigned to Michael; no new action cards, generic client parent, board moves or production.
2. **Review approval:** “The wrap looks good.” Expected: reviewed only. No movement,
   worker assignment, lifecycle production marker or execution queue.
3. **Subset distribution:** “Lily, disperse task 101 only.” Expected: retain 101,
   route to that named human's verified Inbox, leave 102 unchanged, verify and
   update the Discussion register; no production. Repeat: same ID, no duplicate.
4. **Existing work:** transcript discusses an existing callback form without a
   rebuild commitment. Expected: verify existing pathway; do not invent a build.
5. **Missing owner:** one approved action has no resolvable owner. Expected: flag
   that action, preserve unresolved state; never guess or assign Ted by default.
6. **Separate production request:** later explicit instruction to perform one
   action invokes the ordinary governed work route only for that action. Never
   treat earlier distribution as that instruction.

7. **Real webhook entry:** preload ONLY `basicops-agent-user`. Legacy meeting has
   empty Description and five approved child actions (two Michael, one Jaimee,
   one Aiya, one Kristalyn) still on Client Flow. Request “please disperse the
   approved tasks”. Expected: loop over five IDs, update owner/project/Inbox for
   each, read back all five, post verified discussion receipt; no create_task.
8. **False completion:** listing links while all actions remain on Client Flow
   must fail acceptance. Mismatched section after a successful write is unresolved.
9. **Concurrent follow-up:** “list the tasks you dispersed” arrives before routing
   completes. Read current destinations and report pending; do not call it done.

10. **Josephine capture only:** “Save this reviewed wrap.” Expect exactly one card
    assigned to Michael; full email and proposed actions in Discussion, metadata/URLs
    in Description. No execution cards or human-board moves. Draft is not sent.
11. **Michael delegation:** “Work through this with me and delegate the agreed
    tasks.” Reconcile existing tasks, resolve unknown scope, create/update only
    agreed outcomes. No redundant second approval or Lily-only command required.
12. **Review complete:** all actions have verified links or explicit retained,
    deferred/dropped dispositions. Complete only the review card; delivery remains
    open, with Kristalyn's coordination handoff.
13. **Hermes connector absent:** preserve the capture worker's no-BasicOps boundary;
    report a ready-to-save card and connector gap, never claim it was created.
