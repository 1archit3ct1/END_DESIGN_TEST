/**
 * Test: scopeState.js stores/retrieves scopes per provider
 */
import {
  setScopes,
  getScopes,
  hasScope,
  clearScopes,
  clearAllScopes,
  getAllScopes
} from '../src/core/scopeState.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testScopeState() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/scopeState.js'),
    'utf-8'
  )

  // Check for required exports
  const requiredExports = [
    'setScopes',
    'getScopes',
    'hasScope',
    'clearScopes',
    'clearAllScopes',
    'getAllScopes'
  ]

  for (const exp of requiredExports) {
    if (!source.includes(`export function ${exp}`)) {
      throw new Error(`scopeState.js missing export: ${exp}`)
    }
  }

  // Test functionality
  clearAllScopes()

  // Test set and get
  setScopes('google', ['read', 'write'])
  const googleScopes = getScopes('google')
  if (googleScopes.length !== 2 || !googleScopes.includes('read')) {
    throw new Error('setScopes/getScopes failed')
  }

  // Test hasScope
  if (!hasScope('google', 'write')) {
    throw new Error('hasScope failed')
  }
  if (hasScope('google', 'admin')) {
    throw new Error('hasScope should return false for unset scope')
  }

  // Test clearScopes
  clearScopes('google')
  if (getScopes('google').length !== 0) {
    throw new Error('clearScopes failed')
  }

  // Test getAllScopes
  setScopes('github', ['read'])
  setScopes('twitter', ['read', 'write', 'admin'])
  const allScopes = getAllScopes()
  if (!allScopes.github || !allScopes.twitter) {
    throw new Error('getAllScopes failed')
  }

  console.log('✓ scopeState.js stores/retrieves scopes per provider')
  return true
}

// Run test
testScopeState()
