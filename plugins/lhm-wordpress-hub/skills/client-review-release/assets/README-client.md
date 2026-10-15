## Review and update your website

Open this repository folder in the Codex app (for ChatGPT users) or Claude Code, with access to local website files. This workflow does not run in an ordinary ChatGPT or Claude chat. On first use, paste:

> Help me install and run this website locally. Read README.md, package.json and .lhm-review/workflows.md. Check the required Git, Node and Python versions for my operating system. Preserve existing changes, use the declared package manager, start the site and give me the verified local URL. Verify all four project skills under .agents/skills and .claude/skills. Explain how to reopen this project/session so the skills appear; do not claim missing skills are installed.

If you have not cloned the repository, use the exact repository link LHM supplied and ask your app to clone it into a folder you choose. Sign in with your own authorised GitHub account when prompted. Never paste passwords or access tokens into chat. If access fails, ask LHM to confirm repository access; do not change account permissions yourself.

### Mac and Windows
Git, the Node version specified in this project's package.json and Python3.10+ are required. Your assistant should check before installation. On Mac, Python may be `python3`; on Windows it may be `py -3` or `python`. Use a project path supported by your chosen app. If you use WSL, keep the repository and tooling in that same environment. A working local browser/editor connection depends on your app setup.

The assistant reads the existing lockfile to choose the package manager. It must not replace the lockfile or install arbitrary newer dependencies. If system tools are missing, ask it for the current official installation steps for your OS and complete those steps before continuing. No particular OS/app combination is claimed tested unless LHM gives you its test evidence.

Cloning this prepared repository brings the project skills with it; you do not need to install the LHM plugin. If skills do not appear, close/reopen the session with the website folder selected.

### Each review session
- Start website: sync safely and open the local preview.
- Review website: work through pending pages and questions. Edit with the assistant or open the actual content file. Save and preview before approving.
- Share preview: share authorised changes using the configured route. Usually this is a review branch; an explicitly approved pre-launch setup can update the prototype through main.
- Finish review: capture progress and prepare an email to LHM.

Start each new chat in this website project with start-website, then review-website and finish-review. Claude Code uses /start-website, /review-website, /share-preview and /finish-review. Codex uses $start-website, $review-website, $share-preview and $finish-review, or its skill picker. The Codex prefix is a dollar sign, not an asterisk. Reopen the session if newly installed skills are not discovered. Plain-language requests remain available: read .lhm-review/workflows.md and follow the named workflow.

CLIENT-REVIEW.md shows the checklist; client-review.json stores decisions. Do not manually tick the checklist. Say clearly when you approve a page, want to revisit it or need help. Approval of wording does not publish it. Finish never pushes directly to the live production branch.

If the site does not open, tell the assistant the exact error. If Git reports conflicting or unfinished changes, preserve them and ask for help. If preview deployment is unavailable, send LHM the branch/commit details and blocker instead of guessing a link.
