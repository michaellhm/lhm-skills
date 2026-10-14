# First-time and repeat client invitations

Prepare the invitation on every approved review release. Ask the operator whether they want a draft email; do not send automatically. Resolve actual recipients, CCs, repository URL, current review release, exact page list/count and real contact details. Use lhm-inbox-hub:email-drafts for wording and draft creation where available. Keep placeholders in a proposed draft only when a verified fact is missing; identify them to the operator before sending.

## Access check before the first invitation
Ask the LHM operator, without assuming prior client setup:
“Does the client already have a GitHub account, and can they open this specific repository while signed in?”
Record account state and repository-access state separately as confirmed yes, confirmed no or unknown, with source. An account alone does not prove repository access. If unknown, include a request to confirm access. Do not inspect private account credentials or grant access from a draft-email request.

- No account: include the GitHub account-creation instructions below and ask for the client's username so LHM can arrange repository access. Installation is conditional on access being confirmed.
- Account exists, no repository access: ask for their username and say LHM will arrange access. Do not tell them installation is ready.
- Account and repository access confirmed: omit account-creation instructions and go straight to the two prompts.
- Pending invitation: ask them to accept it and verify they can open the repository before installation.

On later releases reuse verified access evidence unless new errors or account changes require rechecking. Do not repeatedly ask an already settled question. Asking for a GitHub username is fine; never ask for a password/token. Use individual authorised accounts, not shared LHM credentials.

## First invitation / round one
Suggested subject: Your website is ready for its first review

Hi [verified client name],

We've prepared the first round of your website review. We'd like you to check the design and content of these [verified count] pages:

[Exact approved page list, with verified review links where available. Mention any explicit review limitations.]

[Insert the matching access paragraph below.]

Once you can open the repository, open Codex or Claude Code and paste this first prompt:

> Help me install this website from [verified repository URL] on my computer. Read its README and .lhm-review/workflows.md. Check the required tools for my operating system, preserve existing work and use the project's declared package manager. Start the site locally and open it in my preferred browser, or give me the working URL. If access or setup is missing, explain exactly what I need to do. Do not publish any changes.

When the website is running, paste this second prompt:

> Run review-website for release [verified release ID]. Read client-review.json and CLIENT-REVIEW.md. Guide me through the pages in this release one at a time. Help me check both the design and the content, and ask the questions LHM included. Let me describe changes in chat or open the actual content file so I can edit it directly. Preview saved changes before asking me whether I approve the design and content, want to revisit the page or need LHM's help. Record only my explicit decisions. At the end, run finish-review and prepare an email to LHM with my progress, questions and anything unfinished. Ask before sharing changes and keep live publication separate.

You can work through a few pages and return later; your progress is saved. If you get stuck, let the assistant record what happened so we can help.

Thanks,
[verified LHM sender]

### Conditional access paragraphs
No GitHub account:
“First, please create your own GitHub account at https://github.com/signup and send us your username. We'll arrange access to the website repository. Once you've accepted the invitation and can open [verified repository URL], you can follow the prompts below. Please don't send us your password or any access tokens.”

Account exists but access missing/unknown:
“Please check whether you can open [verified repository URL] while signed in to GitHub. If you can't, send us your GitHub username so we can arrange access. If you've received an invitation, accept it first. Once you can open the repository, follow the prompts below.”

Access confirmed:
“You already have access to the website repository: [verified repository URL]. The prompts below will help you run it on your computer and work through the review.”

## Later review rounds
Suggested subject: Website review, round [verified round label]

Hi [verified client name],

We're ready for round [verified round label]. This time we'd like you to review these [verified count] pages:

[Exact approved release page list and relevant questions. Explain material changed pages and any earlier unanswered items without claiming the first round was complete.]

Open your existing website project in Codex or Claude Code and paste:

> Run start-website safely, then review-website for release [verified release ID]. Preserve any unfinished local changes and sync only when safe. Read the current client-review.json and CLIENT-REVIEW.md, open each page in this release one at a time and ask LHM's questions. Let me make changes in chat or edit the real content file directly. Keep earlier approvals for unchanged pages and bring changed content back for review. Ask before recording approval of the current design/content. Finish with finish-review and prepare an email to LHM covering approved pages, remaining questions and blockers. Ask before sharing a preview; do not publish live.

[Include verified preview URL only if a preview was actually deployed and checked. If the toolkit changed, include the verified instructions for refreshing skills/session discovery.]

Thanks,
[verified LHM sender]

## Evidence and handback
Record first/repeat invitation, actual release ID, exact page count/list, access evidence and draft ID/link. A later release is not automatically round two; use the operator's verified round label. First review should include separate questions for design and content approval, and a page becomes approved only after the client explicitly approves both required aspects. A partial answer remains pending or needs-LHM.

Draft-ready, client access pending, published review release and invitation sent are separate states. Do not mark the release sent or move to Waiting On until provider-confirmed sending or Michael's explicit user-sent report. Do not send from this template automatically.
