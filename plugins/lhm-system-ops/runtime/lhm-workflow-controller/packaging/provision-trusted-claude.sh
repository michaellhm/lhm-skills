#!/bin/sh
set -eu

[ "$(id -u)" -eq 0 ] || { echo "root required" >&2; exit 1; }
SOURCE=/home/claudeworker/.local/share/claude/versions/2.1.232
EXPECTED=61d23f8749136907d586d5b11831ea8a5234d4c1dea40a5e55c33b52e204c6d1
TARGET_DIR=/opt/lhm-workflow/claude/2.1.232
TARGET="$TARGET_DIR/claude"
PLUGIN_PACKAGE=/var/lib/lhm-plugin-releases/lhm-marketing-hub-2.2.2.tar
PLUGIN_PACKAGE_SHA256=61b46faa9105e45c517bdd6d1de78ebee458887896ac7b31eb92c46b959df7ac
PLUGIN_TARGET=/opt/lhm-workflow/claude/plugins/lhm-marketing-hub-2.2.2
PACKAGER=$(dirname "$0")/trusted-marketing-hub-package.py

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
[ -f "$PACKAGER" ] && [ ! -L "$PACKAGER" ] || { echo "trusted Marketing Hub packager absent or linked" >&2; exit 1; }
python3 "$PACKAGER" install "$PLUGIN_PACKAGE" "$(dirname "$PLUGIN_TARGET")" "$PLUGIN_PACKAGE_SHA256"
[ -d "$PLUGIN_TARGET" ] && [ ! -L "$PLUGIN_TARGET" ] || { echo "trusted Marketing Hub target missing" >&2; exit 1; }
echo "$PLUGIN_PACKAGE_SHA256  $PLUGIN_PACKAGE"
