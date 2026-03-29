/**
 * Test: provider-scopes.js exports scopes for all 6 providers
 */
import {
  PROVIDER_SCOPES,
  getDefaultScopes,
  getScopeTypes,
  getProviderIds
} from '../src/data/provider-scopes.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testProviderScopes() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/data/provider-scopes.js'),
    'utf-8'
  )

  // Check for required providers
  const requiredProviders = ['google', 'github', 'twitter', 'instagram', 'discord', 'meta']
  for (const provider of requiredProviders) {
    if (!source.includes(`${provider}:`)) {
      throw new Error(`provider-scopes.js missing provider: ${provider}`)
    }
  }

  // Check for required exports
  const requiredExports = [
    'PROVIDER_SCOPES',
    'getDefaultScopes',
    'getScopeTypes',
    'getProviderIds'
  ]
  for (const exp of requiredExports) {
    if (!source.includes(`export`) || !source.includes(exp)) {
      throw new Error(`provider-scopes.js missing export: ${exp}`)
    }
  }

  // Test functionality
  const providerIds = getProviderIds()
  if (providerIds.length !== 6) {
    throw new Error(`getProviderIds should return 6 providers, found ${providerIds.length}`)
  }

  const scopeTypes = getScopeTypes()
  if (scopeTypes.length !== 3 || !scopeTypes.includes('read')) {
    throw new Error('getScopeTypes should return [read, write, admin]')
  }

  // Test getDefaultScopes for each provider
  for (const provider of requiredProviders) {
    const scopes = getDefaultScopes(provider)
    if (!scopes.read || !scopes.write || !scopes.admin) {
      throw new Error(`getDefaultScopes('${provider}') missing scope types`)
    }
  }

  console.log('✓ provider-scopes.js exports scopes for all 6 providers')
  return true
}

// Run test
testProviderScopes()
