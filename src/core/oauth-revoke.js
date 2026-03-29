/**
 * OAuth token revocation - call provider revoke endpoint, clear local state.
 */

const OAUTH_REVOKE_ENDPOINTS = {
  google: 'https://oauth2.googleapis.com/revoke',
  github: null, // GitHub doesn't support token revocation
  twitter: null, // Twitter doesn't support token revocation
  instagram: null, // Instagram uses Facebook revoke
  discord: null, // Discord doesn't support token revocation
  meta: 'https://graph.facebook.com/v18.0/permissions'
}

/**
 * Revoke token for provider and clear local state.
 */
export async function revokeToken(providerId) {
  const tokenData = getToken(providerId)
  if (!tokenData) {
    return { success: false, error: 'No token found for provider' }
  }

  const revokeUrl = OAUTH_REVOKE_ENDPOINTS[providerId]

  // Call revoke endpoint if available
  if (revokeUrl) {
    try {
      await callRevokeEndpoint(providerId, revokeUrl, tokenData.accessToken)
    } catch (error) {
      console.warn(`Revoke failed for ${providerId}:`, error.message)
    }
  }

  // Always clear local state
  clearLocalState(providerId)

  return {
    success: true,
    provider: providerId,
    revoked: !!revokeUrl
  }
}

/**
 * Call provider revoke endpoint.
 */
async function callRevokeEndpoint(providerId, url, token) {
  const params = new URLSearchParams({
    token: token
  })

  if (providerId === 'meta') {
    params.append('access_token', token)
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: params.toString()
  })

  if (!response.ok) {
    throw new Error(`Revoke request failed: ${response.statusText}`)
  }

  return true
}

/**
 * Clear local state for provider.
 */
export function clearLocalState(providerId) {
  sessionStorage.removeItem(`oauth_token_${providerId}`)
  sessionStorage.removeItem(`oauth_state_${providerId}`)
  sessionStorage.removeItem(`oauth_pkce_${providerId}`)
}

/**
 * Clear all OAuth state.
 */
export function clearAllOAuthState() {
  const keys = Object.keys(sessionStorage)
  keys.forEach(key => {
    if (key.startsWith('oauth_')) {
      sessionStorage.removeItem(key)
    }
  })
}

/**
 * Get stored token for provider.
 */
function getToken(providerId) {
  const stored = sessionStorage.getItem(`oauth_token_${providerId}`)
  if (!stored) return null
  return JSON.parse(stored)
}

/**
 * Check if provider supports revocation.
 */
export function supportsRevocation(providerId) {
  return OAUTH_REVOKE_ENDPOINTS[providerId] !== null
}

/**
 * Get all providers that support revocation.
 */
export function getRevocableProviders() {
  return Object.entries(OAUTH_REVOKE_ENDPOINTS)
    .filter(([_, url]) => url !== null)
    .map(([provider, _]) => provider)
}
