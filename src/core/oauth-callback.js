/**
 * OAuth callback handler - exchange code for token, validate, store in session.
 */
import { validateStateToken } from './state-token.js'
import { getOAuthEndpoint } from './oauth.js'

const OAUTH_ENDPOINTS = {
  google: { tokenUrl: 'https://oauth2.googleapis.com/token' },
  github: { tokenUrl: 'https://github.com/login/oauth/access_token' },
  twitter: { tokenUrl: 'https://api.twitter.com/2/oauth2/token' },
  instagram: { tokenUrl: 'https://api.instagram.com/oauth/access_token' },
  discord: { tokenUrl: 'https://discord.com/api/oauth2/token' },
  meta: { tokenUrl: 'https://graph.facebook.com/v18.0/oauth/access_token' }
}

/**
 * Handle OAuth callback - exchange code for token.
 */
export async function handleCallback(providerId, code, state) {
  // Validate state token (CSRF protection)
  const stateValidation = validateStateToken(providerId, state)
  if (!stateValidation.valid) {
    throw new Error(`State validation failed: ${stateValidation.error}`)
  }

  // Get PKCE verifier if available
  const codeVerifier = sessionStorage.getItem(`oauth_pkce_${providerId}`)
  sessionStorage.removeItem(`oauth_pkce_${providerId}`)

  // Exchange code for token
  const tokenData = await exchangeCodeForToken(providerId, code, codeVerifier)

  // Validate token response
  if (!tokenData.access_token) {
    throw new Error('No access token received')
  }

  // Store token in session
  const sessionData = {
    accessToken: tokenData.access_token,
    refreshToken: tokenData.refresh_token || null,
    expiresIn: tokenData.expires_in || 3600,
    tokenType: tokenData.token_type || 'Bearer',
    scope: tokenData.scope || '',
    receivedAt: Date.now()
  }

  sessionStorage.setItem(`oauth_token_${providerId}`, JSON.stringify(sessionData))

  return {
    success: true,
    provider: providerId,
    expiresIn: sessionData.expiresIn,
    scope: sessionData.scope
  }
}

/**
 * Exchange authorization code for access token.
 */
async function exchangeCodeForToken(providerId, code, codeVerifier) {
  const endpoint = OAUTH_ENDPOINTS[providerId]
  if (!endpoint) {
    throw new Error(`Unknown provider: ${providerId}`)
  }

  const params = new URLSearchParams({
    client_id: getClientId(providerId),
    client_secret: getClientSecret(providerId),
    code: code,
    grant_type: 'authorization_code',
    redirect_uri: getRedirectUri(providerId)
  })

  if (codeVerifier) {
    params.append('code_verifier', codeVerifier)
  }

  const response = await fetch(endpoint.tokenUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: params.toString()
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Token exchange failed: ${error}`)
  }

  return await response.json()
}

/**
 * Get stored token for provider.
 */
export function getToken(providerId) {
  const stored = sessionStorage.getItem(`oauth_token_${providerId}`)
  if (!stored) return null

  const tokenData = JSON.parse(stored)

  // Check if token is expired
  const now = Date.now()
  const expiresAt = tokenData.receivedAt + (tokenData.expiresIn * 1000)
  if (now > expiresAt) {
    // Token expired, clear it
    sessionStorage.removeItem(`oauth_token_${providerId}`)
    return null
  }

  return tokenData
}

/**
 * Check if provider is connected (has valid token).
 */
export function isConnected(providerId) {
  return getToken(providerId) !== null
}

function getClientId(providerId) {
  return process?.env?.[`OAUTH_${providerId.toUpperCase()}_CLIENT_ID`] || `client_id_${providerId}`
}

function getClientSecret(providerId) {
  return process?.env?.[`OAUTH_${providerId.toUpperCase()}_CLIENT_SECRET`] || `client_secret_${providerId}`
}

function getRedirectUri(providerId) {
  return `${window.location.origin}/oauth/callback/${providerId}`
}
