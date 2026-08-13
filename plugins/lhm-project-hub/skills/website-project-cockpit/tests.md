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
   - Refuses the state mutation and does not create Aiya's task without Aiya's explicit pilot approval.

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
