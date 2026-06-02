# AHPRA Quick Reference - PMax Optimizer

This is a checklist for compliance gating during a PMax optimisation pass. The full AHPRA framework lives at `pmax-banner-generator/references/ahpra-pmax.md`. Use that for new copy generation. Use this file for the spot-check during optimisation.

## Banned Language (Hard Stops)

Pause any asset, callout, sitelink, or promotion that contains:

- `best`, `top`, `#1`, `leading`, `premier` (without substantiation a regulator would accept)
- `guarantee`, `guaranteed`
- `cure`, `cured`, `cures`, `permanent fix`, `eliminate`
- `expert`, `specialist` (unless the practitioner holds a recognised AHPRA specialist title)
- Testimonials or quoted patient experiences (unless explicit AHPRA-compliant consent on file AND the testimonial passes the "no regulated services / no outcomes" rule - most don't)
- Before / after framing in copy or imagery
- Sensational outcome claims: "transform", "miracle", "life-changing"
- Any claim of restricted services beyond the practitioner's scope

## Yellow Flags (Review Before Approving)

These can be acceptable in narrow contexts but flag for human review:

- `safe` - only if accompanied by qualifying language (TGA-approved, evidence-based)
- `effective` - only with substantiation
- `proven` - only with citation
- `affordable` - fine, but not as a substitute for regulated price disclosure where required
- Any service description that implies a clinical outcome the practitioner can't deliver

## Pricing Claims

AHPRA + ACCC restrict pricing claims for regulated health services. In PMax assets:

- Avoid price-anchored copy (`50% off`, `limited offer`) for regulated services unless the offer meets fair-trading rules.
- Bulk-billing or HICAPS callouts are fine if they are accurate and current.
- Free consultations are fine in copy, but ensure the LP explains scope clearly.

## Image / Asset Compliance

When recommending creative refresh in the action list, push the following requirements through `pmax-banner-generator`:

- No before / after imagery
- No exaggerated body shapes or dramatic transformations
- No images that imply a guaranteed clinical outcome
- No text overlays that would breach the banned-language list
- Real-world clinical / professional environments preferred

## Spot-Check Procedure During Optimisation

1. Pull a sample of currently-serving assets via the GAQL query in `gaql-queries.md` (query 5).
2. For each headline, long headline, description: scan against the banned list.
3. Flag breaches as 🔴 in the checklist row.
4. The recommended action: pause the asset immediately, brief replacement via `pmax-banner-generator`.
5. Note in the report that compliance gating happened - don't quietly fix it without record.

## Non-Healthcare Local Services

If the client is non-healthcare (legal, accounting, trades, real estate), AHPRA doesn't apply. Apply the equivalent compliance lens:

- **Legal**: Australian Solicitors' Conduct Rules (no "win guarantees", no "best lawyer", no comparative claims without substantiation).
- **Financial / Accounting**: ASIC's misleading-conduct provisions, RG 234 (financial advertising).
- **Trades / Home services**: ACL fair-trading rules; pricing claims must be honoured.
- **Real estate**: state-by-state agent codes; no "guaranteed sale" language.

For non-healthcare clients, write the equivalent banned-language list into the report and use it for the spot-check.

## Reference

For the canonical full AHPRA framework, including evidence requirements and the rationale behind each rule, read:

`${CLAUDE_PLUGIN_ROOT}/skills/pmax-banner-generator/references/ahpra-pmax.md`

For broader anti-AI writing guidelines that ALSO apply to every recommendation written into the report, read:

`${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
