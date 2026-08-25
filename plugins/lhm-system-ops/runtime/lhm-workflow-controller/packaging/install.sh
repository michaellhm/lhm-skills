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
check_group lhmprojection 10007; check_group lhmhop 10008
check_user lhmprojection 10007; check_user lhmhop 10008
check_group lhmdepartmentqa 10009; check_group lhmdepartmentlead 10010
check_user lhmdepartmentqa 10009; check_user lhmdepartmentlead 10010

units='lhm-workflow-bridge.path lhm-workflow-adapter.path lhm-workflow-stage.path lhm-workflow-verifier.path lhm-workflow-verification.path lhm-workflow-recover.service lhm-scheduled-work.path'
department_units='lhm-department-evidence-attestor.path lhm-department-qa-producer.path lhm-department-lead-producer.path lhm-department-connector-translator.path lhm-department-snapshot-broker.path lhm-department-projection-producer.path lhm-department-hop-producer.path lhm-department-projection-import.path lhm-department-hop-import.path'
systemctl disable --now $units 2>/dev/null || true
systemctl disable --now $department_units 2>/dev/null || true
systemctl disable --now lhm-seo-envelope-runtime.service 2>/dev/null || true
for d in bridge-incoming adapter-source adapter-incoming verifier-requests verifier-results department-signer-requests department-signer-results department-connector-requests department-connector-results qa-requests qa-results lead-requests lead-results projection-requests projection-results hop-requests hop-results; do
  test ! -d "/var/lib/lhm-workflow/$d" || test -z "$(find "/var/lib/lhm-workflow/$d" -type f -name '*.json' -print -quit)" || { echo "refusing install with queued input in $d" >&2; exit 1; }
done

