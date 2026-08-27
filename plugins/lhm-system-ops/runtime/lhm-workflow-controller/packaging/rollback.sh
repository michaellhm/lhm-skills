#!/bin/sh
set -eu
test "$(id -u)" -eq 0
approval_claim=${LHM_RELEASE_APPROVAL_CLAIM:-}
test -n "$approval_claim" && test -f "$approval_claim" && test ! -L "$approval_claim" || { echo "signed one-use rollback approval required" >&2; exit 2; }
test "$(stat -c %u "$approval_claim")" = 0 && test "$(stat -c %a "$approval_claim")" = 400 || { echo "unsafe release approval claim" >&2; exit 2; }
python3 -c 'import json,sys; assert json.load(open(sys.argv[1],encoding="utf-8"))["action"]=="rollback"' "$approval_claim" || { echo "rollback approval action mismatch" >&2; exit 2; }
rm -f -- "$approval_claim"
test ! -e "$approval_claim" || { echo "failed to consume rollback approval claim" >&2; exit 2; }
target_release=${1:-}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/var/backups/lhm-workflow-rollback-$stamp"
install -d -o root -g root -m 0700 "$backup"
if test -L /opt/lhm-workflow/current; then
  readlink /opt/lhm-workflow/current > "$backup/current-target"
fi
systemctl disable --now lhm-workflow-bridge.path lhm-workflow-adapter.path lhm-workflow-stage.path lhm-workflow-verifier.path lhm-workflow-verification.path lhm-scheduled-work.path 2>/dev/null || true
systemctl disable --now lhm-barney-monitor.timer 2>/dev/null || true
systemctl disable --now lhm-barney-action-executor.path 2>/dev/null || true
systemctl disable --now lhm-barney-downstream-consumer.path 2>/dev/null || true
systemctl disable --now lhm-delegated-basicops-request.path lhm-delegated-basicops-dispatch.path lhm-delegated-basicops-import.path lhm-delegated-human-observe.path lhm-delegated-human-observe.timer lhm-delegated-human-import.path lhm-delegated-workflow-observe.timer lhm-delegated-workflow-import.path 2>/dev/null || true
for unit in /etc/systemd/system/lhm-scheduled-org-signer-*.path; do
  test ! -e "$unit" || systemctl disable --now "$(basename "$unit")" 2>/dev/null || true
done
systemctl disable --now lhm-department-qa-producer.path lhm-department-lead-producer.path lhm-department-connector-translator.path lhm-department-projection-producer.path lhm-department-hop-producer.path 2>/dev/null || true
if test -n "$target_release"; then
  case "$target_release" in (*[!0-9a-f]*|'') echo "target must be a full lowercase SHA-256" >&2; exit 2;; esac
  test "${#target_release}" -eq 64
  test -d "/opt/lhm-workflow/releases/$target_release"
  ln -sfn "releases/$target_release" /opt/lhm-workflow/current.rollback
  mv -Tf /opt/lhm-workflow/current.rollback /opt/lhm-workflow/current
  printf '%s\n' "$target_release" > "$backup/restored-release"
  systemctl daemon-reload
  systemctl enable --now lhm-workflow-bridge.path lhm-workflow-adapter.path lhm-workflow-stage.path lhm-workflow-verifier.path lhm-workflow-verification.path lhm-scheduled-work.path
  exit 0
fi
for f in /etc/systemd/system/lhm-workflow-*.service /etc/systemd/system/lhm-workflow-*.path; do
  test -e "$f" || continue
  mv "$f" "$backup/"
done
for f in /etc/systemd/system/lhm-scheduled-work.service /etc/systemd/system/lhm-scheduled-work.path; do
  test -e "$f" || continue
  mv "$f" "$backup/"
done
for f in /etc/systemd/system/lhm-scheduled-org-signer-*.service /etc/systemd/system/lhm-scheduled-org-signer-*.path; do
  test ! -e "$f" || rm -f -- "$f"
done
for f in /etc/systemd/system/lhm-department-*.service /etc/systemd/system/lhm-department-*.path; do
  test -e "$f" || continue
  mv "$f" "$backup/"
done
for f in /etc/systemd/system/lhm-barney-monitor.service /etc/systemd/system/lhm-barney-monitor.timer /etc/systemd/system/lhm-barney-action-executor.service /etc/systemd/system/lhm-barney-action-executor.path /etc/systemd/system/lhm-barney-downstream-consumer.service /etc/systemd/system/lhm-barney-downstream-consumer.path; do
  test -e "$f" || continue
  mv "$f" "$backup/"
done
for f in /etc/systemd/system/lhm-delegated-*.service /etc/systemd/system/lhm-delegated-*.path /etc/systemd/system/lhm-delegated-*.timer; do
  test -e "$f" || continue
  mv "$f" "$backup/"
done
systemctl daemon-reload
# Broker/importer executables are preserved in the rollback backup for recovery.
for f in /usr/local/libexec/lhm-department-snapshot-dispatch /usr/local/libexec/lhm-department-snapshot-broker /usr/local/libexec/lhm-department-result-importer /usr/local/libexec/lhm-seo-envelope-runtime /usr/local/libexec/lhm-workflow-registered-adapter /usr/local/libexec/lhm-delegated-basicops-bridge /usr/local/libexec/lhm-scheduled-work-ingress /usr/local/libexec/lhm-scheduled-work-runtime /usr/local/libexec/lhm-barney-monitor /usr/local/libexec/lhm-barney-basicops-watch /usr/local/libexec/lhm-barney-action-executor /usr/local/libexec/lhm-barney-downstream-consumer /home/hermes/.hermes/profiles/lhm_brain/bin/lhm-scheduled-work-dispatch /home/hermes/.hermes/profiles/lhm_brain/bin/lhm-seo-org-cron-alternate; do
  test -e "$f" || continue
  mv "$f" "$backup/"
done
# State, evidence, keys, and versioned releases are deliberately preserved.
