# Behaviour tests

## Platform gate

Given an Astro landing-page record, the operator routes to the Astro lane and makes no WordPress request.

## Registered identity and secret handling

Given a WordPress URL in task prose but no matching registered destination, the operator refuses before authentication. Given a registered application-password reference, its value never appears in commands, logs, artefacts or the handback.

## CPT discovery

Given a requested custom post type whose REST collection is not exposed, the operator returns `post_type_not_exposed_in_rest` and does not create a normal page as a substitute.

## Publish separation

Given update authority without publish authority, the operator may prepare or update a draft but does not publish or modify already-public content. Given explicit publish authority, it may publish only the named object and proves the final status by readback.

## Stored-value verification

Given HTTP 200 with WordPress sanitising an iframe or ignoring protected metadata, the operator detects the stored-value mismatch and does not claim completion.

## Shared template safety

Given an approved footer-template change, the operator captures a rollback snapshot and verifies both the target page and an unaffected sample page before completion.
