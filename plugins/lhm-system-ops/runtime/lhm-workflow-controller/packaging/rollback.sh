#!/bin/sh
set -eu
test "$(id -u)" -eq 0
target_release=${1:-}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/var/backups/lhm-workflow-rollback-$stamp"
install -d -o root -g root -m 0700 "$backup"
if test -L /opt/lhm-workflow/current; then
  readlink /opt/lhm-workflow/current > "$backup/current-target"
fi
systemctl disable --now lhm-workflow-bridge.path lhm-workflow-adapter.path lhm-workflow-stage.path lhm-workflow-verifier.path lhm-workflow-verification.path 2>/dev/null || true
if test -n "$target_release"; then
  case "$target_release" in (*[!0-9a-f]*|'') echo "target must be a full lowercase SHA-256" >&2; exit 2;; esac
  test "${#target_release}" -eq 64
  test -d "/opt/lhm-workflow/releases/$target_release"
  ln -sfn "releases/$target_release" /opt/lhm-workflow/current.rollback
  mv -Tf /opt/lhm-workflow/current.rollback /opt/lhm-workflow/current
  printf '%s\n' "$target_release" > "$backup/restored-release"
  exit 0
fi
for f in /etc/systemd/system/lhm-workflow-*.service /etc/systemd/system/lhm-workflow-*.path; do
  test -e "$f" || continue
  mv "$f" "$backup/"
done
systemctl daemon-reload
# State, evidence, keys, and versioned releases are deliberately preserved.
