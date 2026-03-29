/**
 * Connection status sync - poll provider for token validity, update UI.
 */

const statusPollers = new Map()
const POLL_INTERVAL = 30000 // 30 seconds default

/**
 * Sync status for provider - poll and update connection status.
 */
export function syncStatus(providerId, options = {}) {
  const interval = options.interval || POLL_INTERVAL

  // Clear existing poller if any
  if (statusPollers.has(providerId)) {
    clearInterval(statusPollers.get(providerId))
  }

  // Start polling
  const poller = setInterval(() => {
    checkProviderStatus(providerId)
  }, interval)

  statusPollers.set(providerId, poller)

  // Initial check
  checkProviderStatus(providerId)

  return () => stopSyncStatus(providerId)
}

/**
 * Check provider status (token validity).
 */
async function checkProviderStatus(providerId) {
  const tokenData = getToken(providerId)

  if (!tokenData) {
    emitStatusUpdate(providerId, { connected: false, valid: false })
    return
  }

  // Check token expiry
  const now = Date.now()
  const expiresAt = tokenData.receivedAt + (tokenData.expiresIn * 1000)
  const isValid = now < expiresAt

  if (!isValid) {
    // Token expired, clear it
    sessionStorage.removeItem(`oauth_token_${providerId}`)
    emitStatusUpdate(providerId, { connected: false, valid: false, expired: true })
    return
  }

  // Token is valid, emit status
  emitStatusUpdate(providerId, {
    connected: true,
    valid: true,
    expiresAt,
    timeRemaining: expiresAt - now
  })
}

/**
 * Stop polling for provider.
 */
export function stopSyncStatus(providerId) {
  if (statusPollers.has(providerId)) {
    clearInterval(statusPollers.get(providerId))
    statusPollers.delete(providerId)
  }
}

/**
 * Stop all status polling.
 */
export function stopAllSyncStatus() {
  statusPollers.forEach(poller => clearInterval(poller))
  statusPollers.clear()
}

/**
 * Emit status update event.
 */
function emitStatusUpdate(providerId, status) {
  window.dispatchEvent(new CustomEvent('oauth:status', {
    detail: { provider: providerId, ...status }
  }))
}

/**
 * Get last synced timestamp for provider.
 */
export function getLastSynced(providerId) {
  const key = `oauth_last_sync_${providerId}`
  return sessionStorage.getItem(key)
}

/**
 * Update last synced timestamp.
 */
export function updateLastSynced(providerId) {
  const key = `oauth_last_sync_${providerId}`
  sessionStorage.setItem(key, new Date().toISOString())
}

/**
 * Get token from session storage.
 */
function getToken(providerId) {
  const stored = sessionStorage.getItem(`oauth_token_${providerId}`)
  if (!stored) return null
  return JSON.parse(stored)
}
