#!/bin/sh
set -eu
[ "$(id -u)" -eq 0 ] || { echo root required >&2; exit 1; }
ROOT=/var/lib/lhm-workflow-canary
id lhmorg >/dev/null 2>&1 || useradd --system --uid 10110 --home-dir "$ROOT" --shell /usr/sbin/nologin lhmorg
install -d -o lhmorg -g lhmorg -m 0700 "$ROOT" "$ROOT/router" "$ROOT/artifacts" "$ROOT/evidence" "$ROOT/operations" "$ROOT/mappings" "$ROOT/requests" "$ROOT/workflow" "$ROOT/vault" "$ROOT/research-requests" "$ROOT/research-results"
install -d -o root -g lhmorg -m 0710 "$ROOT/keys"
ROLES='lhm_chief_of_staff lhm_head_of_production lhm_seo_lead lhm_researcher lhm_content lhm_website lhm_operations lhm_learning_steward lhm_verifier'
NEXT_UID=10120
for ROLE in $ROLES; do
  USER="lhmsign${NEXT_UID}"
  id "$USER" >/dev/null 2>&1 || useradd --system --uid "$NEXT_UID" --home-dir /nonexistent --shell /usr/sbin/nologin "$USER"
  usermod -a -G lhmorg "$USER"
  PRIVATE="$ROOT/keys/$ROLE.private.pem"; PUBLIC="$ROOT/keys/$ROLE.public.pem"
  if [ ! -e "$PRIVATE" ]; then openssl genpkey -algorithm ED25519 -out "$PRIVATE"; openssl pkey -in "$PRIVATE" -pubout -out "$PUBLIC"; fi
  chown "$USER:$USER" "$PRIVATE"; chmod 0400 "$PRIVATE"; chown root:lhmorg "$PUBLIC"; chmod 0440 "$PUBLIC"
  install -d -o lhmorg -g "$USER" -m 2730 "$ROOT/sign-requests/$ROLE"
  install -d -o "$USER" -g lhmorg -m 2730 "$ROOT/sign-results/$ROLE"
  VERIFY=''
  [ "$ROLE" = lhm_verifier ] && VERIFY="--verifier --registry $ROOT/artifact-registry.json"
  sed -e "s|@USER@|$USER|g" -e "s|@ROLE@|$ROLE|g" -e "s|@VERIFY@|$VERIFY|g" packaging/lhm-org-signer.service.in > "/etc/systemd/system/lhm-org-signer-$ROLE.service"
  sed -e "s|@ROLE@|$ROLE|g" packaging/lhm-org-signer.path.in > "/etc/systemd/system/lhm-org-signer-$ROLE.path"
  NEXT_UID=$((NEXT_UID+1))
done
install -o root -g root -m 0644 packaging/lhm-org-research.service packaging/lhm-org-research.path /etc/systemd/system/
systemctl daemon-reload
echo 'Signer path units installed disabled; start only for the bounded manual canary.'
