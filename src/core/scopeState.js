/**
 * Scope state management - per-provider scope tracking.
 */

const scopeStore = new Map()

/**
 * Set scopes for a provider.
 */
export function setScopes(providerId, scopes) {
  if (!Array.isArray(scopes)) {
    throw new Error('Scopes must be an array')
  }
  scopeStore.set(providerId, scopes)
}

/**
 * Get scopes for a provider.
 */
export function getScopes(providerId) {
  return scopeStore.get(providerId) || []
}

/**
 * Check if provider has a specific scope.
 */
export function hasScope(providerId, scope) {
  const scopes = scopeStore.get(providerId) || []
  return scopes.includes(scope)
}

/**
 * Clear scopes for a provider.
 */
export function clearScopes(providerId) {
  scopeStore.delete(providerId)
}

/**
 * Clear all scopes.
 */
export function clearAllScopes() {
  scopeStore.clear()
}

/**
 * Get all provider scopes.
 */
export function getAllScopes() {
  return Object.fromEntries(scopeStore)
}
