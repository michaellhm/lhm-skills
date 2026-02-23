# Standard Viewport Breakpoints for Visual QA

These are the exact viewport sizes to use for every visual QA comparison. Both the prototype and WordPress build must be screenshotted at each breakpoint.

## Breakpoints

| Name | Width | Height | Device Category |
|------|-------|--------|-----------------|
| Desktop Large | 1920px | 1080px | Desktop (1080p) |
| Desktop Standard | 1440px | 900px | Desktop (laptop) |
| Desktop Small | 1280px | 800px | Desktop (small laptop) |
| Tablet Landscape | 1024px | 768px | Tablet (iPad landscape) |
| Tablet Portrait | 768px | 1024px | Tablet (iPad portrait) |
| Mobile Large | 430px | 932px | Mobile (iPhone 15 Pro Max) |
| Mobile Standard | 390px | 844px | Mobile (iPhone 14/15) |
| Mobile Small | 360px | 800px | Mobile (Android standard) |

## Required Screenshots Per Page

For a full QA pass, each page needs screenshots at all 8 breakpoints. That means:
- **Prototype**: 8 screenshots per page
- **WordPress build**: 8 screenshots per page
- **Total per page**: 16 screenshots, producing 8 comparison pairs

## Minimum QA Pass

If time is limited, the minimum acceptable QA pass uses these 4 breakpoints:
- Desktop Standard (1440px)
- Tablet Portrait (768px)
- Mobile Standard (390px)
- Mobile Small (360px)

## Screenshot Settings

- Full-page screenshots (not just the viewport, capture the entire scrollable page)
- Wait for all fonts and images to load before capturing
- Disable cookie banners or popups if possible
- Use a consistent browser (Chromium via Playwright)
