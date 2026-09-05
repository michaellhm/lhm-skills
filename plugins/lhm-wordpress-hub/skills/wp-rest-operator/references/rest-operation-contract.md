# WordPress REST operation contract

Use this reference when preparing or executing a REST request. Adapt the resource path to the endpoint discovered from `/wp-json/`; do not assume every custom post type uses `/wp/v2/pages`.

## Request envelope

Record these fields without secret values:

```yaml
client: registered client slug
site_base_url: registered HTTPS origin
credential_reference: registry key, not the credential
resource_collection: /wp-json/wp/v2/pages
resource_id: numeric ID or null for an approved create
operation: inspect | create_draft | update | publish
allowed_fields: [title, slug, content, status]
expected_status: draft | publish
expected_markers: []
success_test: []
publish_authority: absent | explicit
```

Reject redirects to another origin, non-HTTPS production origins, unresolved IDs and fields outside `allowed_fields`.

## Safe HTTP shape

Use an HTTP client that passes credentials as an argument or protected environment input. Disable verbose tracing. Never place an application password in a URL, command transcript, artefact, Git file or handback.

For an update, send a JSON body to the discovered item endpoint:

```http
POST /wp-json/wp/v2/{collection}/{id}
Content-Type: application/json
Authorization: Basic [redacted]

{"content":"...","status":"draft"}
```

Use `status: publish` only when the current task contains explicit publication authority. When changing a published object without publish authority, prepare the exact payload and stop for approval.

## Snapshot and rollback

Before mutation, save a restricted evidence record containing:

- retrieval timestamp and site origin;
- item endpoint, ID, type, slug, status and modified timestamp;
- raw writable fields required to reverse this change;
- SHA-256 of the canonical JSON snapshot.

Keep the snapshot outside Git and client-facing deliverables. Rollback replays only the captured fields to the same numeric ID, then performs the same REST and browser readback as the forward change.

## Readback checks

Require all applicable checks:

- response origin equals the registered origin;
- numeric ID and resource type match;
- returned status equals the authorised target status;
- canonical link and slug are correct;
- raw content hash or expected markers match the submitted payload;
- public/preview response succeeds;
- page-level visual QA passes at desktop and mobile;
- forms and CTAs reach their registered destinations;
- a shared template change did not regress a sampled unaffected page.

If WordPress returns success but omits or rewrites a submitted field, report `stored_value_mismatch`. If the endpoint is absent for a CPT, report `post_type_not_exposed_in_rest`. If authentication works but the action is forbidden, report `capability_not_authorised`; do not retry with broader credentials.
