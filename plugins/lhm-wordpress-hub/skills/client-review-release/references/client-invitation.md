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

## First-time onboarding: three emails

Default to separate drafts, preserving actual recipients/CCs. Access email can be sent first; hold installation until account and specific repository access are confirmed, and hold the batch email until setup is working. Never send automatically. Explain local preview versus sharing accurately; actual page sources may be JSON/Astro rather than Markdown. The following wording is reusable; replace verified placeholders, not by copying client-specific correspondence into the skill.

### Email 1: GitHub access
Subject: [Client] website | First step: GitHub access

Hi [verified greeting],

We're getting ready for you to give us feedback on the website. As discussed, we're setting this up so you can review and edit it using your preferred AI tool: ChatGPT through Codex, or Claude through Claude Code.

It will open a local version of the website, basically a test site running on your computer. You can chat to the assistant and say “this paragraph doesn't sound like us” or “could you change this service description?” It can make the change and show you how it looks on the page as you work. Nothing goes live at this stage.

You can also ask it to open the page's content file and edit a few words yourself, a little like editing a Word document.

Changes appear on your computer first. When you're ready to share them, the assistant saves them to GitHub so we can see your edits and check the updated preview. Explain the verified publishing route: review branch by default; explicitly approved pre-launch main may deploy the prototype automatically. Never promise automatic deployment without evidence. Draft changes can remain unshared; live publication follows the configured approval process.

To give you access to the website files, you'll each need a free GitHub account. Think of it as a shared Google Drive for the website, with a history of changes. The private website folder is called a repository.

Could you please create an account at https://github.com/signup if you don't already have one, and send through your username so we can arrange access? Once you've accepted the invitation and confirmed the repository opens, I'll send instructions for running the website with your AI assistant and the review features we've built in.

Thanks,
[verified sender]

### Email 2: install and use the review tools
Subject: [Client] website | Installing the website and using the review tools

Use Codex (for ChatGPT users) or Claude Code with the website folder open. Emphasise that an ordinary chat cannot run this local workflow. These apps can work with the files on the client's computer.

**First step: paste this prompt**

> Help me install this website from [verified repository URL] on my computer. Read README.md and .lhm-review/workflows.md. Check required tools for my operating system and guide me through anything missing. Preserve existing work and use the declared package manager. Verify all four project skills under .agents/skills and .claude/skills, start the local website and give me the working browser link. Explain how to reopen the website project/session so the skills appear. Do not publish changes.

Explain that cloning brings the committed skills; the prompt verifies them, it does not guarantee discovery or install missing plugin files. Reopen the website project/session after setup if needed.

**Using the review tools**

Skills are saved instructions the assistant can follow. Claude Code uses `/start-website`; Codex uses `$start-website` or the skill picker. Use a forward slash, not backslash; dollar sign, not star. At each new chat in the website project: start-website safely syncs files and opens the local site; review-website guides the current batch/questions one page at a time; finish-review records explicit decisions and drafts a handback. Share-preview saves authorised changes through the configured route. Finish can offer that sharing step but must not claim automatic pushing. For an approved pre-launch-main setup, explain that sharing updates the prototype through the named branch; after launch keep live publication separate.

Ask the client to confirm setup works before sending the batch email. Do not repeat the full page list here.

### Email 3: the approved review batch
Subject: [Client] website | [Verified round and page count] to review

Hi [verified greeting],

We've put together [verified count] pages for you to review under [verified batch/menu label]:

[Exact approved page list.]

**First step: open your website project in Codex or Claude Code, start a new chat and paste this prompt**

Use the following prompt with the exact release ID and configured sharing route:

> Run start-website safely, then review-website for release [verified release ID]. Read client-review.json, CLIENT-REVIEW.md and .lhm-review/workflows.md. Guide me through the pages and included questions one at a time. Let me give feedback in chat or edit the actual content file. Preview changes and ask for explicit design/content approval. At the end, run finish-review and prepare an email to [verified LHM contact] with progress, questions and unfinished work. Ask before sharing through the configured route and keep live publication separate.

The assistant will open each page and guide you through the review. Please check:
- **Design:** the layout, images and how the page looks.
- **Content:** whether the wording sounds like your clinic and accurately describes services, practitioners, clinic availability and FAQs.

[Include the actual page-specific questions, explicit exclusions and unresolved coverage. Mention unbuilt menu destinations only where verified.]

No need to write polished copy. Tell the assistant what feels wrong or what you'd like changed, and it can help you work through it. You can review a few pages and return later, with your progress saved.

Thanks,
[verified sender]

Edits and answers alone do not approve a page. Keep all three draft IDs, access/setup evidence and actual sent state distinct. If the operator reports sending the access email, preserve it as sent; do not recreate it as a new draft unless explicitly requested. Save the remaining approved emails as drafts and respect the access/setup gates.

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
