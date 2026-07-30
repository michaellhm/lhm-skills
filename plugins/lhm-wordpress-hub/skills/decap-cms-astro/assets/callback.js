const githubTokenUrl = 'https://github.com/login/oauth/access_token';

function readCookie(request, name) {
  const cookies = request.headers.get('Cookie') ?? '';
  const match = cookies.match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : undefined;
}

function clearStateCookie() {
  return [
    'decap_oauth_state=',
    'Path=/',
    'Max-Age=0',
    'HttpOnly',
    'Secure',
    'SameSite=Lax',
  ].join('; ');
}

function callbackPage(origin, status, content) {
  const message = `authorization:github:${status}:${JSON.stringify(content)}`;
  const safeOrigin = JSON.stringify(origin).replaceAll('<', '\\u003c');
  const safeMessage = JSON.stringify(message).replaceAll('<', '\\u003c');

  return `<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>GitHub sign-in</title></head>
  <body>
    <p>Completing GitHub sign-in...</p>
    <script>
      (() => {
        const allowedOrigin = ${safeOrigin};
        const result = ${safeMessage};
        const receiveMessage = (event) => {
          if (event.origin !== allowedOrigin || event.source !== window.opener) return;
          window.opener.postMessage(result, allowedOrigin);
          window.removeEventListener('message', receiveMessage);
          window.close();
        };
        window.addEventListener('message', receiveMessage);
        window.opener?.postMessage('authorizing:github', allowedOrigin);
      })();
    </script>
  </body>
</html>`;
}

function htmlResponse(origin, status, content, responseStatus = 200) {
  return new Response(callbackPage(origin, status, content), {
    status: responseStatus,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store',
      'Set-Cookie': clearStateCookie(),
      'Content-Security-Policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'none'; base-uri 'none'; frame-ancestors 'none'",
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer',
    },
  });
}

export async function onRequestGet({ request, env }) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const returnedState = requestUrl.searchParams.get('state');
  const savedState = readCookie(request, 'decap_oauth_state');

  if (!code || !returnedState || !savedState || returnedState !== savedState) {
    return htmlResponse(requestUrl.origin, 'error', { message: 'Invalid or expired OAuth request.' }, 400);
  }

  if (!env.GITHUB_OAUTH_CLIENT_ID || !env.GITHUB_OAUTH_CLIENT_SECRET) {
    return htmlResponse(requestUrl.origin, 'error', { message: 'GitHub OAuth is not configured.' }, 503);
  }

  const tokenResponse = await fetch(githubTokenUrl, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'User-Agent': '__OAUTH_USER_AGENT__',
    },
    body: JSON.stringify({
      client_id: env.GITHUB_OAUTH_CLIENT_ID,
      client_secret: env.GITHUB_OAUTH_CLIENT_SECRET,
      code,
      redirect_uri: `${requestUrl.origin}/callback`,
      state: returnedState,
    }),
  });

  const tokenData = await tokenResponse.json();
  if (!tokenResponse.ok || !tokenData.access_token) {
    return htmlResponse(requestUrl.origin, 'error', {
      message: tokenData.error_description || 'GitHub did not return an access token.',
    }, 502);
  }

  return htmlResponse(requestUrl.origin, 'success', {
    token: tokenData.access_token,
    provider: 'github',
  });
}
