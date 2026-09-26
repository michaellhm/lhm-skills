#!/bin/sh
set -eu
test "$(id -u)" -eq 0
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
roles='lhm_chief_of_staff lhm_head_of_production lhm_seo_lead lhm_researcher lhm_content lhm_website lhm_operations lhm_learning_steward lhm_verifier'
install -d -o root -g root -m 0711 /var/lib/lhm-workflow/secrets/org
install -d -o root -g lhmworkflow -m 0750 /var/lib/lhm-workflow/org-signer-requests /var/lib/lhm-workflow/org-signer-results
install -d -o root -g lhmworkflow -m 0750 /var/lib/lhm-workflow/verifier-signing-inputs
for role in $roles; do
  user="lhmsign-$(printf %s "$role" | sed 's/^lhm_//;s/_/-/g')"
  id "$user" >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin "$user"
  usermod -a -G lhmworkflow "$user"
  private="/var/lib/lhm-workflow/secrets/org/$role.private.pem"
  public="/var/lib/lhm-workflow/public/$role.public.pem"
  test -f "$private" || openssl genpkey -algorithm ED25519 -out "$private"
  openssl pkey -in "$private" -pubout -out "$public"
  chown "$user:$user" "$private"; chmod 0400 "$private"
  chown root:root "$public"; chmod 0644 "$public"
  install -d -o lhmworkflow -g "$user" -m 2770 "/var/lib/lhm-workflow/org-signer-requests/$role"
  install -d -o "$user" -g lhmworkflow -m 2730 "/var/lib/lhm-workflow/org-signer-results/$role"
  verify=''
  extra_read=''
  if test "$role" = lhm_verifier; then
    verify='--verifier --registry /var/lib/lhm-workflow/artifact-registry.json'
    extra_read='/var/lib/lhm-workflow/verifier-signing-inputs'
  fi
  sed -e "s|@USER@|$user|g" -e "s|@ROLE@|$role|g" -e "s|@VERIFY@|$verify|g" -e "s|@EXTRA_READ@|$extra_read|g" "$repo_dir/packaging/lhm-scheduled-org-signer.service.in" > "/etc/systemd/system/lhm-scheduled-org-signer-$role.service"
  sed -e "s|@ROLE@|$role|g" "$repo_dir/packaging/lhm-scheduled-org-signer.path.in" > "/etc/systemd/system/lhm-scheduled-org-signer-$role.path"
  chmod 0644 "/etc/systemd/system/lhm-scheduled-org-signer-$role.service" "/etc/systemd/system/lhm-scheduled-org-signer-$role.path"
  systemctl disable --now "lhm-scheduled-org-signer-$role.path" 2>/dev/null || true
done
if test ! -f /var/lib/lhm-workflow/artifact-registry.json; then
  install -o lhmworkflow -g lhmworkflow -m 0640 /dev/null /var/lib/lhm-workflow/artifact-registry.json
  printf '{}\n' > /var/lib/lhm-workflow/artifact-registry.json
fi
chown lhmworkflow:lhmworkflow /var/lib/lhm-workflow/artifact-registry.json
chmod 0640 /var/lib/lhm-workflow/artifact-registry.json
echo 'Scheduled signer units provisioned disabled by default.'
