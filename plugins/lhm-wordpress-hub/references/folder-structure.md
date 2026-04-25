# Canonical Project Folder Structure

The LHM WordPress Hub supports two workflows. Shared client artefacts live at the client root; workflow-specific artefacts live under workflow folders.

## Client root layout

```
[client_root]/
  client_profile.md                       # cross-project — used by WP, LP, GMB, social
  playbook.md                             # Campaign Playbook — cross-project
  website-brief.md                        # Website Brief — cross-project
  clarifications.md                       # cross-project clarifications log
  design/                                 # SHARED design — reusable across projects
    brand_guidelines.md                   # internal brand doc
    brand_style_guide.pdf                 # client-shareable
    design_system.md                      # tokens, scales, component specs

  wordpress/                              # full WordPress build project
  landing-pages/[campaign]/               # PPC landing page campaigns
  gmb/                                    # GMB hub project (existing convention)
```

## Full Website Build — `wordpress/` subtree

```
[client_root]/wordpress/
  website-project-management.md           # root-level PM doc (auto-created Phase 1.5)
  seo/
    keyword_map.md                        # Phase 2 output
    sitemap.md                            # Phase 2 output
    blog_schedule.md                      # Phase 2 output
    page_briefs/                          # Phase 3.1 outputs
      home.md
      about.md
      [service-pages].md
      [location-pages].md
  content/
    home.md                               # Phase 3.2 — client-approved before others
    services/                             # Phase 3.3
    locations/
    supporting/
  prototype/                              # Phase 4.4 — homepage variants
    v1/index.html
    v2/index.html
    v3/index.html
  wp/
    theme/                                # Phase 5.2 — block theme files
    blocks/                               # Phase 5 — custom block source
    blocks.md                             # Phase 4.3 — block architecture decisions
    wp_state.md                           # Phase 5 — WP install state log
  qa/
    visual_qa_reports/                    # Phase 5 visual QA outputs
    launch_checklist.md                   # Phase 6 output
  docs/
    superpowers/
      specs/                              # Phase 1.5 — Superpowers spec docs
      plans/                              # Phase 1.5 — Superpowers implementation plans
```

## Landing Page Campaign — `landing-pages/[campaign]/` subtree

See `references/lp-reference.md` for full LP folder layout. The campaign folder uses `landing-page-project-management.md` as its tracking doc, and references shared brand/design artefacts at `../../design/...`.

## Phase detection rules (full WP build)

| State | Folders/files present | Next phase |
|---|---|---|
| Fresh project | Empty `wordpress/` or only `seo/` | Phase 1 |
| Phase 1 done | `../playbook.md` and `../website-brief.md` exist; `docs/superpowers/specs/` populated | Phase 2 |
| Phase 2 done | `seo/sitemap.md` and `seo/page_briefs/*.md` populated | Phase 3 |
| Phase 3 done | `content/home.md` exists and marked `copy-locked` in PM doc | Phase 4 |
| Phase 4 done | `../design/brand_guidelines.md`, `../design/design_system.md`, `wp/blocks.md`, `prototype/v*/index.html` exist; staging approval logged | Phase 5 |
| Phase 5 done | `wp/wp_state.md` shows site deployed to staging; walkthrough approval logged | Phase 6 |
| Phase 6 done | `qa/launch_checklist.md` signed off | Site live |

## Removed from previous structure

- `/ops/` — merged into `qa/`
- `/client/` (project-level) — moved up to client root
- `/design/` (project-level) — moved up to client root for cross-project reuse
