---
name: lhm-website-dispatch
description: Dispatch bounded website research, drafting, branch work or specialist Website, Prototype, Astro and WordPress review through approved lanes.
---

# LHM Website Dispatch

Choose the narrowest registered lane:

- Specialist review through Claude Code CLI: `/opt/data/profiles/lhm_brain/bin/claude-dispatch submit-specialist-readonly ROUTE SUBJECT_TYPE SUBJECT_NAME OBJECTIVE`.
  - Use `/opt/data/profiles/lhm_brain/bin/claude-dispatch submit-specialist-readonly wordpress-rest SUBJECT_TYPE SUBJECT_NAME OBJECTIVE` for an existing WordPress or LeadScale site whose registered implementation method is the WordPress REST API. This selects `lhm-wordpress-hub:wordpress-lead` and requires `lhm-wordpress-hub:wp-rest-operator`.
  - Use `wordpress` for a broader WordPress build or WP-CLI/SSH workflow.
  - Other supported routes are `website`, `prototype`, and `astro`.
- Registered site work: `/opt/data/profiles/lhm_brain/bin/website-dispatch submit --site SITE --mode MODE --objective OBJECTIVE --success-test TEST --handback HANDBACK`.
- Prototype manifest work: `/opt/data/profiles/lhm_brain/bin/prototype-dispatch submit` only when the registered manifest contract is already prepared.

The Claude specialist route is review-only until a separate registered WordPress REST destination profile supplies the exact site, allowed resources, credential reference and mutation authority. Never tell the Claude worker to bypass that boundary with raw credentials or an unregistered shell request.

Website modes are `research`, `draft`, `branch`, and `release`; the mode does not itself grant authority. Preserve request IDs and resolve through the matching `status` and `result` helper. Never guess a site, path, preview URL, merge or deployment permission.
