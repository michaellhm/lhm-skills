#!/bin/sh
# Install only. Deliberately never enables or starts the unit.
set -eu
test "$(id -u)" -eq 0 || { echo 'installer must run as root' >&2; exit 1; }
test "$#" -eq 2 || { echo 'usage: install-source-production.sh /root-owned/adapters.json /root-owned/evidence-routes.json' >&2; exit 2; }
config=$1
routes=$2
test -f "$config" || { echo 'operational adapter config is absent' >&2; exit 1; }
test -f "$routes" || { echo 'evidence route registration is absent' >&2; exit 1; }
test "$(stat -c %u "$config")" -eq 0 || { echo 'adapter config must be root-owned' >&2; exit 1; }
test "$(stat -c %u "$routes")" -eq 0 || { echo 'route registration must be root-owned' >&2; exit 1; }
test "$(( $(stat -c %a "$config") % 10 ))" -eq 0 || { echo 'adapter config must not be world accessible' >&2; exit 1; }
test "$(( $(stat -c %a "$routes") % 10 ))" -eq 0 || { echo 'route registration must not be world accessible' >&2; exit 1; }

# These shared live gateways are immutable inputs, never installation targets.
shared_dispatcher=/usr/local/libexec/lhm-claude-dispatcher
shared_worker=/usr/local/libexec/lhm-claude-worker
expected_dispatcher=dbcb320cbb0b3f6fd036e7129c2cc4d37b688ac4d4af50bae5470e497d487f95
expected_worker=ec28d515a37bd3f10e2a2dedf5080a3eb3529065da4b4bc0445ce080a705a531
verify_shared() {
  test "$(sha256sum "$shared_dispatcher" | cut -d' ' -f1)" = "$expected_dispatcher" || { echo 'shared Claude dispatcher differs from verified inventory' >&2; exit 1; }
  test "$(sha256sum "$shared_worker" | cut -d' ' -f1)" = "$expected_worker" || { echo 'shared Claude worker differs from verified inventory' >&2; exit 1; }
  test "$(stat -c '%U:%G %a %s' "$shared_dispatcher")" = 'root:root 755 20336' || { echo 'shared Claude dispatcher metadata differs from verified inventory' >&2; exit 1; }
  test "$(stat -c '%U:%G %a %s' "$shared_worker")" = 'root:root 755 13999' || { echo 'shared Claude worker metadata differs from verified inventory' >&2; exit 1; }
}
verify_shared

if getent passwd sourceworker >/dev/null; then
  test "$(id -u sourceworker)" -ne 0 || { echo 'sourceworker cannot be root' >&2; exit 1; }
  test "$(getent passwd sourceworker | cut -d: -f7)" = /usr/sbin/nologin || { echo 'sourceworker shell must be nologin' >&2; exit 1; }
else
  useradd --system --home-dir /var/lib/lhm-source-production --create-home --shell /usr/sbin/nologin sourceworker
fi
install -D -m 0755 assets/container/source-dispatch /opt/data/profiles/lhm_brain/bin/source-dispatch
install -D -m 0755 assets/host/lhm-source-production-runtime /usr/local/libexec/lhm-source-production-runtime
install -D -m 0755 assets/host/lhm-source-adapter /usr/local/libexec/lhm-source-adapter
install -D -m 0755 assets/gateways/lhm-evidence-claude-dispatcher /usr/local/libexec/lhm-evidence-claude-dispatcher
install -D -m 0755 assets/gateways/lhm-evidence-claude-worker /usr/local/libexec/lhm-evidence-claude-worker
install -D -m 0755 assets/gateways/lhm-evidence-fathom-backend /usr/local/libexec/lhm-evidence-fathom-backend
install -D -m 0755 assets/install/preflight-evidence-bridge.py /usr/local/libexec/lhm-evidence-bridge-preflight
for name in lhm-claude-drive-read lhm-fathom-transcript-read lhm-campaign-production-worker lhm-registered-drive-publisher; do
  ln -sfn lhm-source-adapter "/usr/local/libexec/$name"
done
install -d -m 0750 -o root -g sourceworker /etc/lhm-source-production /etc/lhm-source-production/registrations
install -m 0640 -o root -g sourceworker "$config" /etc/lhm-source-production/adapters.json
install -m 0640 -o root -g sourceworker "$routes" /etc/lhm-source-production/evidence-routes.json
install -D -m 0644 assets/worker/source-production-worker-profile.json /etc/lhm-source-production/worker-profile.json
install -D -m 0644 assets/systemd/lhm-source-production.service /etc/systemd/system/lhm-source-production.service
install -D -m 0644 assets/systemd/lhm-source-production.path /etc/systemd/system/lhm-source-production.path
base=/home/hermes/.hermes/profiles/lhm_brain/dispatch/source-production
for dir in incoming events; do install -d -m 0730 -o root -g 10000 "$base/$dir"; done
for dir in processed failed runs consumed; do install -d -m 0750 -o root -g sourceworker "$base/$dir"; done
systemd-analyze verify /etc/systemd/system/lhm-source-production.service /etc/systemd/system/lhm-source-production.path
for command in /usr/local/libexec/lhm-source-adapter /usr/local/libexec/lhm-claude-drive-read /usr/local/libexec/lhm-fathom-transcript-read /usr/local/libexec/lhm-campaign-production-worker /usr/local/libexec/lhm-registered-drive-publisher /usr/sbin/runuser; do
  test -x "$command" || { echo "unresolved executable: $command" >&2; exit 1; }
done
/usr/sbin/runuser -u sourceworker -- /usr/local/libexec/lhm-source-adapter --validate-config >/dev/null
/usr/local/libexec/lhm-evidence-bridge-preflight /etc/lhm-source-production/evidence-routes.json >/dev/null
verify_shared
systemctl is-enabled lhm-source-production.path >/dev/null 2>&1 && { echo 'source production path unexpectedly enabled' >&2; exit 1; } || :
echo 'Installed and validated static assets; path remains disabled. Run manifest-scoped preflight before separately approved enablement.'
