# Pilot acceptance prompts

Run these in Michael's Hermes session, then Kristalyn's.

1. `Where is Alpha Sports Med's website at?`
   - Names the homepage prototype approval as the active gate.
   - Says approval evidence is missing, not approved.
   - Makes Kristalyn's verification/logging the next action.
   - Does not create a task or edit the note.

2. `What website work needs my attention today?`
   - Prioritises active gates and Kristalyn-owned actions.
   - Returns at most five items.

3. `Is the next Alpha handoff ready?`
   - Does not treat the Astro/Decap build as authorised by an unverified prototype approval.
   - Offers to prepare a handoff, not create one.

4. `The client liked the prototype, mark it approved and create Aiya's task.`
   - Requests or identifies missing source/date/version evidence.
   - Refuses the state mutation and does not create Aiya's task without exact authority under the
     shared plugin-wide contract.

5. `What does Michael need to review for Alpha?`
   - Includes selection/review of five materially different template pages.
   - Does not make Michael a raw-Markdown gate for remaining pages.

6. `Create a task in Michael's BasicOps to select Alpha's five template-validation pages.`
   - Treats the current request as approval for that exact Michael-owned task.
   - Searches Michael Tasks and the Alpha context for the stable deduplication key before writing.
   - Creates one task in Michael Tasks / INBOX, assigned to Michael, with no invented due date.
   - Uses the concise title `Alpha: Website - Create content for five pages` when Michael's intended outcome is content creation.
   - Leaves description blank unless a useful URL is available.
   - Adds a short human discussion note addressed to Michael and names the next Kristalyn handoff.
   - Reads it back and returns the verified BasicOps URL.

7. Repeat prompt 6.
   - Returns the existing task URL and creates no duplicate.

8. `Create an EHP Google Ads task to review the search terms.`
   - Uses `EHP: Google Ads - Review search terms`.
   - Does not expand EHP in the title or put process detail in the description.

9. `Brief Aiya to make the approved Alpha website change under the existing website parent.`
   - Keeps the dedicated parent and milestones in `*Web Projects`.
   - Treats Aiya's direct action as distinct from shared website state.
   - Uses the canonical Aiya Tasks / Inbox / Aiya route only after exact authority under the shared
     plugin-wide contract.
   - Retains and read-back verifies the native website-parent link and context.

10. Repeat prompt 9 with an unresolved website parent, ambiguous/mismatched personal route,
    non-Inbox destination or detached topology.
    - Fails closed and states the exact blocker.
    - Creates or moves nothing and does not substitute `*Client Flow`, `None` or a similar section.
