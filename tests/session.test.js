/**
 * Test: session.js stores, retrieves, clears tokens
 */
import {
  storeToken,
  getToken,
  clearToken,
  clearAllTokens,
  hasValidToken,
  getAllTokens
} from '../src/core/session.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testSession() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/session.js'),
    'utf-8'
  )

  // Check for required exports
  const requiredExports = [
    'storeToken',
    'getToken',
    'clearToken',
    'clearAllTokens',
    'hasValidToken',
    'getAllTokens'
  ]
  for (const exp of requiredExports) {
    if (!source.includes(`export function ${exp}`)) {
      throw new Error(`session.js missing export: ${exp}`)
    }
  }

  // Check for tokenStore Map
  if (!source.includes('tokenStore') || !source.includes('Map()')) {
    throw new Error('session.js missing tokenStore Map')
  }

  // Test functionality
  clearAllTokens()

  // Test store and get
  const futureExpiry = Date.now() + 3600000 // 1 hour from now
  storeToken('google', 'test_token_123', futureExpiry)
  
  const token = getToken('google')
  if (token !== 'test_token_123') {
    throw new Error('storeToken/getToken failed')
  }

  // Test hasValidToken
  if (!hasValidToken('google')) {
    throw new Error('hasValidToken should return true')
  }
  if (hasValidToken('github')) {
    throw new Error('hasValidToken should return false for unset token')
  }

  // Test expiry
  const pastExpiry = Date.now() - 1000 // 1 second ago
  storeToken('expired', 'expired_token', pastExpiry)
  if (getToken('expired') !== null) {
    throw new Error('getToken should return null for expired token')
  }

  // Test clearToken
  clearToken('google')
  if (getToken('google') !== null) {
    throw new Error('clearToken failed')
  }

  // Test getAllTokens
  storeToken('github', 'gh_token', futureExpiry)
  const all = getAllTokens()
  if (!all.github) {
    throw new Error('getAllTokens should include github')
  }

  // Cleanup
  clearAllTokens()

  console.log('✓ session.js stores, retrieves, clears tokens')
  return true
}

// Run test
testSession()
