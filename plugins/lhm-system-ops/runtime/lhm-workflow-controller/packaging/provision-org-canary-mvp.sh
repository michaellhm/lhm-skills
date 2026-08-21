#!/bin/sh
set -eu
[ "$(id -u)" = 0 ] || { echo "root required" >&2; exit 1; }
root=/var/lib/lhm-workflow-canary
install -d -o root -g root -m 0700 "$root" "$root/router" "$root/workflow" "$root/evidence" "$root/vault"
if [ ! -e "$root/controller.key" ]; then
  umask 077
  openssl rand 32 > "$root/controller.key"
fi
chown root:root "$root/controller.key"
chmod 0600 "$root/controller.key"
echo "Provisioned disabled manual canary state only; no cron, watcher, or dispatcher was changed."