getent group lhmworkflow >/dev/null || groupadd --system --gid 10004 lhmworkflow
getent group lhmworkflowadapter >/dev/null || groupadd --system --gid 10005 lhmworkflowadapter
getent group lhmworkflowverify >/dev/null || groupadd --system --gid 10006 lhmworkflowverify
getent group lhmadapterkey >/dev/null || groupadd --system lhmadapterkey
getent group lhmverifierkey >/dev/null || groupadd --system lhmverifierkey
getent group lhmprojection >/dev/null || groupadd --system --gid 10007 lhmprojection
getent group lhmhop >/dev/null || groupadd --system --gid 10008 lhmhop
getent group lhmdepartmentqa >/dev/null || groupadd --system --gid 10009 lhmdepartmentqa
getent group lhmdepartmentlead >/dev/null || groupadd --system --gid 10010 lhmdepartmentlead
id lhmworkflow >/dev/null 2>&1 || useradd --system --uid 10004 --gid lhmworkflow --no-create-home --shell /usr/sbin/nologin lhmworkflow
id lhmworkflowadapter >/dev/null 2>&1 || useradd --system --uid 10005 --gid lhmworkflowadapter --groups lhmworkflow,lhmadapterkey --no-create-home --shell /usr/sbin/nologin lhmworkflowadapter
id lhmworkflowverify >/dev/null 2>&1 || useradd --system --uid 10006 --gid lhmworkflowverify --groups lhmworkflow,lhmverifierkey --no-create-home --shell /usr/sbin/nologin lhmworkflowverify
id lhmprojection >/dev/null 2>&1 || useradd --system --uid 10007 --gid lhmprojection --no-create-home --shell /usr/sbin/nologin lhmprojection
id lhmhop >/dev/null 2>&1 || useradd --system --uid 10008 --gid lhmhop --no-create-home --shell /usr/sbin/nologin lhmhop
id lhmdepartmentqa >/dev/null 2>&1 || useradd --system --uid 10009 --gid lhmdepartmentqa --no-create-home --shell /usr/sbin/nologin lhmdepartmentqa
id lhmdepartmentlead >/dev/null 2>&1 || useradd --system --uid 10010 --gid lhmdepartmentlead --no-create-home --shell /usr/sbin/nologin lhmdepartmentlead

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
install -d -o lhmworkflow -g lhmworkflow -m 0750 /var/lib/lhm-workflow/scheduled-intake
install -d -o root -g root -m 0755 /etc/lhm-workflow
install -d -o lhmworkflow -g lhmworkflow -m 0750 /var/lib/lhm-workflow/departmental-parents
install -d -o lhmworkflow -g lhmworkflow -m 0750 /var/lib/lhm-workflow/artifacts /var/lib/lhm-workflow/seo-envelope /var/lib/lhm-workflow/seo-failures
install -d -o root -g root -m 0750 /var/lib/lhm-workflow/department-observations
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
install -d -o lhmworkflow -g lhmworkflow -m 0750 /var/lib/lhm-workflow/department-signer-requests /var/lib/lhm-workflow/department-signer-results
install -d -o lhmworkflowadapter -g lhmworkflowadapter -m 0750 /var/lib/lhm-workflow/department-connector-requests /var/lib/lhm-workflow/department-connector-results
install -d -o root -g root -m 0755 /var/lib/lhm-workflow/public
install -d -o lhmprojection -g lhmprojection -m 0750 /var/lib/lhm-workflow/projection-requests /var/lib/lhm-workflow/projection-results
install -d -o lhmhop -g lhmhop -m 0750 /var/lib/lhm-workflow/hop-requests /var/lib/lhm-workflow/hop-results
install -d -o lhmdepartmentqa -g lhmdepartmentqa -m 0750 /var/lib/lhm-workflow/qa-requests /var/lib/lhm-workflow/qa-results
install -d -o lhmdepartmentlead -g lhmdepartmentlead -m 0750 /var/lib/lhm-workflow/lead-requests /var/lib/lhm-workflow/lead-results
install -d -o root -g root -m 0700 /var/lib/lhm-workflow/snapshot-consumed /var/lib/lhm-workflow/snapshot-quarantine /var/lib/lhm-workflow/result-consumed /var/lib/lhm-workflow/result-quarantine
install -d -o root -g root -m 0700 /var/lib/lhm-workflow/evidence-attestor-requests
umask 0077
test -f /var/lib/lhm-workflow/secrets/adapter.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/adapter.key
test -f /var/lib/lhm-workflow/secrets/verifier.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/verifier.key
test -f /var/lib/lhm-workflow/secrets/approval.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/approval.key
test -f /var/lib/lhm-workflow/secrets/head-production.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/head-production.key
test -f /var/lib/lhm-workflow/secrets/production.key || head -c 32 /dev/urandom > /var/lib/lhm-workflow/secrets/production.key
chown root:lhmadapterkey /var/lib/lhm-workflow/secrets/adapter.key; chown root:lhmverifierkey /var/lib/lhm-workflow/secrets/verifier.key
chmod 0640 /var/lib/lhm-workflow/secrets/adapter.key /var/lib/lhm-workflow/secrets/verifier.key
chown root:lhmworkflow /var/lib/lhm-workflow/secrets/approval.key /var/lib/lhm-workflow/secrets/head-production.key /var/lib/lhm-workflow/secrets/production.key
chmod 0640 /var/lib/lhm-workflow/secrets/approval.key /var/lib/lhm-workflow/secrets/head-production.key /var/lib/lhm-workflow/secrets/production.key
test -f /var/lib/lhm-workflow/secrets/projection.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/projection.private.pem
test -f /var/lib/lhm-workflow/secrets/hop.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/hop.private.pem
test -f /var/lib/lhm-workflow/secrets/controller-dispatch.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/controller-dispatch.private.pem
test -f /var/lib/lhm-workflow/secrets/adapter.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/adapter.private.pem
test -f /var/lib/lhm-workflow/secrets/verifier.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/verifier.private.pem
test -f /var/lib/lhm-workflow/secrets/department-qa.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/department-qa.private.pem
test -f /var/lib/lhm-workflow/secrets/department-lead.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/department-lead.private.pem
test -f /var/lib/lhm-workflow/secrets/evidence-attestor.private.pem || openssl genpkey -algorithm ED25519 -out /var/lib/lhm-workflow/secrets/evidence-attestor.private.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/projection.private.pem -pubout -out /var/lib/lhm-workflow/public/projection.public.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/hop.private.pem -pubout -out /var/lib/lhm-workflow/public/hop.public.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/controller-dispatch.private.pem -pubout -out /var/lib/lhm-workflow/public/controller-dispatch.public.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/adapter.private.pem -pubout -out /var/lib/lhm-workflow/public/adapter.public.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/verifier.private.pem -pubout -out /var/lib/lhm-workflow/public/verifier.public.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/department-qa.private.pem -pubout -out /var/lib/lhm-workflow/public/department-qa.public.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/department-lead.private.pem -pubout -out /var/lib/lhm-workflow/public/department-lead.public.pem
openssl pkey -in /var/lib/lhm-workflow/secrets/evidence-attestor.private.pem -pubout -out /var/lib/lhm-workflow/public/evidence-attestor.public.pem
chown root:lhmprojection /var/lib/lhm-workflow/secrets/projection.private.pem; chmod 0640 /var/lib/lhm-workflow/secrets/projection.private.pem
chown root:lhmhop /var/lib/lhm-workflow/secrets/hop.private.pem; chmod 0640 /var/lib/lhm-workflow/secrets/hop.private.pem
chmod 0644 /var/lib/lhm-workflow/public/projection.public.pem /var/lib/lhm-workflow/public/hop.public.pem
chown root:lhmworkflow /var/lib/lhm-workflow/secrets/controller-dispatch.private.pem; chmod 0640 /var/lib/lhm-workflow/secrets/controller-dispatch.private.pem
chmod 0644 /var/lib/lhm-workflow/public/controller-dispatch.public.pem
chown root:lhmadapterkey /var/lib/lhm-workflow/secrets/adapter.private.pem; chmod 0640 /var/lib/lhm-workflow/secrets/adapter.private.pem
chown root:lhmverifierkey /var/lib/lhm-workflow/secrets/verifier.private.pem; chmod 0640 /var/lib/lhm-workflow/secrets/verifier.private.pem
chmod 0644 /var/lib/lhm-workflow/public/adapter.public.pem /var/lib/lhm-workflow/public/verifier.public.pem
chown root:lhmdepartmentqa /var/lib/lhm-workflow/secrets/department-qa.private.pem; chmod 0640 /var/lib/lhm-workflow/secrets/department-qa.private.pem
chown root:lhmdepartmentlead /var/lib/lhm-workflow/secrets/department-lead.private.pem; chmod 0640 /var/lib/lhm-workflow/secrets/department-lead.private.pem
chmod 0644 /var/lib/lhm-workflow/public/department-qa.public.pem /var/lib/lhm-workflow/public/department-lead.public.pem
chown root:root /var/lib/lhm-workflow/secrets/evidence-attestor.private.pem; chmod 0600 /var/lib/lhm-workflow/secrets/evidence-attestor.private.pem
chmod 0644 /var/lib/lhm-workflow/public/evidence-attestor.public.pem

