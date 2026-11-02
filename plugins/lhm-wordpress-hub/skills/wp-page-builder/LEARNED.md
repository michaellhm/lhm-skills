# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
- (2026-11-02) When building Elementor layouts with $e.run('document/elements/create'), settings with the wrong name are silently ignored. Check every key against elementor.widgetsCache[widget].controls (or elementor.config.elements.container.controls) before saving.
- (2026-11-02) Elementor control names that differ from the obvious guess: Post Excerpt colour is title_color; Table of Contents item colour is item_text_color_normal and its font is list_typography_*; a container's grow setting is _flex_size ('grow'); Post Navigation title colour is text_color.
- (2026-11-02) Elementor Pro's Post Excerpt widget shows nothing when a post has no manual excerpt, because the post-excerpt dynamic tag's apply_to_post_content setting defaults to 'no'. Set it to 'yes' to auto-generate, or ask for manual excerpts.
- (2026-11-02) On Kadence sites, Elementor Archive Posts ignores archive_cards_excerpt_length because the theme's excerpt length wins. Limit card summaries with a CSS line-clamp on .elementor-post__excerpt p instead.
- (2026-11-02) To build Theme Builder templates on a live site without anything going public, create them as drafts with no display conditions and preview them with private sample posts (document setting preview_type single/post with preview_id, or archive/recent_posts).
