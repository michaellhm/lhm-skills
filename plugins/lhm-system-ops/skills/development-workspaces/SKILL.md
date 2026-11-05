---
name: development-workspaces
description: Govern persistent Hermes development storage and website Git workspaces shared by Codex and Claude. Use for "set up the repo on Hermes", "move development workspaces", "work on this website", "where does the checkout live", or a missing repository, disk or workspace preflight. Preserve active tasks, provider sessions and existing approvals.
---

# Development Workspaces

Use the Hermes host as the persistent development machine. OpenAI and Anthropic run
the models; the installed host workers use local files. Separate hosted Codex or
Claude products do not automatically see the host filesystem.

## Storage standard

Read the root-owned `/etc/lhm-development-storage.json` and the shared
`30 Projects/TED Client Workspaces.md` location index. Never guess a volume ID,
repository, client, provider or folder from a display name.

- The additional development volume holds client/provider workspaces, website Git
  repositories, task worktrees, dependency directories, build outputs and drafts.
- Keep stable registered paths such as `/var/lib/lhm-client-workspaces`,
  `/var/lib/lhm-sites` and existing pilot paths. Host-managed bind mounts may place
  their data on the volume without changing registrations or saved task context.
- The main disk retains Linux, installed executables, credentials, provider login
  settings, saved conversation databases and Hermes operational state. Do not move
  whole worker homes, `.ssh`, authentication files or production state as incidental
  workspace cleanup. Repository-local `.codex`/`.agents` anchors are workspace files,
  not authority to copy a provider's credential home.
- Confirm the recorded volume is mounted and each ordinary development root is on
  that device before creating a checkout or writing build data. A directory existing
  at the expected mount path is insufficient. Missing storage blocks new admission;
  never silently create a replacement on the main disk.
- Preserve existing Unix ownership, ACLs, per-worker isolation and GitHub scopes.
  A common storage device does not grant either provider access to every client.

The registration records physical targets, stable aliases, expected device and
temporary active-workspace pins. Report an active pin as **pending physical
relocation**, not as fully migrated. See [the host contract](references/host-contract.md).

## Website repository intake

1. Read the canonical client and website project, existing task Discussion, workspace
   registration and current router status. Reuse the original task and conversation.
2. Verify the exact GitHub repository, remote, default branch, deployment mapping,
   applicable authority and current owner. Existing `.git` anchor directories in
   task-context folders are not proof of a real checkout.
3. Reuse a registered local clone. Clone a missing repository only through the
   authorised host route and its existing repository-scoped credential mechanism.
   Do not bulk-clone all clients or expand App installation access automatically.
4. Standardise new repository work on a task branch and isolated Git worktree under
   the registered development volume. Preserve dirty files and unpublished commits.
   Never reset, clean, stash or switch an active worker's checkout to admit another.
5. Check what the installed host supervisor actually supports. If it only supports
   one checkout per site, retain its repository-wide lease and serialize writers;
   report task-worktree support as a capability gap rather than inventing support
   or creating an unmanaged parallel writer. A worktree never bypasses the lease.
6. For a Codex/Claude handoff, preserve repository, task branch, commits, drafts,
   prior provider session and run identity. Inspect the existing lease and worker
   status first. Do not steal locks, restart live sessions or submit the same
   instruction as a new job merely because a path or provider changes.
7. Run repository-controlled Git commands, hooks, package scripts and tests as the
   assigned worker, never root. Keep credentials out of remotes, files and logs.

Workspace setup authorises no merge, main push, deployment, client send or extra
spend. Honour any separately verified, task-specific publication authority; otherwise
return the branch, checks and review handoff. Local files are working copies; publish
deliverables through the established verified Drive/GitHub route.

## Move existing work without interrupting it

Inventory active workers, cwd directories, open handles, locks and task/session
receipts before copying. Save identities and hashes. Do not assume an `interactive`
session is safe to stop or that copying a live cwd changes its open file handles.

Move idle roots with a verified copy and stable aliases. For an active workspace,
retain the original directory inode and attach it through a recorded temporary
bind mount while moving other roots. Verify relative and absolute paths still reach
the same files. Do not replace that workspace with a copied inode, freeze/kill the
worker, change its conversation or replay its instruction to complete a disk move.

Keep the active pin until that worker and every other writer/open cwd have released
the directory. At a separately verified idle maintenance point, copy and verify the
remaining files, remove the pin, and verify the ordinary volume-backed path. Never
claim full migration while pins remain. If an inode-preserving pin cannot be proved,
leave the active workspace untouched and report the bounded exception.

## Handback

Report the verified volume/device, stable and physical paths, actual repository and
branch/worktree, current task/run/session, lease owner, storage/readback evidence,
active pins still pending, rollback location and next handoff. Skill publication,
merge, installation, workspace migration and website deployment are separate states.
