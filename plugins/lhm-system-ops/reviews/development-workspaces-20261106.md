# Development workspace storage standard

## Source and scope

Base: `78c0a7c5` on `cto/hermes-site-workspaces-20261026`, the canonical source
recorded for the installed website workflow. This is a stacked update, not an
attempt to merge the existing website feature into main. The unrelated canonical
desktop checkout is unchanged.

Add `development-workspaces` and link it from the website, task preflight, Lily
planning and marketing catalog entry points. Development data belongs on the
registered additional volume; installed tools, credentials and supervisor/session
state stay on the main disk. Preserve client permissions, repository leases,
request IDs, dirty work and existing provider conversations.

Task branches and isolated worktrees are the standard for new supported repository
routes. The current one-checkout website supervisor remains serialized; this change
does not pretend it has acquired parallel worktree support or publication authority.

Versions: System Ops `0.9.125`, Project Hub `0.1.137`, Marketing Hub `2.2.74`.
The source tree has 202 skills, including 14 System Ops skills. Update the existing
validator's stale baseline manifest/skill expectations to those verified counts.

## Validation and security

- 57 existing task-router/client/workspace/delivery tests pass.
- 14 existing website workspace tests pass.
- Three rehearsal boundary tests reject non-admin, unmounted and main-filesystem
  destinations without changing anything.
- Live disposable Linux rehearsal passes with the same process, held file,
  relative path, absolute alias and directory inode; generated mounts are removed.
- Plugin versions, duplicated-script parity, System Ops skill set, affected skill
  frontmatter and Git whitespace checks pass.
- Reviewed accumulated learning files. The five prospect-sitemap entries are
  unrelated to this task and left unchanged, as are unrelated local edits.
- No credentials, client data or live host registrations enter the source branch.

## Operational application and limits

The operator prepared private copies of inactive workspace data on the development
volume, excluding the two folders held by existing Claude processes. The broad
multi-root live cutover was rejected by automatic approval review because of
disruption and rollback risk around active processes, mounts and namespaces.

Only the separately verified idle Codex-provider root was cut over: no open cwd/file
users, verified copied contents and no Claude write permission on its files. Its
stable alias and startup mount dependency are recorded in root-owned host
configuration. Claude roots, registered website source and legacy Codex pilot roots
remain at their original locations, with inactive data staged privately. The
current production task, provider session, namespace and instruction are unchanged.

Do not report a full migration. Complete the remaining cutover only at a verified
idle maintenance point or after approval of a narrower proven plan. Do not install
a task-completion poller, stop a worker or replay production as a disk-move shortcut.

## Release and rollback handoff

Feature-branch publication is not merge or installation. Review only this delta
against the existing website feature branch. Deployment still needs approval of
the exact immutable commit and intended profiles. The consumers are the website
workflow, Brain, Chief of Staff and Project Manager.

Use a selective, backed-up skill deployment. Do not run the broad task-router
installer as incidental documentation rollout: compare live drift first and do
not overwrite independent operational repairs, credentials, provider settings,
registered clients, active sessions or queue state. Verify installed hashes and
skill discovery without restarting the active worker.

Retain the recorded fstab backup, original files behind the idle alias and private
staging receipt. Reversing that alias requires a fresh idle/open-handle check.
Full-volume, Docker and workspace rollback records are distinct. Restore only the
changed mount or skill files; never resubmit the original task to recover storage.
