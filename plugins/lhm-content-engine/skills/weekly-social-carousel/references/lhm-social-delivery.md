# LHM Social delivery

## Purpose and boundary

`lhmorg/lhm-social` is the private source library and protected review site for LHM social carousels. It is not a social publishing system.

The repository build creates:

- one review row per calendar week, newest first
- one interactive slide carousel per approved review package
- an expandable caption with a copy control
- a downloadable ZIP containing the public slide PNG files

Do not generate those controls inside the carousel package. Add the package to `content/` and let the repository build create the review interface.

## Canonical destination

- GitHub repository: `lhmorg/lhm-social`
- verified Mac clone: `/Users/michaelcolman/Documents/Projects/lhm-social`
- package path: `content/YYYY/MM/YYYY-MM-DD-slug/`
- build command: `npm run build`
- deployable output: `dist/`

Verify the remote and local clone before writing. If the clone is unavailable, dirty with overlapping changes, points to another remote, or the requested branch is not explicit, return `blocked` rather than creating a fallback folder.

## Package contract

Copy the completed carousel artefacts into the package directory:

```text
carousel.html
caption.md
manifest.json
source-receipt.private.json
slide-01.png ... slide-N.png
carousel-preview.png
publish.json
```

An image-led package may also contain its copied cover image.

`source-receipt.private.json` stays in the private repository as provenance. It must never enter `dist/`, a slide ZIP, a client-facing export or a social upload.

## Protected-preview gate

Create `publish.json` only after the final privacy check, PNG rendering and artefact readback pass:

```json
{
  "status": "approved",
  "scope": "protected-preview",
  "approved_by": "weekly-social-carousel",
  "approved_on": "YYYY-MM-DD",
  "notes": "Ready for the protected LHM review site only. Social publishing requires separate human approval."
}
```

Here, `approved` means safe and complete enough to appear on the access-controlled review site. It does not mean approved for publication to a social platform.

If the content or privacy review is incomplete, preserve the package without `publish.json` and return `needs_review`.

## Build and acceptance checks

From the verified repository root:

1. Run `npm run build`.
2. Confirm the generated home page contains the expected week row and carousel title.
3. Confirm `dist/carousels/YYYY/MM/YYYY-MM-DD-slug/slides.zip` exists.
4. Test the ZIP and confirm it contains exactly the `slide-NN.png` files recorded by `manifest.json`.
5. Confirm no file ending in `.private.json` exists anywhere under `dist/`.
6. Confirm `dist/carousels/YYYY/MM/YYYY-MM-DD-slug/caption.md`, `carousel.html` and every slide PNG exist.
7. When browser inspection is available, verify next/previous navigation, one visible slide at a time, caption copy and the ZIP link.

Do not report the review site as built when any acceptance check fails.

## Git workflow

- `github.mode: none`: save and verify the package only.
- `github.mode: prepare`: prepare the package and report the changed files without committing.
- `github.mode: commit_push`: commit and push only when the repository and branch exactly match the structured input.
- A scheduled workflow may push directly to `main` only when its saved automation prompt explicitly names `lhmorg/lhm-social`, branch `main`, and authorises the weekly commit and push.
- A manual run without that explicit authority uses a dated content branch.

Before committing, inspect repository status, preserve unrelated changes, run the build checks, scan changed text files for secrets and review the final diff. After pushing, verify the remote SHA and return the commit URL.

Never enable hosting, change Cloudflare settings, modify access permissions or publish to social accounts as an implied part of this delivery.
