#!/bin/sh
set -eu
test "$(id -u)" -eq 0
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python_bin=${LHM_WORKFLOW_PYTHON_BIN:-/usr/bin/python3}
release_id=${LHM_WORKFLOW_RELEASE_ID:-}
enable_units=${LHM_WORKFLOW_ENABLE:-0}
case "$release_id" in (*[!0-9a-f]*|'') echo "LHM_WORKFLOW_RELEASE_ID must be a full lowercase SHA-256" >&2; exit 2;; esac
test "${#release_id}" -eq 64 || { echo "release id must be 64 hex characters" >&2; exit 2; }
test "$enable_units" = 0 || test "$enable_units" = 1
"$python_bin" -c 'import sys; assert sys.version_info >= (3,11), sys.version'

check_group() {
  name=$1 gid=$2
  by_name=$(getent group "$name" || true); by_id=$(getent group "$gid" || true)
  test -z "$by_name" || test "$(printf '%s' "$by_name" | cut -d: -f3)" = "$gid" || { echo "group $name has wrong GID" >&2; exit 1; }
  test -z "$by_id" || test "$(printf '%s' "$by_id" | cut -d: -f1)" = "$name" || { echo "GID $gid belongs to another group" >&2; exit 1; }
}
check_user() {
  name=$1 uid=$2
  by_name=$(getent passwd "$name" || true); by_id=$(getent passwd "$uid" || true)
  test -z "$by_name" || test "$(printf '%s' "$by_name" | cut -d: -f3)" = "$uid" || { echo "user $name has wrong UID" >&2; exit 1; }
  test -z "$by_id" || test "$(printf '%s' "$by_id" | cut -d: -f1)" = "$name" || { echo "UID $uid belongs to another user" >&2; exit 1; }
}
check_group lhmworkflow 10004; check_group lhmworkflowadapter 10005; check_group lhmworkflowverify 10006
check_user lhmworkflow 10004; check_user lhmworkflowadapter 10005; check_user lhmworkflowverify 10006

units='lhm-workflow-bridge.path lhm-workflow-adapter.path lhm-workflow-stage.path lhm-workflow-verifier.path lhm-workflow-verification.path lhm-workflow-recover.service'
systemctl disable --now $units 2>/dev/null || true
for d in bridge-incoming adapter-source adapter-incoming verifier-requests verifier-results; do
  test ! -d "/var/lib/lhm-workflow/$d" || test -z "$(find "/var/lib/lhm-workflow/$d" -type f -name '*.json' -print -quit)" || { echo "refusing install with queued input in $d" >&2; exit 1; }
done

getent group lhmworkflow >/dev/null || groupadd --system --gid 10004 lhmworkflow
getent group lhmworkflowadapter >/dev/null || groupadd --system --gid 10005 lhmworkflowadapter
getent group lhmworkflowverify >/dev/null || groupadd --system --gid 10006 lhmworkflowverify
getent group lhmadapterkey >/dev/null || groupadd --system lhmadapterkey
getent group lhmverifierkey >/dev/null || groupadd --system lhmverifierkey
id lhmworkflow >/dev/null 2>&1 || useradd --system --uid 10004 --gid lhmworkflow --no-create-home --shell /usr/sbin/nologin lhmworkflow
id lhmworkflowadapter >/dev/null 2>&1 || useradd --system --uid 10005 --gid lhmworkflowadapter --groups lhmworkflow,lhmadapterkey --no-create-home --shell /usr/sbin/nologin lhmworkflowadapter
id lhmworkflowverify >/dev/null 2>&1 || useradd --system --uid 10006 --gid lhmworkflowverify --groups lhmworkflow,lhmverifierkey --no-create-home --shell /usr/sbin/nologin lhmworkflowverify
usermod -a -G lhmadapterkey,lhmverifierkey lhmworkflow

release_dir=/opt/lhm-workflow/releases/$release_id
test ! -e "$release_dir" || { echo "release already exists; refusing overwrite" >&2; exit 1; }
install -d -o root -g root -m 0755 /opt/lhm-workflow /opt/lhm-workflow/releases "$release_dir" "$release_dir/src"
"$python_bin" -m venv "$release_dir/venv"
cp -R "$repo_dir/src/lhm_workflow" "$release_dir/src/"
find "$release_dir/src/lhm_workflow" -type d -exec chmod 0755 {} \;
find "$release_dir/src/lhm_workflow" -type f -exec chmod 0644 {} \;
install -o root -g root -m 0755 "$repo_dir/packaging/lhm-workflow-prod" "$release_dir/venv/bin/lhm-workflow"
install -o root -g root -m 0755 "$repo_dir/packaging/service-rehearsal.py" "$release_dir/service-rehearsal.py"
printf '%s\n' "$release_id" > "$release_dir/RELEASE_ID"; chmod 0444 "$release_dir/RELEASE_ID"
diff -qr "$repo_dir/src/lhm_workflow" "$release_dir/src/lhm_workflow"
ln -sfn "releases/$release_id" /opt/lhm-workflow/current.new
mv -Tf /opt/lhm-workflow/current.new /opt/lhm-workflow/current

