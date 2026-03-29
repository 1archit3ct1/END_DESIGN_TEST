/**
 * Test: oauth-endpoints.js exports endpoints for all 6 providers
 */
import {
  OAUTH_ENDPOINTS,
  getEndpoint,
  getScopesForProvider,
  getAllProviderIds,
  supportsRevocation
} from '../src/core/oauth-endpoints.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testOAuthEndpoints() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/oauth-endpoints.js'),
    'utf-8'
  )

  // Check for required providers
  const requiredProviders = ['google', 'github', 'twitter', 'instagram', 'discord', 'meta']
  for (const provider of requiredProviders) {
    if (!source.includes(`${provider}:`)) {
      throw new Error(`oauth-endpoints.js missing provider: ${provider}`)
    }
  }

  // Check for required exports
  const requiredExports = [
    'OAUTH_ENDPOINTS',
    'getEndpoint',
    'getScopesForProvider',
    'getAllProviderIds',
    'supportsRevocation'
  ]
  for (const exp of requiredExports) {
    if (!source.includes(`export`) || !source.includes(exp)) {
      throw new Error(`oauth-endpoints.js missing export: ${exp}`)
    }
  }

  // Test getAllProviderIds
  const providerIds = getAllProviderIds()
  if (providerIds.length !== 6) {
    throw new Error(`getAllProviderIds should return 6 providers, found ${providerIds.length}`)
  }

  // Test getEndpoint
  for (const provider of requiredProviders) {
    const authUrl = getEndpoint(provider, 'auth')
    if (!authUrl || !authUrl.startsWith('https://')) {
      throw new Error(`getEndpoint('${provider}', 'auth') returned invalid URL`)
    }
  }

  // Test getScopesForProvider
  for (const provider of requiredProviders) {
    const readScopes = getScopesForProvider(provider, 'read')
    if (!Array.isArray(readScopes)) {
      throw new Error(`getScopesForProvider('${provider}', 'read') should return array`)
    }
  }

  // Test supportsRevocation
  if (!supportsRevocation('google')) {
    throw new Error('Google should support revocation')
  }
  if (!supportsRevocation('meta')) {
    throw new Error('Meta should support revocation')
  }
  if (supportsRevocation('github')) {
    throw new Error('GitHub should not support revocation')
  }

  console.log('✓ oauth-endpoints.js exports endpoints for all 6 providers')
  return true
}

// Run test
testOAuthEndpoints()
