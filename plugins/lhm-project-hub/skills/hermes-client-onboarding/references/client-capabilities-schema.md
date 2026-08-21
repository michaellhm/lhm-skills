# Client capability schema

## Workflow mapping

| Work | Required capability key |
|---|---|
| SEO research and rollout | `google_search_console` |
| Analytics review | `google_analytics` |
| Google Ads work | `google_ads` |
| Website branch or preview | `website` |
| File storage or retrieval | `google_drive` |
| Task creation or updates | `basicops` |
| Obsidian project or tracker work | `knowledge` |

## Status values

- `unconfigured`: no usable route or identifiers.
- `configured`: configuration exists but its real smoke test has not passed.
- `verified`: a dated real-boundary smoke test passed.
- `failed`: the latest real-boundary smoke test failed.
- `blocked`: onboarding needs a person, approval, or external change.
- `not_applicable`: intentionally unavailable for this client.

`verified` requires a route, identifiers, allowed operations, and a passing `last_test` with an
absolute evidence reference plus the exact lowercase SHA-256 of that evidence file. Search Console
also requires a `binding` object containing the client ID, exact property, the
`google_search_console.property_read` capability, and the exact allowed-operations list. Runtime
preflight verifies the record is a non-linked, non-group/world-writable regular file owned by the
fixed canonical vault owner. Evidence is a separate root-owned `0600` regular file; its bytes and
structured property and capability claims must match the record. The binding must match exactly.

```json
{
  "result": "passed",
  "evidence_ref": "/var/lib/lhm-workflow-canary/evidence/example.json",
  "evidence_sha256": "64-lowercase-hex-characters",
  "binding": {
    "client_id": "example-client",
    "property": "sc-domain:example.test",
    "capability": "google_search_console.property_read",
    "allowed_operations": ["list_sites", "batch_url_inspection", "search_analytics", "list_sitemaps"]
  }
}
```

## Identifier examples

- Search Console: exact `property` URL.
- GA4: exact `property_id` and account label.
- Google Ads: exact `customer_id` and optional manager ID.
- Website: repository, production hostname, staging provider/project.
- Drive: folder ID and human-readable folder name.
- BasicOps: workspace, board, and governed list identifiers.
- Knowledge: vault-relative client root and governed tracker paths.

Identifiers locate resources. They must never include access tokens or credentials.
