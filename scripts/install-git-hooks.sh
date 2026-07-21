#!/usr/bin/env bash
# One-time setup per clone: copies the tracked hooks in .githooks/ into
# .git/hooks/ so they actually run (git never executes hooks straight out of
# a tracked directory).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"

for hook in pre-commit pre-push; do
  cp "$ROOT/.githooks/$hook" "$ROOT/.git/hooks/$hook"
  chmod +x "$ROOT/.git/hooks/$hook"
  echo "Installed $hook"
done
