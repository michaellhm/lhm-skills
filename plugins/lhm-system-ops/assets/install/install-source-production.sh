#!/bin/sh
set -eu
install -D -m 0755 assets/container/source-dispatch /opt/data/profiles/lhm_brain/bin/source-dispatch
install -D -m 0755 assets/host/lhm-source-production-runtime /usr/local/libexec/lhm-source-production-runtime
install -D -m 0644 assets/worker/source-production-worker-profile.json /etc/lhm-source-production/worker-profile.json
install -D -m 0644 assets/systemd/lhm-source-production.service /etc/systemd/system/lhm-source-production.service
install -D -m 0644 assets/systemd/lhm-source-production.path /etc/systemd/system/lhm-source-production.path
install -d -m 0750 -o root -g 10000 /home/hermes/.hermes/profiles/lhm_brain/dispatch/source-production/incoming /home/hermes/.hermes/profiles/lhm_brain/dispatch/source-production/events /home/hermes/.hermes/profiles/lhm_brain/dispatch/source-production/runs
echo 'Assets installed but not enabled; deployment requires Michael approval.'
