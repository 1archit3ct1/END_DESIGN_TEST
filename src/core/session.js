/**
 * Session store - in-memory token storage (no persistence).
 */

const tokenStore = new Map()

/**
 * Store token for provider.
 */
export function storeToken(providerId, token, expiry) {
  tokenStore.set(providerId, {
    token,
    expiry,
    createdAt: Date.now()
  })
}

/**
 * Get token for provider.
 */
export function getToken(providerId) {
  const entry = tokenStore.get(providerId)
  if (!entry) return null

  // Check if expired
  if (Date.now() > entry.expiry) {
    tokenStore.delete(providerId)
    return null
  }

  return entry.token
}

/**
 * Clear token for provider.
 */
export function clearToken(providerId) {
  tokenStore.delete(providerId)
}

/**
 * Clear all tokens.
 */
export function clearAllTokens() {
  tokenStore.clear()
}

/**
 * Check if provider has valid token.
 */
export function hasValidToken(providerId) {
  return getToken(providerId) !== null
}

/**
 * Get all stored tokens (for debugging).
 */
export function getAllTokens() {
  return Object.fromEntries(tokenStore)
}
