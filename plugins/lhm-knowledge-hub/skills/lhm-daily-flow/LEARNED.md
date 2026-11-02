# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
- (2026-11-02) Loom's transcript panel only renders a few lines at a time. Get the full text from POST /graphql with operation FetchVideoTranscript (fields source_url, captions_source_url; asking for id fails), then fetch source_url and read phrases[].value with ts.
- (2026-11-02) When a Loom transcript says 'this' or 'here', click play once so the full-length <video> loads, then pause, set currentTime to each timestamp, wait for 'seeked' and screenshot the frame to see what the speaker is pointing at.
