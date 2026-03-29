/**
 * Event bus - workflow eligibility, connect/disconnect events.
 */

const eventListeners = new Map()

/**
 * Emit event on the event bus.
 */
export function emitEvent(eventName, data = {}) {
  const event = new CustomEvent(eventName, { detail: data })

  // Dispatch on window for global listeners
  window.dispatchEvent(event)

  // Also notify registered listeners
  if (eventListeners.has(eventName)) {
    eventListeners.get(eventName).forEach(callback => callback(data))
  }
}

/**
 * Subscribe to event.
 */
export function onEvent(eventName, callback) {
  if (!eventListeners.has(eventName)) {
    eventListeners.set(eventName, [])
  }
  eventListeners.get(eventName).push(callback)

  // Also add window listener
  const handler = (e) => callback(e.detail)
  window.addEventListener(eventName, handler)

  return () => offEvent(eventName, callback)
}

/**
 * Unsubscribe from event.
 */
export function offEvent(eventName, callback) {
  if (eventListeners.has(eventName)) {
    const listeners = eventListeners.get(eventName)
    const index = listeners.indexOf(callback)
    if (index > -1) {
      listeners.splice(index, 1)
    }
  }
}

/**
 * Clear all listeners for event.
 */
export function clearEventListeners(eventName) {
  eventListeners.delete(eventName)
}

/**
 * Clear all event listeners.
 */
export function clearAllEventListeners() {
  eventListeners.clear()
}

// OAuth-specific event emitters

/**
 * Emit provider connected event.
 */
export function emitProviderConnected(providerId, scopes = []) {
  emitEvent('oauth:provider:connected', { provider: providerId, scopes })
}

/**
 * Emit provider disconnected event.
 */
export function emitProviderDisconnected(providerId) {
  emitEvent('oauth:provider:disconnected', { provider: providerId })
}

/**
 * Emit workflow eligibility event.
 */
export function emitWorkflowEligible(eligible, details = {}) {
  emitEvent('oauth:workflow:eligible', { eligible, ...details })
}

/**
 * Emit token expiry event.
 */
export function emitTokenExpiry(providerId) {
  emitEvent('oauth:token:expired', { provider: providerId })
}

/**
 * Listen for provider connected event.
 */
export function onProviderConnected(callback) {
  return onEvent('oauth:provider:connected', callback)
}

/**
 * Listen for provider disconnected event.
 */
export function onProviderDisconnected(callback) {
  return onEvent('oauth:provider:disconnected', callback)
}

/**
 * Listen for workflow eligibility event.
 */
export function onWorkflowEligible(callback) {
  return onEvent('oauth:workflow:eligible', callback)
}
