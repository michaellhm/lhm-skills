# Client Folder Convention (Project Hub contract)

Every PM skill reads/writes client state using this structure:

    20 Clients/<Client>/
    ├── <Client>.md                  # canonical client overview
    ├── Current Projects.md          # at-a-glance index; EVERY PM skill updates it
    ├── Goals.md                     # goals and targets
    └── project-management/          # ALL process state lives here
        ├── Onboarding.md            # scope-aware onboarding state, evidence and detailed checklist
        ├── Handover YYYY-MM-DD.md   # sales-handover output
        ├── website.md               # website build PM state (wp-project-manager)
        ├── landing-pages.md         # LP campaign PM state (lp-project-manager)
        ├── gmb.md                   # GMB cycle PM state (gmb-project-manager)
        ├── seo.md / google-ads.md / blog.md   # created by kickoff skills
        └── meetings/                # meeting wraps + review reports (YYYY-MM-DD-<type>.md)

## Rules

1. `Current Projects.md` holds one block per active process:
   status, phase, owner, next action, and a link into `project-management/`.
   Read the index first; then open only the file your skill owns.
2. Per-process Obsidian files are canonical for detailed context, checklist state, evidence and decisions. BasicOps owns visible stage, assignment and due action. Google Drive owns assets, working files and deliverables.
3. Lazy legacy migration: if your skill's state file exists at a legacy
   location (e.g. `wordpress/project-management.md`,
   `landing-pages/landing-page-project-management.md`, a GMB cycle file),
   move it to the path above, leave a one-line pointer file at the old path
   ("Moved to ../project-management/<file> on YYYY-MM-DD"), and add/update
   the index block in `current-projects.md`. Never migrate files you don't own.
4. Never store credentials in any of these files — reference the password
   manager entry by name instead.

## Current Projects.md block format

    ## <Process name> — <Status: active | blocked | complete>
    - Phase: <phase name>
    - Overall owner: <process owner>
    - Immediate owner: <owner of next gate or action>
    - Next action: <one line>
    - Detail: project-management/<file>.md
    - Updated: YYYY-MM-DD
