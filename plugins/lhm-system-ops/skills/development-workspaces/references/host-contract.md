# Development storage host contract

This contract is configuration-driven. Keep machine IDs, client registrations,
credentials and live task state out of the plugin source.

## Registration and startup

The root-owned `/etc/lhm-development-storage.json` records schema version, expected
block-device path, mounted volume path, physical development directories, stable
aliases, legacy roots, migration receipt and active-workspace exceptions. It contains
locations and operational evidence, never credentials. Workers cannot alter it.

Verify the block device identity and mount, not just a directory name. Ordinary
aliases must resolve to the volume device. An active exception must resolve to the
same device/inode as its retained original and name its existing task/session or non-task service/PID.

Persist the source-volume mount, the stable bind aliases and their dependency order.
Use service `RequiresMountsFor` guards for development admission. The volume must be
available before admitting work. Do not weaken existing worker sandbox paths, ACLs,
GitHub App scope or repository leases to make the new location accessible.

Keep router receipts, authentication, supervisor state, conversation stores and
original request IDs at their existing registered locations. Existing runtime code
may continue using stable aliases; do not rewrite every task, checkout or Git path.

## Active workspace exception

A safe exception keeps an active workspace's original inode accessible through all
registered aliases. If the parent root is relocated, an inode-preserving bind pin
must be established before the parent alias changes, and restored before the parent
recursive bind on boot. Avoid symlinks where the host registration rejects them.
Retain the original root behind a private legacy bind; do not rename a root still
used by a live worker namespace. Before host mount changes, inspect every affected
worker's mount namespace and existing read/write restrictions. Keep protected worker
namespaces private so new host mounts cannot bypass their read-only paths. Verify
the original aliases, device/inode and mount access flags inside those namespaces
afterwards. Do not change a worker's namespace identity, PID or effective write scope.

Rehearse this with a disposable process holding both cwd and an open file before
touching live work. Verify the process can still read/write through relative and
registered absolute paths, and both paths have identical device/inode identities.
Run `python3 scripts/rehearse_active_pin.py --volume <verified-mounted-volume>`
from this skill as the authorised administrator. It operates only on generated
fixture folders and removes their mounts afterwards; it does not migrate clients.
On the real task verify unchanged worker PID, provider session ID, instruction hash,
lock identity and exactly one saved run. No task submission is part of a disk move.

Record pins as pending physical moves. Do not unmount a live pin or clear its legacy
files. Do not install a new task-completion poller as incidental migration work.
Finalize at a verified idle maintenance point, with no live worker/open cwd/writer,
then copy with ownership, hardlinks and ACLs preserved, verify contents, remove the
pin and check all aliases against the volume device. Retain rollback until accepted.

## Repository layout and compatibility

Use the registered website root for a reusable clone and task-specific worktrees;
keep provider task context/drafts in the existing registered client/provider roots.
Both providers can receive a governed handoff of the same repository, but must not
edit the same branch/worktree concurrently. Keep the current repository-wide lease
until a reviewed host implementation supports finer-grained isolation.

Legacy supervisors with one `repo` checkout continue serialized operation. Installing
this skill does not add Git-worktree support to those supervisors. Record that gap
and route an authorised host improvement rather than silently altering live code.

## Release, operational knowledge and rollback

Publish this skill from canonical Git source. The intended Hermes consumers are
Chief of Staff, Brain/context, Project Manager and the website/setup route; install
only through an approved immutable release. Update caller entry skills to reference
the storage preflight. Pushing a branch is not merging or installing it.

Record the applied host configuration and exceptions in the existing generated
workspace index's human-maintained preamble, or a linked shared operational note.
Preserve generated workspace identities and existing links. Do not invent a new
canonical client folder or replace client knowledge with filesystem paths.

Before rollback verify no active process depends on the replacement paths. Restore
the recorded aliases, fstab/drop-ins and original data under the same task/session;
never replay production to recover a mount. Do not reclaim legacy or rollback data
while a pin or open handle depends on it.
