#!/bin/bash
# Full-page desktop screenshot of a local or live page, optionally cropped to a section.
#
# Usage:
#   screenshot.sh <file-or-url> <out.png> [crop-offset-px] [crop-height-px] [page-height-px]
#
# Examples:
#   screenshot.sh index.html shots/full.png                  # whole page, 1440 wide
#   screenshot.sh index.html shots/team.png 5200 1200        # 1200px slice starting 5200px down
#
# Headless Chrome will not render narrower than about 500px, so use the browser pane's
# mobile preset for phone checks instead.
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC="$1"; OUT="$2"; OFFSET="${3:-}"; CROP_H="${4:-1200}"; PAGE_H="${5:-10000}"

if [[ -f "$SRC" ]]; then
  SRC="file://$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
  SRC="${SRC// /%20}"
fi

FULL="${OUT%.png}-full.png"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=10000 \
  --window-size=1440,"$PAGE_H" --screenshot="$FULL" "$SRC" 2>/dev/null

if [[ -z "$OFFSET" ]]; then
  mv "$FULL" "$OUT"
else
  # Crop by rendering the full screenshot inside a clipped frame (sips crop offsets are unreliable).
  TMP_HTML="$(dirname "$FULL")/.crop-$$.html"
  printf '<html><body style="margin:0;overflow:hidden"><div style="width:1440px;height:%spx;overflow:hidden"><img src="%s" style="display:block;margin-top:-%spx"></div></body></html>' \
    "$CROP_H" "$(basename "$FULL")" "$OFFSET" > "$TMP_HTML"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=1440,"$CROP_H" \
    --screenshot="$OUT" "file://$TMP_HTML" 2>/dev/null
  rm -f "$TMP_HTML"
fi
echo "$OUT"
