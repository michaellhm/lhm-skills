# Feedback patterns

Comments that came up while building the Healthstin and Better Backs homepages, and what fixed them. Expect similar feedback from other clients and from Michael.

| Feedback | What fixed it |
|---|---|
| "It looks very AI" | Removed the small uppercase labels, the 01/02/03 numbering, the floating hero stat card, the tick row under the buttons, the stats band and the comparison box. Rewrote headings in plain words. See `anti-ai-design.md`. |
| "Should it be wider?" | Content had been capped at 1200px. 1400px suited a content-heavy homepage. |
| "Not sold on the colours" | Rebuilt the palette from the client's own footer, buttons and clinic pages (charcoal, brand green, referral purple, neutral grey) in place of a generated forest green. |
| "The referrer card takes away from the others" | Made it the same white card as the others, with the accent colour only on its icon and link. |
| "Does it have the wow factor?" | Photo-led service cards, a dark tabbed conditions section, brand-colour rules above headings, star ratings on reviews and gentle fade-ins. Restraint, not flashy effects. |
| "Can we have a background video?" | Full-width muted loop with an overlay, a pause control and a photo fallback, plus a Video/Photo toggle so the client can compare. The client's videos had burned-in captions, so the video was positioned to push them out of frame. |
| "Can we get a better photo of the clinic?" | Searched every service and location page for larger originals. The best images were rarely on the homepage. |
| "Put the logos next to the funding options" | Small scheme logos at the top of each funding card. |
| "Add the awards, with images, in a carousel" | Pulled each year's award graphics from the client's filterable gallery data and built a year-by-year carousel. |
| "Make the bottom call to action like their careers band, all green" | Full-width brand gradient band with the team cut-out breaking out of the top. |
| "Show the team, but in one row" | One horizontally scrolling row of clinicians from the team page. |
| "Drop the FAQs" | FAQs belong on their own page, not the homepage. |
| "That's terrible, way too AIey" (Better Backs v1) | Rebuilt on the clinic layout v2 structure with plainer copy. See `clinic-layout-v2.md`. |
| "The logo doesn't look crisp, it looks squashed" | The client only had a 200px PNG. Traced it to SVG with `scripts/trace_logo.py` and asked for vector files. |
| "Use Marlon's navigation, just the top level" | Copied the top-level items from the proposed sitemap page. |
| "Find the killer headline they liked in the call" | Searched the Fathom transcript for the headlines read out and used the one the client called "perfect". |
| "Most people wait a while before they call us is the wrong play" | Replaced the pain band with an outcome band built from the founders' own words. |
| "Can we see his face in the hero?" | Flipped the photo horizontally. |
| "Add all their services, the health fund logos, the map and the new patient offer" | Eight condition tiles from the live site, greyscale fund logos above the footer, a Google Maps iframe and an offer band with the site's terms. Flagged the conflicting offer prices. |
| "The offer looks a tiny bit off" | Put price, inclusions and button in one row with a divider and moved the terms to a full-width row underneath. |
| "Make the final call to action pop" | A wide gradient card half over the footer, with founder portraits and a light border so its edge stays visible. |
| "Remove the conditions chips from the hero, get SEO in the eyebrow" | Eyebrow became "Chiropractor in Parramatta"; chips removed. |
