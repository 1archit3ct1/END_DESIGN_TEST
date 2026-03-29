/**
 * OAuth connect flow - redirect to OAuth URL with correct scopes.
 */
import { generateStateToken } from './state-token.js'
import { generatePKCE } from './pkce.js'
import { getScopes } from './scopeState.js'
import { getDefaultScopes } from '../data/provider-scopes.js'

const OAUTH_ENDPOINTS = {
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    revokeUrl: 'https://oauth2.googleapis.com/revoke'
  },
  github: {
    authUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    revokeUrl: null
  },
  twitter: {
    authUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    revokeUrl: null
  },
  instagram: {
    authUrl: 'https://www.instagram.com/oauth/authorize',
    tokenUrl: 'https://api.instagram.com/oauth/access_token',
    revokeUrl: null
  },
  discord: {
    authUrl: 'https://discord.com/api/oauth2/authorize',
    tokenUrl: 'https://discord.com/api/oauth2/token',
    revokeUrl: null
  },
  meta: {
    authUrl: 'https://www.facebook.com/v18.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v18.0/oauth/access_token',
    revokeUrl: 'https://graph.facebook.com/v18.0/permissions'
  }
}

/**
 * Redirect to OAuth URL with correct scopes.
 */
export async function connectProvider(providerId, scopes = []) {
  const endpoint = OAUTH_ENDPOINTS[providerId]
  if (!endpoint) {
    throw new Error(`Unknown provider: ${providerId}`)
  }

  const state = generateStateToken()
  const pkce = await generatePKCE()

  // Use provided scopes or default scopes
  const scopeList = scopes.length > 0 ? scopes : getDefaultScopes(providerId)
  const scopeString = Array.isArray(scopeList)
    ? scopeList.join(' ')
    : Object.values(scopeList).flat().join(' ')

  const params = new URLSearchParams({
    client_id: getClientId(providerId),
    redirect_uri: getRedirectUri(providerId),
    response_type: 'code',
    scope: scopeString,
    state: state,
    access_type: 'offline',
    prompt: 'consent'
  })

  // Add PKCE for providers that support it
  if (pkce.codeChallenge) {
    params.append('code_challenge', pkce.codeChallenge)
    params.append('code_challenge_method', 'S256')
  }

  // Store state and PKCE verifier in session for callback validation
  sessionStorage.setItem(`oauth_state_${providerId}`, state)
  sessionStorage.setItem(`oauth_pkce_${providerId}`, pkce.codeVerifier)

  const authUrl = `${endpoint.authUrl}?${params.toString()}`
  window.location.href = authUrl

  return { state, pkce: pkce.codeVerifier }
}

/**
 * Get client ID for provider (from env or config).
 */
function getClientId(providerId) {
  return process?.env?.[`OAUTH_${providerId.toUpperCase()}_CLIENT_ID`] || `client_id_${providerId}`
}

/**
 * Get redirect URI for provider.
 */
function getRedirectUri(providerId) {
  return `${window.location.origin}/oauth/callback/${providerId}`
}

/**
 * Get OAuth endpoint for provider.
 */
export function getOAuthEndpoint(providerId, type = 'auth') {
  const endpoint = OAUTH_ENDPOINTS[providerId]
  if (!endpoint) return null

  switch (type) {
    case 'auth': return endpoint.authUrl
    case 'token': return endpoint.tokenUrl
    case 'revoke': return endpoint.revokeUrl
    default: return endpoint.authUrl
  }
}

/**
 * Get all supported providers.
 */
export function getSupportedProviders() {
  return Object.keys(OAUTH_ENDPOINTS)
}
