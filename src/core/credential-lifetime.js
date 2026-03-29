/**
 * Credential lifetime management - session timer and expiry handling.
 */

let expiryTimers = new Map()
let sessionStartTime = Date.now()

/**
 * Set credential expiry timer for provider.
 */
export function setCredentialExpiry(providerId, expiryMs) {
  // Clear existing timer if any
  if (expiryTimers.has(providerId)) {
    clearTimeout(expiryTimers.get(providerId))
  }

  // Set new expiry timer
  const timer = setTimeout(() => {
    onCredentialExpiry(providerId)
  }, expiryMs)

  expiryTimers.set(providerId, timer)
}

/**
 * Handle credential expiry for provider.
 */
function onCredentialExpiry(providerId) {
  // Clear from session storage
  sessionStorage.removeItem(`oauth_token_${providerId}`)
  
  // Clear from token store
  sessionStorage.removeItem(`oauth_state_${providerId}`)
  sessionStorage.removeItem(`oauth_pkce_${providerId}`)

  // Emit expiry event
  window.dispatchEvent(new CustomEvent('oauth:expiry', {
    detail: { provider: providerId }
  }))

  expiryTimers.delete(providerId)
}

/**
 * Clear expiry timer for provider.
 */
export function clearCredentialExpiry(providerId) {
  if (expiryTimers.has(providerId)) {
    clearTimeout(expiryTimers.get(providerId))
    expiryTimers.delete(providerId)
  }
}

/**
 * Clear all expiry timers.
 */
export function clearAllExpiryTimers() {
  expiryTimers.forEach(timer => clearTimeout(timer))
  expiryTimers.clear()
}

/**
 * Expire all credentials (called on window close).
 */
export function expireCredentials() {
  // Clear all timers
  clearAllExpiryTimers()

  // Clear all OAuth session storage
  const keys = Object.keys(sessionStorage)
  keys.forEach(key => {
    if (key.startsWith('oauth_')) {
      sessionStorage.removeItem(key)
    }
  })

  // Reset session start time
  sessionStartTime = Date.now()

  // Emit expiry event for all providers
  window.dispatchEvent(new CustomEvent('oauth:expiry:all', {
    detail: { timestamp: Date.now() }
  }))
}

/**
 * Get session duration in milliseconds.
 */
export function getSessionDuration() {
  return Date.now() - sessionStartTime
}

/**
 * Get time until credential expiry.
 */
export function getTimeToExpiry(providerId) {
  // This would need to store expiry times to calculate
  // For now, return null
  return null
}

/**
 * Setup automatic expiry on window close.
 */
export function setupWindowCloseExpiry() {
  window.addEventListener('beforeunload', () => {
    expireCredentials()
  })
}
