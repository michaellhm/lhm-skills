# Google Ads skill-provenance and handback repair

## Incident

The mhealth Marketing Hub 2.2.0 regression completed its analysis but reported that specialist
skills were applied as inline methodology. The worker selected the `google-ads` agent directly and
embedded `/lhm-marketing-hub:start-googleads` inside contextual prose, so the canonical slash
command was never executed. A repeated failed registration also exposed that the legacy Google Ads
submitter did not scan the failed bucket when allocating run IDs.

## Repair

CAP-015 0.9.0 starts the Google Ads prompt with the installed canonical slash command and removes
the direct agent override. The worker captures Claude `stream-json` events, records observed Skill
tool calls in `skill-provenance.json`, and fails closed unless the monthly review, bid/budget,
conversion-audit and delivery-QA skills were genuinely invoked. Google Ads remains limited to the
strict read-only MCP and registered client/CID evidence boundary.

The governed container client now uses the common collision-safe ID allocator for Google Ads and
general marketing runs. That allocator scans incoming, processed, running and failed buckets.

The first mhealth handback registration then exposed a pre-existing systemd-sandbox mismatch: the
dispatcher attempted its safety copy under read-only `/root`. Release 0.9.1 moves that copy beside
the already-governed registry, preserves root-only mode, and returns a durable refusal if backup
creation ever fails.

Drive and BasicOps remain separate least-privilege handback profiles. This change does not add those
credentials or mutation tools to the Google Ads reader.

## Live diagnostic evidence before source change

A no-MCP Claude trace beginning with `/lhm-marketing-hub:start-googleads` emitted a real `Skill`
tool-use event for `lhm-marketing-hub:google-ads-monthly-review`, followed by a successful tool
result containing the installed skill body. This demonstrated that the plugin was installed and the
defect was entrypoint construction rather than marketplace availability.

## Acceptance

- Source hashes and exact deployed predecessor hashes are pinned in the CAP-015 manifest.
- Python syntax, system-ops validation, plugin version parity and `git diff --check` must pass.
- The focused source/installer suite and full system-ops suite must pass on the governed Hermes test runtime.
- Deployment must preserve a byte-for-byte rollback state.
- A post-deployment no-MCP trace must show the canonical monthly-review Skill call.
- A real client regression is successful only when `skill-provenance.json` verifies all required calls and the separate registered handback workers return Drive and BasicOps readback receipts.
