# Client Onboarding Checklist Contract

Instantiate this structure into `20 Clients/<Client>/project-management/Onboarding.md`. Use the handover and purchased services to generate detailed checks. Preserve the instantiated file as version-stable client state.

## Required properties

- Type: `client-onboarding`
- Status: `active`
- Client link
- Overall owner: Kristalyn
- Current phase
- Started, created and updated dates

## Top-level gates

- [ ] Michael handover and client introduction completed.
- [ ] Invoice and payment setup completed.
- [ ] Kristalyn welcome email and strategy call completed.
- [ ] Required access and assets confirmed.
- [ ] Tracking and configuration confirmed.
- [ ] Purchased services kicked off.
- [ ] Client onboarding completed.

## Detailed checklist sections

### Handover and client contact

- Verify the sales handover and Michael's delivery brief.
- Verify Michael's client introduction was sent.
- Draft and confirm Kristalyn's welcome email.
- Kristalyn schedules and coordinates the strategy call; include Michael when strategic decisions require him.
- Complete the strategy call and record its decisions.
- Create or link the client campaign/project record: the canonical project brief or service record that turns the call decisions into delivery scope.

### Payment and billing

- Confirm signed scope, price, billing contact and payment arrangement.
- Issue the invoice and record payment status.
- Include GoCardless only when it applies to the agreed arrangement.
- Record clearance to proceed or the approved exception.

### Access, assets and configuration

Generate only the checks required by purchased services. Candidate branches include website/CMS, hosting, cPanel, domain/DNS, brand assets, GA4, GTM, GSC, Google Ads, GBP, Meta, booking platform, call tracking, Clarity, forms and CRM. For each included item, record owner and verification method.

### Service kickoff

For every purchased service, record the kickoff skill, destination BasicOps task, delivery owner, initial schedule, next action, connected Drive folder and any explicit deferral.

## Applicability and verification

- Never assume a candidate branch applies merely because it appears here.
- Never omit an uncertain branch silently; confirm and record `N/A — <reason>` when it does not apply.
- If no tracking or configuration branch applies, complete the top-level gate only after recording `N/A — no tracking/configuration required for purchased scope` with human confirmation.
- Tick only after explicit human confirmation or successful system verification.
- Log every completed, deferred, failed or reconciled action with its date and evidence.

## System boundary

- Obsidian: detailed checklist, evidence, decisions and durable state.
- BasicOps: five top-level phases, seven top-level checks, immediate owner and next action.
- Google Drive: assets, working files and deliverables.
