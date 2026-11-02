# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
- (2026-11-02) When byte-checking files on a Cloudflare-fronted host, public HTML includes Cloudflare email-protection rewrites (/cdn-cgi/l/email-protection, __cf_email__), and cPanel's Fileman/get_file_content moves the <meta charset> tag when it returns a file. Ignore those differences, or compare file sizes and chunk hashes, before calling a mismatch.