install -d -o lhmworkflow -g lhmworkflow -m 0750 /var/lib/lhm-workflow
for d in parents wal locks receipts operations processed quarantine audit verifier-requests; do install -d -o lhmworkflow -g lhmworkflow -m 0750 "/var/lib/lhm-workflow/$d"; done
touch /var/lib/lhm-workflow/controller.lock
chown lhmworkflow:lhmworkflow /var/lib/lhm-workflow/controller.lock
chmod 0640 /var/lib/lhm-workflow/controller.lock
install -d -o lhmworkflowadapter -g lhmworkflow -m 0750 /var/lib/lhm-workflow/processed/adapter-source /var/lib/lhm-workflow/quarantine/adapter
install -d -o root -g root -m 0700 /var/lib/lhm-workflow/bridge-incoming /var/lib/lhm-workflow/controller-outgoing /var/lib/lhm-workflow/issued-contracts /var/lib/lhm-workflow/host-events /var/lib/lhm-workflow/worker-results /var/lib/lhm-workflow/verifier-worker-results
install -d -o root -g root -m 0700 /var/lib/lhm-workflow/processed/bridge /var/lib/lhm-workflow/quarantine/bridge
install -d -o lhmworkflowverify -g lhmworkflow -m 0750 /var/lib/lhm-workflow/quarantine/verifier
install -d -o root -g lhmworkflowadapter -m 0770 /var/lib/lhm-workflow/adapter-source
install -d -o root -g lhmworkflowadapter -m 0750 /var/lib/lhm-workflow/worker
install -d -o lhmworkflowadapter -g lhmworkflow -m 0770 /var/lib/lhm-workflow/adapter-incoming
install -d -o lhmworkflowadapter -g lhmworkflow -m 0750 /var/lib/lhm-workflow/adapter-incoming/artifacts
chmod 0770 /var/lib/lhm-workflow/verifier-requests
install -d -o lhmworkflowverify -g lhmworkflow -m 0770 /var/lib/lhm-workflow/verifier-results
install -d -o root -g lhmworkflow -m 0750 /var/lib/lhm-workflow/secrets
umask 0077
test -f /var/lib/lhm-workflow/secrets/adapter.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/adapter.key
test -f /var/lib/lhm-workflow/secrets/verifier.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/verifier.key
test -f /var/lib/lhm-workflow/secrets/department-lead.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/department-lead.key
test -f /var/lib/lhm-workflow/secrets/projection.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/projection.key
test -f /var/lib/lhm-workflow/secrets/approval.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/approval.key
test -f /var/lib/lhm-workflow/secrets/head-production.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/head-production.key
test -f /var/lib/lhm-workflow/secrets/production.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/production.key
chown root:lhmadapterkey /var/lib/lhm-workflow/secrets/adapter.key; chown root:lhmverifierkey /var/lib/lhm-workflow/secrets/verifier.key
chmod 0640 /var/lib/lhm-workflow/secrets/adapter.key /var/lib/lhm-workflow/secrets/verifier.key
chown root:lhmworkflow /var/lib/lhm-workflow/secrets/department-lead.key /var/lib/lhm-workflow/secrets/projection.key
chmod 0640 /var/lib/lhm-workflow/secrets/department-lead.key /var/lib/lhm-workflow/secrets/projection.key
chown root:lhmworkflow /var/lib/lhm-workflow/secrets/approval.key /var/lib/lhm-workflow/secrets/head-production.key /var/lib/lhm-workflow/secrets/production.key
chmod 0640 /var/lib/lhm-workflow/secrets/approval.key /var/lib/lhm-workflow/secrets/head-production.key /var/lib/lhm-workflow/secrets/production.key

install -o root -g root -m 0644 "$repo_dir"/packaging/lhm-workflow-*.service "$repo_dir"/packaging/lhm-workflow-*.path /etc/systemd/system/
systemctl daemon-reload
systemd-analyze verify /etc/systemd/system/lhm-workflow-*.service /etc/systemd/system/lhm-workflow-*.path
if test "$enable_units" = 1; then
  systemctl enable --now $units
else
  for unit in $units; do
    test "$(systemctl is-enabled "$unit" 2>/dev/null || true)" = disabled
    state=$(systemctl is-active "$unit" 2>/dev/null || true); test "$state" = inactive || test "$state" = failed
  done
fi
