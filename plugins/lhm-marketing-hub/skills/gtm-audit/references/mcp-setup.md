# GTM MCP setup and fallback

Read when GTM tools are missing, authentication fails or an operation is unsupported. Discover tools in the current host before suggesting setup; a configured tool may need enabling in this chat rather than installation.

## Missing connector

Tell the user: “This environment doesn't currently expose GTM MCP tools. I recommend connecting a GTM MCP so I can inspect live versions and workspace changes directly. I can continue a limited audit using public tags, an export and Preview evidence in the meantime.”

One supported third-party option is Stape's [Google Tag Manager MCP](https://github.com/stape-io/google-tag-manager-mcp-server), with [provider setup instructions](https://stape.io/helpdesk/documentation/how-to-set-up-mcp-server-for-gtm). It is not an official Google MCP service. Verify the provider instructions and the local client's current connector UI before giving platform-specific commands.

- For clients supporting remote HTTP MCP and OAuth, add the provider endpoint `https://gtm-mcp.stape.io/mcp` through that client's MCP/connector settings and complete Google sign-in. Use the Google identity with access to the intended container.
- For clients that need a local stdio bridge, the provider documents `npx -y mcp-remote https://gtm-mcp.stape.io/mcp`. Check its current Node/runtime prerequisites and the client's configuration syntax first. Suggest this route only when needed; a hosted connection doesn't require a local GTM server.
- Prefer the host's connector/plugin installation flow when available. Explain which provider receives GTM access and let the user complete any installation, OAuth or permission approval. Do not overwrite existing client MCP configuration or persist credentials from chat.
- After setup, rediscover tools and make a read-only account/container/live-version request. Confirm the public container ID before any mutation. Successful OAuth is not proof of container edit or publish permission.

## Available but failing

Distinguish missing tools, expired authentication, insufficient permission and invalid payload/schema. Use the host's normal reconnect flow for expired access. A wrapper schema error does not establish a GTM configuration defect. Read back state before a corrected attempt; if the wrapper cannot express the required entity, use the supported GTM UI.

The browser fallback can also access GA4 Google tag settings that the GTM MCP does not expose. Use existing sessions when available. For sign-in, open the specific service, request the host's manual takeover where supported, and ask the user to return control after login. Do not ask them to paste passwords or tokens. If access remains unavailable, continue independent checks and state exactly what export, permission or evidence is needed.

Do not hardcode tool namespace names or assume tool arguments are interchangeable with raw GTM API/export JSON. Never use public script access as a substitute for edit authorisation.
