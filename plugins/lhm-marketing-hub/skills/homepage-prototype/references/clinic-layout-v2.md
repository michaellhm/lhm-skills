# Clinic homepage layout v2

A proven single-location clinic homepage. It started as the Rediscover Physio v2 prototype and was refined over four feedback rounds on Better Backs Better Living (chiropractic, Parramatta, November 2026). Michael's verdict: "I really love this prototype".

- Working code: `assets/better-backs-homepage-example.html` (images load from lhmstaging).
- Live: https://lhmstaging.net/prototypes/better-backs/homepage/
- Original layout reference: https://lhmstaging.net/prototypes/rediscover-physio/homepage/v2.html

Use it when Michael asks for "the Better Backs layout", "the Rediscover layout", or a homepage "like that one", and as the default starting point for a single-location allied health or chiropractic clinic. Multi-location providers with funding schemes and referrers suit the Healthstin example better.

Keep the structure and rhythm and swap everything else: brand colours, logo, photos, copy, nav, offer and services. It is a layout, not a skin. Every word must come from this client's call, site or sitemap.

## Section order

| # | Section (class) | Job | Where the content comes from |
|---|---|---|---|
| 1 | Prototype note, top strip, sticky header (`.proto`, `.strip`, `header.site`) | Address, hours and phone at a glance; nav; one Book button | Live site. **Nav = the top level of the proposed sitemap** (for Better Backs, Marlon's: About, Services, Conditions, Fees, Areas we serve, Learn, Contact). Hide the nav under about 1120px and keep the logo, the Book button and an accessible Menu button that opens the same links (see "Refinements from Eyecentric") |
| 2 | Photo hero (`.hero`) | Eyebrow, H1, one lede, two buttons | Eyebrow carries the SEO term ("Chiropractor in Parramatta"). H1 is a short promise about the experience, not a pain list ("Chiropractic care that finally makes sense"). Put the client's favourite line from the call in the lede. **No condition chips in the hero**: the conditions grid covers them |
| 3 | Trust bar overlapping the hero (`.trust`) | Four quick reasons to trust them | Verified facts only: years in practice, who you'll see, gentle options, location |
| 4 | Team (`.team`) | Faces early | Real portraits; heading in the client's voice ("Two chiropractors who get to know you, and your family") |
| 5 | Outcome band, dark (`.problem` with three `.prob` cards) | What they help people get back to | **The founders' own words from the interview.** Heading names the outcome ("More time doing what you love"); the cards are what makes them different (explaining clearly, gentle and precise care, getting back to everyday life). Not a pain-point band |
| 6 | First visits, photo and numbered steps (`.outcome`, `.ticks`) | Take the fear out of booking | The client's actual new-patient process. Numbering is fine here because the steps really are in order. No caption tag on the photo |
| 7 | New patient offer band (`.offer-card`) | The live offer, clearly framed | Only an offer already on their site. Price block, inclusions and button in one row; the terms run across the bottom. Confirm the price with the client if the site is inconsistent |
| 8 | Conditions grid (`.cond-grid`, eight `.cond` tiles) | "What we help with" | Their service and condition list from the live site, plus a short scope note on what they don't see |
| 9 | How we help, bento (`.bento`, two `.svc.feature` + four `.svc`) | Treatments and technology | Two photo features (core treatment, diagnostics). Four small tiles for differentiators from the call (decompression, instruments, posture checks, progress re-examinations). Don't repeat sections already on the page (first visit, fees) |
| 10 | FAQ band (`.worry`) | Objections before booking | What the client said people worry about |
| 11 | Visit (`.visit`) with a live Google Maps iframe | Getting there | Address, transport, hours; embed `maps.google.com/maps?q=<name, address>&output=embed` |
| 11b | Brands and suppliers (optional, retail-led practices) | Show what they stock and trust | Supplier logos pulled from their products or partners page (Eyecentric: Rodenstock lenses plus eight frame brands), greyscale on a white panel, colour on hover. Confirm the brands are still current |
| 12 | Health fund logos (`.funds`) | "We accept all major private health funds" | Logos pulled from their site, shown greyscale at reduced opacity in a 6/4/3-column grid, colour on hover |
| 13 | Call-to-action card (`.cta-card`) half over the footer | Last push to book | Section background split white/navy at 50%. Brighter gradient card with a thin light border so its bottom edge stays visible; founder portraits and the address on the right |
| 14 | Footer | Visit, contact, hours, Ahpra-style disclaimer | Live site |

## Design system

- Tokens at `:root`: `--navy-900` (dark bands, footer), `--navy-700` (cards, secondary bands), `--cyan` (accent on dark, button fill), `--cyan-deep` (accent text on white), `--cyan-soft` (text on dark, offer background), `--mist`, `--sand`, `--line`. Rename and recolour them from the client's own palette.
- Figtree headings with Noto Sans body, 17px base, 1220px container, 18px card radius, pill buttons at least 52px tall.
- Short kicker labels above headings are fine in this layout because they are consistent and say something. The other rules in `anti-ai-design.md` still apply.

## Logo

Small PNG logos look soft and squashed. Run `scripts/trace_logo.py logo.png assets/ --colour "#MAIN" --colour "#ACCENT"` to make `logo.svg` and `logo-white.svg`, then zoom in and compare with the original. Note it as interim and ask the client for vector files.

## What Michael rejected on the way

- A first attempt with heavy structure and generic copy was "way too AIey". Rebuilding on this layout with plainer copy fixed it.
- A "Sound familiar? Most people wait a while before they call us" pain band was the wrong play. Lead with the outcome and the founders' passion.
- "Back and neck pain, properly explained" read as a description, not a headline. Pull headline candidates from the call (Michael often tests ten on the client) and use the one the client liked.
- The hero photo must show the practitioner's face. Flip it with `transform:scaleX(-1)` if needed, as long as there's no text in the photo.
- Photo caption tags, duplicated first-visit tiles and condition chips in the hero were all removed.

## Compliance

- Ahpra: no outcome claims (immunity, fertility, digestion, anxiety and so on), even when the client tells those stories on the call. Keep "results vary" style terms on offers and a general disclaimer in the footer.
- Don't invent testimonials, credentials, statistics or prices. Record unconfirmed facts in the working notes for the client to check.

## Refinements from Eyecentric (optometry, November 2026)

Michael called the revised Eyecentric homepage "perfect". These rules came from his two review rounds and apply to every build on this layout.

- **Header colour:** use the brand's main colour for the sticky header and a slightly deeper shade for the address strip. A near-black header was "too dark".
- **Dark bands:** use a mid-tone shade of the brand colour, not the darkest shade. Cards on a dark band can be translucent white panels (`rgba(255,255,255,.08)` with a light border) instead of a second solid colour.
- **Section labels:** the hero label is plain white text, with no dash and no underline. Elsewhere the short rule before a label uses the brand colour on light sections and white on dark ones. An accent-colour rule (Eyecentric's coral) read as a stray "red line".
- **Booking buttons:** every button says "Book an appointment", never "Book on <platform>". Use white text. If white fails contrast on the brand colour, darken that colour for the button (Eyecentric teal `#2FA5A2` became `#1F7A77`, 5.11:1) rather than switching to dark text.
- **Team section copy:** lead with the founders' combined experience and what patients get for the price ("more than the minimum"). Don't frame it as "unlike a busy chain", and never name competitors.
- **Brand motifs:** if the client has a distinctive pattern, use it in a few deliberate places (over the hero photo, one band, the final call to action). Don't add an extra decorative strip above the address bar.
- **Footer:** keep it clean, with no navigation link columns. Visit, contact and hours only, plus a disclaimer line. Privacy and Terms become real links in the build. No "concept by" credit.
- **Mobile menu:** below 1120px show a Menu button (`aria-expanded`, `aria-controls`) that drops the nav as a full-width panel. Focus moves to the first link, and Escape closes it and returns focus. At 400px and below, show the icon only with a visually hidden label. The example file includes it.
- **Navigation scope:** an item like "Conditions" goes in the top nav only if the client diagnoses and manages those conditions. If they mostly monitor and refer, list it as a question for the client and fold the pages under the relevant service.
- **Missing photos:** use a free-licence stock photo, not a placeholder panel (see SKILL.md step 4).
