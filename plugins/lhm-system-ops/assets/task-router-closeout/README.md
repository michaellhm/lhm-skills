# Claude task close-outs

The central router intentionally keeps draft-only workers offline and the Obsidian bisync
state private. Interactive workers receive six connector allowlist entries and previously had
no route to post their own task close-outs or create a client knowledge note.

This adds a credential-free `LHMCloseout` stdio MCP server to the existing
`voyager-review.mcp.json` profile, plus its server-name entry and two native approval rules in
`task-execution.settings.json`. Existing server definitions and approval rules are preserved.
It does not alter the strict no-MCP draft runner, task status, ownership, sync permissions,
SSH/sudo privileges, or existing publication/feedback completion routes.

## Tools

- `get_closeout_context`: revalidate the original human instruction, client, task ownership
  and In Progress status through the router's existing authenticated verifier; return the
  task link, fixed knowledge destination and prior close-out receipts.
- `post_basicops_closeout(draft_name)`: take one flat Markdown file from this task's
  `drafts/`, post a Discussion to that exact task, and verify the full text and author.
  This never completes or reassigns a task. An uncertain remote outcome is reconciled by
  readback; if the exact message is not found, it refuses another create call.
- `write_knowledge_closeout(draft_name)`: create or verify
  `<registered client vault_prefix>/Task Close-outs/<request_id>.md` through the existing
  root-held rclone route. A different existing note fails; `--ignore-existing` prevents a
  competing create from becoming an overwrite. Exact content readback is required.

The local server discovers the UUID from its Claude ancestor and matches one router receipt.
An explicit request ID may also be supplied for controlled tests. The host independently
verifies that request; no worker-provided client, task ID, path, API operation or destination
is accepted. The Unix socket permits only uid 10002 and the daemon verifies SO_PEERCRED.
Workers share that UID in the existing architecture: this is not a new kernel isolation
boundary between simultaneous workers. Client binding relies on the existing verified router
contracts and root-created workspace anchors. Every draft path component uses openat with
O_NOFOLLOW; symlinks, hardlinks, pipes, oversized and non-UTF-8 files fail closed.

The broker uses the existing authenticated BasicOps adapter inside the Hermes container.
It does not copy tokens. Private receipts and locks live in `/var/lib/lhm-task-closeout`
(root 0700); the socket is `/run/lhm-task-closeout/broker.sock` (root:claudeworker 0660).

## Reviewable installation

Create the release archive from the approved immutable Git commit, verify its SHA-256
against the reviewed local archive, and extract this directory to root-private staging on
the authorised VPS. Then run, replacing the commit argument with that exact approved SHA:

```sh
python3 /root/lhm-closeout-stage/install.py --source-commit APPROVED_40_CHARACTER_COMMIT_SHA
systemctl is-active lhm-task-closeout.service
```

The installer writes only `closeout/{host_closeout,closeout_mcp}.py` under the router,
`/etc/systemd/system/lhm-task-closeout.service`, and the two connector JSON files above.
It enables the new service; no existing task service is restarted. It records backups under
`/root/lhm-closeout-backups/<id>/`, including pre-install config and source hashes.

Use `/mcp` in the existing Claude chat to reload/reconnect LHMCloseout. If Claude does not
reload newly added server definitions in place, resume the saved UUID with the refreshed
router connector profile. Never rerun the original task or restart its terminal automatically.
Once visible, call `get_closeout_context`, then request approval to post/write the existing
`closeout-basicops-and-obsidian.md` draft. Do not use the whole sync tree or change task status.

## Validation

```sh
python3 -m unittest discover -s plugins/lhm-system-ops/tests -p test_task_closeout.py -v
```

On the host, run the same tests against deployed source, exercise MCP initialize/list using
the worker identity, and call only get_closeout_context for a real task. Verify uid 10002
still cannot list `/var/lib/lhm-obsidian-sync` and uid 10001 cannot connect to the broker.
Do not create a Discussion or knowledge note as an installation smoke test.

Readback checks on actual writes occur when the human authorises the close-out. BasicOps
HTML transport differences fail closed rather than inventing success. If the original
instruction has fallen outside the router's latest 50 messages or task ownership/state has
changed, the existing verifier refuses delivery; this does not bypass those restrictions.

## Rollback

Stop/disable `lhm-task-closeout.service`, restore the two JSON profiles from the recorded
root-private backup, and reload systemd after removing the added unit. Reconnect the Claude
profile. Retain private receipts to avoid duplicate external writes on reinstall. No vault
permission rollback is needed. Never roll back remote notes or Discussions automatically.
