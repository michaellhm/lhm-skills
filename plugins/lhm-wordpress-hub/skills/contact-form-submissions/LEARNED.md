# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
- (2026-10-19) To find silent Elementor form email failures, read /wp-json/elementor/v1/form-submissions and compare actions_count with actions_succeeded_count (plus form_actions_log); a WP Mail SMTP error 'Could not instantiate mail function' means the site is on the default PHP mailer. When client DNS is unavailable, switch WP Mail SMTP to Mailgun on the LHM sending domain, then send a test email and a real form test.
