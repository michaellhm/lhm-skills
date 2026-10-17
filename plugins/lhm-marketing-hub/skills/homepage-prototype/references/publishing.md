# Publishing to lhmstaging

Publishing shows the page to the client. Only publish when the person asks for it in the conversation. Approval to build is not approval to publish.

## Where it goes

- Repository: `michaellhm/lhm-prototype`, branch `main`. Every push to `main` triggers the "Deploy to lhmstaging" action, which copies the repository to `https://lhmstaging.net/prototypes/`.
- Paths: `<client-slug>/homepage/index.html` for the homepage and `<client-slug>/sitemap/index.html` for the matching proposed sitemap. Only touch those paths, `<client-slug>/README.md` and the root `README.md`.
- Add `<meta name="robots" content="noindex, nofollow">` to each page before publishing.
- Add one row per page to the "Current contents" table in the root `README.md`.

## Steps

1. **Independent QA.** Have a separate subagent, which doesn't edit anything, check the file: balanced tags, one `h1`, every external URL returns 200, no placeholder text or em dashes, no secrets or tracking scripts, no local relative dependencies, plus its SHA-256 hash and byte size. When republishing, also have it diff the file against the live version so only the intended changes go out. Fix anything it blocks.
2. Clone the repository fresh (or pull), copy the approved files into place, and confirm the copied hashes match the Drive files.
3. Commit with a clear message and push to `main`.
4. Watch the deploy: `gh run list -R michaellhm/lhm-prototype --commit <sha>` then `gh run watch <id> --exit-status`.
5. Read back each live URL with `curl` and confirm its SHA-256 matches the Drive file exactly.
6. Report the live URLs, the commit and anything QA flagged.

The deploy mirrors the whole repository to the server, so never delete or rewrite other clients' folders.
