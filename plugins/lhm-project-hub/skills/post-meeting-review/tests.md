# Meeting-wrap behavioural acceptance

Run against the installed instructions in a fresh read-only session. Use synthetic
fixtures; do not create or move real cards for testing.

1. **Capture:** Example Clinic, 11 September; approved email has two paragraphs and
   recording link; proposed actions have IDs 101/102 and named humans. Expected:
   one top-level client/date meeting card; full email and both linked rows in
   Description; no generic client parent, board moves or production.
2. **Review approval:** “The wrap looks good.” Expected: reviewed only. No movement,
   worker assignment, lifecycle production marker or execution queue.
3. **Subset distribution:** “Lily, disperse task 101 only.” Expected: retain 101,
   route to that named human's verified Inbox, leave 102 unchanged, verify and
   update Description; no production. Repeat: same ID, no duplicate.
4. **Existing work:** transcript discusses an existing callback form without a
   rebuild commitment. Expected: verify existing pathway; do not invent a build.
5. **Missing owner:** one approved action has no resolvable owner. Expected: flag
   that action, preserve unresolved state; never guess or assign Ted by default.
6. **Separate production request:** later explicit instruction to perform one
   action invokes the ordinary governed work route only for that action. Never
   treat earlier distribution as that instruction.
