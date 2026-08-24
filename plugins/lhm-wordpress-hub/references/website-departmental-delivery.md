# Website Departmental Delivery Contract

## Boundary

- Hermes owns intake, durable state, approval state, dispatch, monitoring and the final BasicOps handoff.
- The installed Claude or Codex worker owns judgement and production through a department Lead and skills.
- A Lead is persistent decision ownership. A skill is a bounded procedure.
- Hermes must never reproduce a sitemap, prototype, Astro build or WordPress change itself.

## Routes

| Route | Lead | Required entry skill | Specialist examples |
|---|---|---|---|
| `prototype` | `prototype-lead` | `start-prototype` | `sitemap-architect`, `html-prototype`, `visual-qa` |
| `astro` | `astro-lead` | `start-astro` | `astro-build`, `decap-cms-astro`, `site-launch-qa` |
| `wordpress` | `wordpress-lead` | `start-wordpress` | `theme-scaffold`, `wp-page-builder`, `wp-ssh-deploy` |

The Lead invokes the required entry skill before specialist work and returns `route_unavailable` rather than improvising when it is missing.

## Dispatch envelope

```yaml
website_department_dispatch:
  schema_version: 1
  request_id: "stable parent/run ID"
  route: prototype | astro | wordpress
  objective: "one bounded outcome"
  client: "confirmed client"
  canonical_client_path: "path or null"
  source_task_url: "BasicOps URL or null"
  source_evidence: []
  approval_state: review_only | approved_for_preparation | approved_for_publish
  mutation_ceiling: read_only | workspace_write | publish_to_prototype_main | deploy
  destination:
    repository: "exact repository or null"
    branch: "exact branch or null"
    client_path: "exact destination path or null"
  completion_test: "observable test"
```

Missing client facts, repository, branch or approval are gaps, not permission to guess.

## Loop and handback

`Hermes intake -> named Lead -> required entry skill -> specialist skills -> website-delivery-qa -> Lead handback -> Hermes state/BasicOps`

For sitemap or homepage mock work, `prototype-lead` owns creation and feedback revisions. Publishing requires `approved_for_publish`, the exact repository, branch and client path, an independently QA-approved manifest, and a Google Drive readback identifying the exact HTML file, byte count and SHA-256. The Lead passes only those bound values to the root-owned publisher; it never receives a repository credential.

Return `request_id`, `route`, `lead`, `entry_skill_invoked`, `skills_used`, Drive file ID/link/hash, evidence, artefacts, mutations, QA verdict, validation, gaps, URL, commit SHA, next owner and status. Completion requires artefact readback and the stated completion test. Publication additionally requires the observed commit SHA, successful deployment and matching public URL; a local file alone is not published.
