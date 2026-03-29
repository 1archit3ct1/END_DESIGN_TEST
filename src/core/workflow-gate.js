/**
 * Workflow gate - verify required providers connected before unlocking workflow.
 */
import { getToken } from './oauth-callback.js'

/**
 * Check if all required providers are connected.
 */
export function checkGate(requiredProviders = []) {
  if (!Array.isArray(requiredProviders) || requiredProviders.length === 0) {
    return { eligible: true, missing: [], connected: [] }
  }

  const connected = []
  const missing = []

  for (const provider of requiredProviders) {
    if (getToken(provider) !== null) {
      connected.push(provider)
    } else {
      missing.push(provider)
    }
  }

  return {
    eligible: missing.length === 0,
    connected,
    missing,
    total: requiredProviders.length,
    connectedCount: connected.length,
    missingCount: missing.length
  }
}

/**
 * Check if specific provider is connected.
 */
export function isProviderConnected(providerId) {
  return getToken(providerId) !== null
}

/**
 * Get connection status for all providers.
 */
export function getAllProvidersStatus(providers = ['google', 'github', 'twitter', 'instagram', 'discord', 'meta']) {
  return providers.map(provider => ({
    provider,
    connected: isProviderConnected(provider)
  }))
}

/**
 * Get minimum providers required for workflow eligibility.
 */
export function getMinimumRequiredProviders() {
  // Default: at least one provider must be connected
  return ['google']
}

/**
 * Check workflow eligibility with minimum requirements.
 */
export function checkWorkflowEligibility() {
  const minimum = getMinimumRequiredProviders()
  return checkGate(minimum)
}