install -o root -g root -m 0644 "$repo_dir"/packaging/lhm-workflow-*.service "$repo_dir"/packaging/lhm-workflow-*.path /etc/systemd/system/
install -o root -g root -m 0644 "$repo_dir"/packaging/lhm-scheduled-work.service "$repo_dir"/packaging/lhm-scheduled-work.path /etc/systemd/system/
install -D -o root -g root -m 0755 "$repo_dir"/integration/lhm-org-role-adapter "$release_dir"/integration/lhm-org-role-adapter
sh "$repo_dir"/packaging/provision-scheduled-signers.sh
scheduled_signer_paths=$(printf '%s ' /etc/systemd/system/lhm-scheduled-org-signer-*.path)
install -o root -g root -m 0644 "$repo_dir"/packaging/lhm-department-*.service "$repo_dir"/packaging/lhm-department-*.path /etc/systemd/system/
install -o root -g root -m 0755 "$repo_dir"/integration/lhm-department-snapshot-dispatch "$repo_dir"/integration/lhm-department-snapshot-broker "$repo_dir"/integration/lhm-department-result-importer /usr/local/libexec/
install -o root -g root -m 0755 "$repo_dir"/integration/lhm-seo-envelope-runtime /usr/local/libexec/lhm-seo-envelope-runtime
install -o root -g root -m 0755 "$repo_dir"/integration/lhm-workflow-registered-adapter /usr/local/libexec/lhm-workflow-registered-adapter
install -o root -g root -m 0755 "$repo_dir"/integration/lhm-scheduled-work-ingress /usr/local/libexec/lhm-scheduled-work-ingress
install -o root -g root -m 0755 "$repo_dir"/integration/lhm-scheduled-work-runtime /usr/local/libexec/lhm-scheduled-work-runtime
install -D -o root -g root -m 0755 "$repo_dir"/integration/lhm-scheduled-work-dispatch /home/hermes/.hermes/profiles/lhm_brain/bin/lhm-scheduled-work-dispatch
install -D -o root -g root -m 0755 "$repo_dir"/integration/lhm-seo-org-cron-alternate /home/hermes/.hermes/profiles/lhm_brain/bin/lhm-seo-org-cron-alternate
install -o root -g root -m 0644 "$repo_dir"/integration/scheduled-workflows.json /etc/lhm-workflow/scheduled-workflows.json
scheduled_base=/home/hermes/.hermes/profiles/lhm_brain/dispatch/scheduled-work
install -d -o root -g 10000 -m 0710 "$scheduled_base"
install -d -o root -g 10000 -m 0730 "$scheduled_base/incoming"
install -d -o root -g 10000 -m 0710 /home/hermes/.hermes/profiles/lhm_brain/dispatch/scheduled-executor
for d in processed failed runs; do install -d -o root -g root -m 0750 "$scheduled_base/$d"; done
systemctl daemon-reload
systemd-analyze verify /etc/systemd/system/lhm-workflow-*.service /etc/systemd/system/lhm-workflow-*.path /etc/systemd/system/lhm-scheduled-work.service /etc/systemd/system/lhm-scheduled-work.path
if test "$enable_units" = 1; then
  for path in $scheduled_signer_paths; do systemctl enable --now "$(basename "$path")"; done
  systemctl enable --now $units
else
  for unit in $units; do
    test "$(systemctl is-enabled "$unit" 2>/dev/null || true)" = disabled
    state=$(systemctl is-active "$unit" 2>/dev/null || true); test "$state" = inactive || test "$state" = failed
  done
  for path in $scheduled_signer_paths; do
    unit=$(basename "$path")
    test "$(systemctl is-enabled "$unit" 2>/dev/null || true)" = disabled
    state=$(systemctl is-active "$unit" 2>/dev/null || true); test "$state" = inactive || test "$state" = failed
  done
fi
for unit in $department_units; do
  test "$(systemctl is-enabled "$unit" 2>/dev/null || true)" = disabled
  state=$(systemctl is-active "$unit" 2>/dev/null || true); test "$state" = inactive || test "$state" = failed
done
test "$(systemctl is-enabled lhm-seo-envelope-runtime.service 2>/dev/null || true)" = disabled
seo_state=$(systemctl is-active lhm-seo-envelope-runtime.service 2>/dev/null || true); test "$seo_state" = inactive || test "$seo_state" = failed
