# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->

- (2026-07-27) Gmail `create_draft` is the reliable send path. Mailgun via Zapier (`MailgunCLIAPI` / `createEmail`) required an explicit `connection_id` because no default connection was set, and then still returned a 403 from Mailgun. If a user asks for Mailgun, warn them the From address must sit on the connected Mailgun domain (`mail.patienthub.app`), so the mail will not come from their own address or land in their Sent folder.
