#!/usr/bin/env bash
# One-time setup per clone: copies the tracked hooks in .githooks/ into
# .git/hooks/ so they actually run (git never executes hooks straight out of
# a tracked directory).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"

# Hooks live in the common git dir, which is shared by every worktree. Inside a
# worktree $ROOT/.git is a file, not a directory, so resolve it properly rather
# than assuming $ROOT/.git/hooks exists.
HOOKS="$(cd "$ROOT" && cd "$(git rev-parse --git-common-dir)" && pwd)/hooks"
mkdir -p "$HOOKS"

for hook in pre-commit pre-push; do
  cp "$ROOT/.githooks/$hook" "$HOOKS/$hook"
  chmod +x "$HOOKS/$hook"
  echo "Installed $hook -> $HOOKS/$hook"
done
