# QA and verification

Check the page the way a client will see it, then check the details a client will never mention but will notice.

## Visual checks

- **Look at real screenshots.** DOM measurements miss ugly things. For full-resolution desktop screenshots use headless Chrome; `scripts/screenshot.sh` captures the full page and crops any section by vertical offset.
- **Headless Chrome won't render narrower than about 500px.** For phone checks use the browser pane's mobile preset (375px wide), not headless Chrome; headless captures below 500px look cut off when they aren't.
- **The browser pane caches local files.** After editing a local HTML file, navigate to it again (or open a fresh tab). Reloading the same tab can show the old version.
- **Resize, then reload.** Some layout logic (for example dropdown flipping) runs on load, so measure after a reload at the new size.

## Checks to run at 1440, 1280 and 375 wide

- The header navigation stays on one row and no dropdown runs past the right edge.
- `document.documentElement.scrollWidth <= innerWidth`: no sideways scroll on the page itself. Carousels may scroll inside their own track.
- Every image has loaded (`naturalWidth > 0`) and the video plays, loops and pauses.
- Menus, tabs, carousels and toggles work by click and by keyboard, and each control only moves its own section (shared class names have broken this before).
- Exactly one `h1`, headings in order, visible focus outlines, buttons at least 44px tall.
- Every text/background pair passes contrast: `python3 scripts/contrast.py "#FFFFFF" "#3B7D23"`.

## Content checks

- No em dashes, placeholder text, invented figures or reworded quotes.
- Australian spelling.
- Claims that need the client's confirmation are listed in the brief's open questions, not buried in the page.
- Award details, team names and roles match the client's own site.

## Hotlinked assets

When images come from the client's site, confirm they load for another domain:

```bash
curl -s -o /dev/null -w '%{http_code}' -r 0-1000 -A 'Mozilla/5.0' -e 'https://lhmstaging.net/' "<image url>"
```

A 200 or 206 means it's fine. If the client's site blocks hotlinking, download the images into an `assets/` folder beside the page.
