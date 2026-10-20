# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->

- (2026-10-01) GitHub Transfer needs owner/admin rights on the source repository; collaborator write access cannot transfer. Ask the owner to transfer or grant admin first.
- (2026-10-01) Actions secrets (CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID) carried over with the Alpha transfer and the old URL redirected (301); a manual workflow_dispatch run was enough as the post-transfer test deploy.
- (2026-10-02) Repositories deploying through Vercel need the Vercel GitHub app installed on lhmorg before transfer, or their deployments stop. The Cloudflare app is already installed on lhmorg for all repositories.
- (2026-10-14) Making a repository private on lhmorg (GitHub Free) did not break the Actions + Wrangler deploy (re-tested), but private repos share 2,000 Actions minutes a month; Alpha's deploy takes about a minute.
- (2026-10-14) Two repos for one client can serve different domains (EHP: ehp-website serves the ads subdomain and the new main-site pages). Compare history and what each deploy serves before marking either superseded.
