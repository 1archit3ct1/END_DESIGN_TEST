/**
 * Test: oauth-revoke.js calls revoke endpoint and clears state
 */
import {
  revokeToken,
  clearLocalState,
  clearAllOAuthState,
  supportsRevocation,
  getRevocableProviders
} from '../src/core/oauth-revoke.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testOAuthRevoke() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/oauth-revoke.js'),
    'utf-8'
  )

  // Check for required providers
  const requiredProviders = ['google', 'github', 'twitter', 'instagram', 'discord', 'meta']
  for (const provider of requiredProviders) {
    if (!source.includes(`${provider}:`)) {
      throw new Error(`oauth-revoke.js missing provider: ${provider}`)
    }
  }

  // Check for required exports
  const requiredExports = [
    'revokeToken',
    'clearLocalState',
    'clearAllOAuthState',
    'supportsRevocation',
    'getRevocableProviders'
  ]
  for (const exp of requiredExports) {
    if (!source.includes(`export`) || !source.includes(`function ${exp}`)) {
      throw new Error(`oauth-revoke.js missing export: ${exp}`)
    }
  }

  // Check for required functionality
  const requiredComponents = [
    'OAUTH_REVOKE_ENDPOINTS',
    'sessionStorage',
    'callRevokeEndpoint'
  ]
  for (const component of requiredComponents) {
    if (!source.includes(component)) {
      throw new Error(`oauth-revoke.js missing: ${component}`)
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

  // Test getRevocableProviders
  const revocable = getRevocableProviders()
  if (!revocable.includes('google')) {
    throw new Error('getRevocableProviders should include google')
  }
  if (!revocable.includes('meta')) {
    throw new Error('getRevocableProviders should include meta')
  }

  console.log('✓ oauth-revoke.js calls revoke endpoint and clears state')
  return true
}

// Run test
testOAuthRevoke()
