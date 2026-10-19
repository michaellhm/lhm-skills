# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
- (2026-10-19) Multisite Elementor upgrade method: JetBackup on-demand backups are refused when the cPanel account exceeds its 20 GB on-demand limit, so fall back to the latest daily backup plus 'wp db export - | gzip' outside public_html. Update core with wp-cli, upload Pro zip via Network Admin, run 'wp --url=<site> elementor update db' on one internal site first, then loop the served sites and run 'elementor flush-css'. 'litespeed-purge' only works where the LiteSpeed plugin is active. Verify against a pre-upgrade baseline (data-widget_type counts, forms, links) and every sitemap page. Possible gap: no dedicated network plugin-update skill.
