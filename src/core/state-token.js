/**
 * CSRF state token generator for OAuth flows.
 */

/**
 * Generate random state token for CSRF protection.
 */
export function generateStateToken() {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return base64UrlEncode(array)
}

/**
 * Base64URL encode without padding.
 */
function base64UrlEncode(buffer) {
  const base64 = btoa(String.fromCharCode(...buffer))
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

/**
 * Validate state token matches stored value.
 */
export function validateStateToken(providerId, receivedState) {
  const storedState = sessionStorage.getItem(`oauth_state_${providerId}`)
  if (!storedState) {
    return { valid: false, error: 'No stored state found' }
  }

  if (storedState !== receivedState) {
    return { valid: false, error: 'State mismatch' }
  }

  // Clear state after validation (one-time use)
  sessionStorage.removeItem(`oauth_state_${providerId}`)

  return { valid: true }
}

/**
 * Clear stored state for provider.
 */
export function clearStateToken(providerId) {
  sessionStorage.removeItem(`oauth_state_${providerId}`)
}
