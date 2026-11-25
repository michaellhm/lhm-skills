# Website Departmental Delivery Contract

## Boundary

- `astro-lead` owns intake, durable state, approval state, dispatch and monitoring. State lives in the client's internal project file (`20 Clients/<client>/project-management/` and `Current Projects.md` in LHM Knowledge, per `obsidian-context-contract.md`).
- When an external dispatcher such as Hermes supplies the envelope, honour it; otherwise `astro-lead` owns intake and state in the internal project file.
- A Lead is persistent decision ownership. A skill is a bounded procedure.
- `astro-lead` delegates sitemaps, prototypes and Astro builds to their skills and never improvises them itself.

## Lead and routes

`astro-lead` is the website lead. Every website request enters it, and it runs the stage the client is at.

| Stage | Entry skill | Specialist examples |
|---|---|---|
| `sitemap` | `astro-sitemap` | `astro-sitemap` |
| `prototype` | `astro-prototype` | `astro-prototype` |
| `build` | `astro-build` | `astro-build`, `astro-form`, `site-launch-qa` |

`astro-lead` runs the named entry skill before specialist work and returns `route_unavailable` rather than improvising when it is missing.

## Dispatch envelope

```yaml
website_department_dispatch:
  schema_version: 1
  request_id: "stable parent/run ID"
  route: sitemap | prototype | build
  objective: "one bounded outcome"
  client: "confirmed client"
  canonical_client_path: "path or null"
  source_project_file: "path of the internal project file entry or null"
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

`Intake -> astro-lead -> required entry skill -> specialist skills -> website-delivery-qa -> astro-lead handback -> internal project file`

For sitemap or homepage mock work, `astro-lead` owns creation and feedback revisions. Publishing requires `approved_for_publish` (explicit approval from the user), the exact repository, branch and client path, and an independently QA-approved manifest. The publish gate is: explicit approval, push to the stated repository and branch, then verify the remote commit SHA and the Cloudflare deployment URL.

Return `request_id`, `route`, `lead` (`astro-lead`), `entry_skill_invoked`, `skills_used`, evidence, artefacts, mutations, QA verdict, validation, gaps, URL, commit SHA, next owner and status. Completion requires artefact readback and the stated completion test. Publication additionally requires the observed remote commit SHA, a successful deployment and a matching public URL; a local file alone is not published.
