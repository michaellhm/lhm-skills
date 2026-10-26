---
name: hermes-site-workspace
description: Set up or resume a website repository on Hermes for Claude or Codex, using one checkout per site, a repository-wide lock and GitHub App authentication. Use for “work on this website on the VPS”, “clone this site for Claude”, “set up the repo on Hermes”, or a website task blocked by missing source/GitHub access.
---
# Hermes Website Workspace

Turn an authorised website task into work in its real Git checkout. Use the existing task router and host-managed `site_workspace.py`; do not create a second client task or hand the user another operator pack.

## Resolve and register the site

Read the shared client overview, current website project and task discussion. Verify the exact GitHub repository, default branch and where it deploys. Keep the existing client knowledge, Drive deliverables, task context and website source distinct. If the repository is missing locally, the host clones the verified repository into `/var/lib/lhm-sites/<site-id>/repo`.

Use the host-owned `/etc/lhm-sites/config.json` registration. It records client ID, repository, explicit `build` or `live` mode, verified deployment mapping, human authority, check commands and commit identity. Never infer build mode from a task name, staging hostname alone or an old note. Register new repositories only under the user's existing authority and GitHub App installation scope; missing App access is a concrete blocker, not permission to use another identity. The host owns registration and App credentials; the provider cannot edit them.

## Admit one worker

Use the ordinary `task_route_preview` / `task_route_submit` / `task_route_status` route on the existing BasicOps task. Registered website tasks automatically enter the host site supervisor. It claims an OS lock keyed by the canonical repository across Claude, Codex and client aliases. Busy means wait/return the current owner and existing chat; never start a second writer, delete a lock file, or use an advisory ignore file.

One site has one source folder. Each task still has its own context/drafts and original conversation. On provider handoff, stop and verify the previous worker, snapshot its files, preserve unfinished changes and resume the existing conversation where supported. Never overwrite, reset, clean or stash work to make admission pass. Dirty work or unpublished commits must be reconciled with the existing task before another task starts.

The host fetches and fast-forwards clean source before work. It supplies the actual repository as working directory plus preserved task context, build tools and explicit publishing mode. A context-only folder or empty `.git` anchor is not a checked-out website. Verify repository HEAD, package scripts and remote before reporting ready.

## Work, check and publish

Claude/Codex edits and runs project checks as its worker account. Read existing drafts as implementation guidance, compare them to source and preserve useful edits. Keep credentials out of conversations, Git, logs and deliverables. The host mints short-lived GitHub App tokens scoped to the one repository; never copy a human Git credential or App private key into a worker home.

- **Build mode:** tested scoped changes may be committed and pushed to `main` under the recorded authority. This is authorised only where main's deployment mapping has been verified as the in-build site.
- **Live mode:** work on `task/<request-id>`, push that branch, and return a preview/review handback. Merge/main publication needs the user's applicable approval.

Commit under the registered automation identity, recording the task ID and provider in the message. Before publication, run the registered checks as the worker, retain logs and bind the successful checks to the exact commit. The host `site_workspace.py publish <request-id> --site <site-id>` rechecks mode, branch, clean tree and remote ancestry, refuses remote drift/force push, and verifies the remote SHA. A pushed commit and a successful hosted deployment are separate outcomes. Return both when verified; never claim client launch from a preview push.

If the worker is still running, do not steal its lock to publish. Reconcile its completion and stop it cleanly, then publish through the host. Keep the existing BasicOps owner/status unless the authorised handoff changes it. Route task writes through `basicops-task-manager`.

## Evidence and recovery

Report repository/folder, task and provider, real session link, lock state, publishing mode, commit/branch, checks, deployed preview if verified, and exact blockers. Update the existing client website note with evidenced operational changes. Do not put credentials or private founder context in shared notes.

For host installation/configuration and recovery, read [host contract](../../assets/task-router/SITE-WORKSPACES.md). After the session finishes, run the installed `lhm-learn:learn` or return a concise learning handback. Do not publish skill changes or mark website work complete merely because its session started.
