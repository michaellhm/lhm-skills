# Project health and specific weekly actions

The snapshot answers how each substantial web project is going. Owner lists answer exactly what each person needs to do this week. These are different views: a one-off website fix belongs in an owner list when actionable, without becoming another project row.

## Inbox research

Resolve each person's current personal board and Inbox section from BasicOps. Michael, Kristalyn and Aiya are required; include Jaimee only when a current unmet website action actually exists. Sweep all pages of the Inbox section. If the tool cannot filter a section, page through the board and retain just Inbox candidates; never silently stop at a fixed cap. Use server-side title/status filters only if they still cover all website candidates, and reconcile other active sections/linked tasks where current work has moved out of Inbox. Board owner is not necessarily task assignee.

Read current candidate task discussions and relevant replies. Record task ID, native URL, assignee, status, last substantive activity, actual due date, dependency, proposed week action and selection/exclusion reason. Retain coverage counts and final cursors. Exclude completed/cancelled/duplicate work, future gated work and unrelated Ads/SEO/admin from this website email. A future milestone doesn't justify assigning its execution now.

Select work due this week, explicit week commitments, ready next steps and urgent follow-ups. Include meetings and their follow-on preparation/output separately when both apply. No invented due dates or made-up workload capacity. If no date is agreed, say what needs scheduling. If a genuine commitment has no matching task, flag “Task to add/confirm” with its evidence; do not claim it exists or create it during reporting.

Each owner bullet should be concrete, for example:
- Michael — Any Stage Pilates: attend the 23 September, 8:30 am strategy call; confirm booking setup and launch scope. After the call, prepare the playbook/sitemap and page plan for Kristalyn.
- Michael — Your Story Physio: review the sitemap and copy during 21–25 September while Aiya prepares the first designs.
- Aiya — Alpha: report which service pages are finished, what is blocking the remainder and the next preview date.

Use the actual current records to decide the final list. Do not permanently embed those example dates/actions as recurring truth. Include a verified native task URL with each action (use the renderer’s {client, text, url} action object for readable linked text); avoid a generic “do the reviews above”. Link a meeting/project record if the action lacks an execution card; explicitly record that gap in inbox-review.json rather than repeating the administrative caveat in the email.

## Health / inactivity

Meaningful BasicOps activity is an actual delivery update, specific discussion/reply, returned artifact, completion or stage transition. Metadata-only touches, repeated sweep comments and this brief do not reset the clock. Compute age in calendar days at the Melbourne cutoff. Seven or more days without substantive recorded progress is orange when work should be moving; fourteen days merits a prominent progress investigation. Absence of an update does not prove nobody worked. Red requires an actual blocker, stalled delivery or unmet commitment, or an explicit current human red classification.

A future agreed start or meeting can be green until work is expected; ordinary planned reviews and missing final dates need not turn green projects orange. Keep due-date uncertainty visible. If newer email evidence proves progress while BasicOps is stale, say so and assign the board update rather than alleging inactivity.

Save inbox-review.json with each board/section ID, retrieval time, pagination/terminal status, selected action records and excluded candidates/reasons. Add it to the research evidence manifest. Add the project activity fields and dated human colour overrides to research-receipt.json. The controller checks that the final owner lists include all selected work and that each project row is a real project, not an isolated fix.

Presentation: group all selected actions for the same client together within each owner’s section, including distinct website/landing-page scopes. Show one client name followed by short linked actions. Keep the detailed evidence, task status and missing-card flag in inbox-review.json; avoid overwhelming the email with repeated background and administrative caveats.
