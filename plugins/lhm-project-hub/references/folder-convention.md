# Client Folder Convention (Project Hub contract)

Every PM skill reads/writes client state using this structure:

    clients/<client>/
    ├── client_profile.md            # root — who the client is (existing convention)
    ├── current-projects.md          # root — at-a-glance index; EVERY PM skill updates it
    ├── goals.md                     # root — goals & targets (existing convention)
    └── project-management/          # ALL process state lives here
        ├── onboarding.md            # Tier 1 pipeline state (phase, ticks, owners, dates)
        ├── handover-YYYY-MM-DD.md   # sales-handover output
        ├── website.md               # website build PM state (wp-project-manager)
        ├── landing-pages.md         # LP campaign PM state (lp-project-manager)
        ├── gmb.md                   # GMB cycle PM state (gmb-project-manager)
        ├── seo.md / google-ads.md / blog.md   # created by kickoff skills
        └── meetings/                # meeting wraps + review reports (YYYY-MM-DD-<type>.md)

## Rules

1. `current-projects.md` holds one block per active process:
   status, phase, owner, next action, and a link into `project-management/`.
   Read the index first; then open only the file your skill owns.
2. Per-process files are the source of truth for CONTEXT.
   BasicOps is the source of truth for WHO does WHAT by WHEN.
3. Lazy legacy migration: if your skill's state file exists at a legacy
   location (e.g. `wordpress/project-management.md`,
   `landing-pages/landing-page-project-management.md`, a GMB cycle file),
   move it to the path above, leave a one-line pointer file at the old path
   ("Moved to ../project-management/<file> on YYYY-MM-DD"), and add/update
   the index block in `current-projects.md`. Never migrate files you don't own.
4. Never store credentials in any of these files — reference the password
   manager entry by name instead.

## current-projects.md block format

    ## <Process name> — <Status: active | blocked | complete>
    - Phase: <phase name>
    - Owner: <team member>
    - Next action: <one line>
    - Detail: project-management/<file>.md
    - Updated: YYYY-MM-DD
