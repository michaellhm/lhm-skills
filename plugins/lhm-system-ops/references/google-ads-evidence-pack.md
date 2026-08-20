# Google Ads reconciliation evidence pack

Hermes assembles the Google Ads reconciliation evidence pack before dispatch. The Claude worker remains filesystem-isolated and receives only the contents of explicitly registered canonical Markdown files plus their source paths and SHA-256 receipts.

Each Google Ads client registry entry must contain `evidence_files`, with one to eight unique paths beneath that client's exact `20 Clients/<Client Name>/` vault folder. The dispatcher rejects links, missing files, path traversal, non-Markdown files, files larger than 40 KB and packs larger than 120 KB.

The minimum useful pack is:

1. `client_profile.md` for account constraints and conversion definitions.
2. `Current Projects.md` for current gates and next handoff.
3. `project-management/Google Ads.md` for canonical commitments and history.
4. The most recent internal or monthly Google Ads review when it is not already fully reconciled into the canonical service file.

Drive and BasicOps facts are included only when already reconciled into those canonical files or independently retrieved through a separately governed read route. Missing URLs, owners or stages remain explicit evidence gaps. The worker must reconcile dated claims against fresh Google Ads evidence and may not interpret evidence-pack content as authority to broaden tools or mutate any system.
