const githubAuthorizeUrl = 'https://github.com/login/oauth/authorize';

function cookie(name, value, maxAge) {
  return [
    `${name}=${encodeURIComponent(value)}`,
    'Path=/',
    `Max-Age=${maxAge}`,
    'HttpOnly',
    'Secure',
    'SameSite=Lax',
  ].join('; ');
}

export async function onRequestGet({ request, env }) {
  if (!env.GITHUB_OAUTH_CLIENT_ID) {
    return new Response('GitHub OAuth is not configured for this environment.', { status: 503 });
  }

  const requestUrl = new URL(request.url);
  const state = crypto.randomUUID();
  const callbackUrl = `${requestUrl.origin}/callback`;
  const authorizeUrl = new URL(githubAuthorizeUrl);

  authorizeUrl.searchParams.set('client_id', env.GITHUB_OAUTH_CLIENT_ID);
  authorizeUrl.searchParams.set('redirect_uri', callbackUrl);
  authorizeUrl.searchParams.set('scope', '__GITHUB_AUTH_SCOPE__');
  authorizeUrl.searchParams.set('state', state);

  return new Response(null, {
    status: 302,
    headers: {
      Location: authorizeUrl.toString(),
      'Set-Cookie': cookie('decap_oauth_state', state, 600),
      'Cache-Control': 'no-store',
    },
  });
}
