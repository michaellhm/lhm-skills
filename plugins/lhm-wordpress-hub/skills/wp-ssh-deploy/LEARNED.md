# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
- (2026-11-02) cPanel sessions are tied to one browser tab (the cpsessNNNN token is in the URL), so a login in another tab doesn't carry over. Open cPanel from the NameHero client area (Manage → Log in to cPanel) in the agent's own tab; this signs in without anyone typing a password.
- (2026-11-02) To upload several files through cPanel from the browser: add a hidden multiple file input to the cPanel page, fill it with the file-upload tool, then POST one FormData (dir, overwrite=1, file-1…n) to /execute/Fileman/upload_files. Keep each batch under 10 MB. Before overwriting, copy the current files server-side into a dated _backup folder with API2 Fileman::fileop op=copy.
- (2026-11-02) Before uploading over a staging site, compare each live file with the local copy and with the pre-edit version. Someone may have edited the server directly (ASP's Back Pain heading was newer on staging than in Drive); copy that change into the local source first so the upload doesn't undo it.
