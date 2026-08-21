#!/bin/sh
set -eu

[ "$(id -u)" -eq 0 ] || { echo "root required" >&2; exit 1; }
SOURCE=/home/claudeworker/.local/share/claude/versions/2.1.232
EXPECTED=61d23f8749136907d586d5b11831ea8a5234d4c1dea40a5e55c33b52e204c6d1
TARGET_DIR=/opt/lhm-workflow/claude/2.1.232
TARGET="$TARGET_DIR/claude"
PLUGIN_SOURCE=/home/claudeworker/.claude/plugins/cache/lhm-marketing-skills/lhm-marketing-hub/2.2.0
PLUGIN_TARGET=/opt/lhm-workflow/claude/plugins/lhm-marketing-hub-2.2.0

[ -f "$SOURCE" ] && [ ! -L "$SOURCE" ] || { echo "pinned Claude source absent or linked" >&2; exit 1; }
[ "$(sha256sum "$SOURCE" | cut -d ' ' -f 1)" = "$EXPECTED" ] || { echo "Claude source digest mismatch" >&2; exit 1; }
install -d -o root -g root -m 0755 "$TARGET_DIR"
if [ -e "$TARGET" ]; then
  [ ! -L "$TARGET" ] && [ "$(sha256sum "$TARGET" | cut -d ' ' -f 1)" = "$EXPECTED" ] || {
    echo "conflicting trusted Claude target" >&2; exit 1;
  }
else
  install -o root -g root -m 0755 "$SOURCE" "$TARGET"
fi
[ "$(stat -c '%u:%g:%a' "$TARGET")" = "0:0:755" ] || { echo "trusted Claude target metadata mismatch" >&2; exit 1; }
[ "$(sha256sum "$TARGET" | cut -d ' ' -f 1)" = "$EXPECTED" ] || { echo "trusted Claude target digest mismatch" >&2; exit 1; }
echo "$EXPECTED  $TARGET"
install -d -o root -g root -m 0755 "$PLUGIN_TARGET/.claude-plugin" "$PLUGIN_TARGET/skills/seo-audit" "$PLUGIN_TARGET/skills/seo-content-writer"
for SPEC in \
  '.claude-plugin/plugin.json:187a2f0e9be99f9694b1809ab97563ac629e9bc4b5ede02c568e5c4d6dfe6fb0' \
  'skills/seo-audit/SKILL.md:4986f41bf86c8721c4b1c78d4ff3be26e48afce007f647130a26121fa0654abe' \
  'skills/seo-content-writer/SKILL.md:c0ea7634d3ee8664791d704787b2e53b9a2cc68ac4921a5a49445d1faee06d1f'
do
  REL=${SPEC%%:*}; HASH=${SPEC#*:}; SRC="$PLUGIN_SOURCE/$REL"; DST="$PLUGIN_TARGET/$REL"
  [ -f "$SRC" ] && [ ! -L "$SRC" ] && [ "$(sha256sum "$SRC" | cut -d ' ' -f 1)" = "$HASH" ] || { echo "skill source mismatch: $REL" >&2; exit 1; }
  if [ ! -e "$DST" ]; then install -o root -g root -m 0444 "$SRC" "$DST"; fi
  [ ! -L "$DST" ] && [ "$(stat -c '%u:%g:%a' "$DST")" = '0:0:444' ] && [ "$(sha256sum "$DST" | cut -d ' ' -f 1)" = "$HASH" ] || { echo "skill target mismatch: $REL" >&2; exit 1; }
done
