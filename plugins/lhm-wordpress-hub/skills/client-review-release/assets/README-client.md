## Review and update your website

Open this repository folder in Codex or Claude Code. On first use, paste:

> Help me install and run this website locally. Read README.md, package.json and .lhm-review/workflows.md. Check the required Git, Node and Python versions for my operating system. Preserve existing changes, use the declared package manager, start the site and give me the verified local URL. Then run review-website to show the pages LHM has asked me to check.

If you have not cloned the repository, use the exact repository link LHM supplied and ask your app to clone it into a folder you choose. Sign in with your own authorised GitHub account when prompted. Never paste passwords or access tokens into chat. If access fails, ask LHM to confirm repository access; do not change account permissions yourself.

### Mac and Windows
Git, the Node version specified in this project's package.json and Python3.10+ are required. Your assistant should check before installation. On Mac, Python may be `python3`; on Windows it may be `py -3` or `python`. Use a project path supported by your chosen app. If you use WSL, keep the repository and tooling in that same environment. A working local browser/editor connection depends on your app setup.

The assistant reads the existing lockfile to choose the package manager. It must not replace the lockfile or install arbitrary newer dependencies. If system tools are missing, ask it for the current official installation steps for your OS and complete those steps before continuing. No particular OS/app combination is claimed tested unless LHM gives you its test evidence.

### Each review session
- Start website: sync safely and open the local preview.
- Review website: work through pending pages and questions. Edit with the assistant or open the actual content file. Save and preview before approving.
- Share preview: save approved sharing changes to a review branch for LHM to see on Cloudflare.
- Finish review: capture progress and prepare an email to LHM.

ClaudeCode uses /start-website, /review-website, /share-preview and /finish-review. In Codex, choose the installed skill or ask by its name; use the app's supported skill invocation. Reopen the session if newly installed skills are not discovered. Plain-language requests remain available: read .lhm-review/workflows.md and follow the named workflow.

CLIENT-REVIEW.md shows the checklist; client-review.json stores decisions. Do not manually tick the checklist. Say clearly when you approve a page, want to revisit it or need help. Approval of wording does not publish it. Finish never pushes directly to the live production branch.

If the site does not open, tell the assistant the exact error. If Git reports conflicting or unfinished changes, preserve them and ask for help. If preview deployment is unavailable, send LHM the branch/commit details and blocker instead of guessing a link.
