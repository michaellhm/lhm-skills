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

if getent passwd sourceworker >/dev/null; then
  test "$(id -u sourceworker)" -ne 0 || { echo 'sourceworker cannot be root' >&2; exit 1; }
  test "$(getent passwd sourceworker | cut -d: -f7)" = /usr/sbin/nologin || { echo 'sourceworker shell must be nologin' >&2; exit 1; }
else
  useradd --system --home-dir /var/lib/lhm-source-production --create-home --shell /usr/sbin/nologin sourceworker
fi
install -D -m 0755 assets/container/source-dispatch /opt/data/profiles/lhm_brain/bin/source-dispatch
install -D -m 0755 assets/host/lhm-source-production-runtime /usr/local/libexec/lhm-source-production-runtime
install -D -m 0755 assets/host/lhm-source-adapter /usr/local/libexec/lhm-source-adapter
install -D -o root -g root -m 0755 assets/host/lhm-evidence-fathom-backend /usr/local/libexec/lhm-evidence-fathom-backend
install -D -o root -g root -m 0440 assets/sudoers/lhm-evidence-fathom-backend /etc/sudoers.d/lhm-evidence-fathom-backend
/usr/sbin/visudo -cf /etc/sudoers.d/lhm-evidence-fathom-backend >/dev/null
install -D -m 0755 assets/gateways/lhm-claude-dispatcher /usr/local/libexec/lhm-claude-dispatcher
install -D -m 0755 assets/gateways/lhm-claude-worker /usr/local/libexec/lhm-claude-worker
install -D -m 0755 -o hermes -g hermes assets/hermes/fathom-exact-recording-wrapper /home/hermes/.hermes/profiles/lhm_brain/bin/fathom-exact-recording-wrapper
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
/usr/sbin/runuser -u sourceworker -- /usr/bin/sudo -n -l /usr/local/libexec/lhm-evidence-fathom-backend >/dev/null
/usr/local/libexec/lhm-evidence-bridge-preflight /etc/lhm-source-production/evidence-routes.json >/dev/null
echo 'Installed and validated static assets; path remains disabled. Run manifest-scoped preflight before separately approved enablement.'
