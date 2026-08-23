#!/bin/sh
set -eu
test "$(id -u)" = 0 || { echo root required >&2; exit 1; }
plugin_root=${1:?canonical lhm-wordpress-hub root required}
target=${2:-/etc/lhm-codex/governed-skills}
wp="$plugin_root/skills/wp-start/SKILL.md"
astro="$plugin_root/skills/astro-build/SKILL.md"
test "$(sha256sum "$wp" | cut -d' ' -f1)" = dd1fe010f59228a88365edaef0b7c2d4fc0dc37ced90394b1e48c507d9df56c6
test "$(sha256sum "$astro" | cut -d' ' -f1)" = df7f65cf72103675c5372a97e99d6b3af6ee7c3bf53473b965c62c15fd6e0dfd
install -d -o root -g root -m 0755 "$target/start-astro" "$target/astro-build"
# start-astro is the governed contract alias for the canonical wp-start router.
install -o root -g root -m 0444 "$wp" "$target/start-astro/SKILL.md"
install -o root -g root -m 0444 "$astro" "$target/astro-build/SKILL.md"
printf '%s\n' 'start-astro=wp-start@lhm-wordpress-hub/1.2.20 sha256:dd1fe010f59228a88365edaef0b7c2d4fc0dc37ced90394b1e48c507d9df56c6' > "$target/MANIFEST"
printf '%s\n' 'astro-build=astro-build@lhm-wordpress-hub/1.2.20 sha256:df7f65cf72103675c5372a97e99d6b3af6ee7c3bf53473b965c62c15fd6e0dfd' >> "$target/MANIFEST"
chown root:root "$target/MANIFEST"; chmod 0444 "$target/MANIFEST"
