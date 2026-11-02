# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
- (2026-11-02) update_task cannot set status 'Under Review' (it returns an error). Call request_review with the reviewer first, then update_task to move the section.
- (2026-11-02) If a task's updated time changes but list_messages_in_task shows no new comment, check list_replies_in_message on the recent messages, especially review-request notices. Replies, such as Michael's answers, are often nested there.
- (2026-11-02) Never build a BasicOps task or message URL by hand. The l=/m= codes can't be derived from the ID, so use only the url a tool returns, or cite the plain task ID.
