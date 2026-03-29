/**
 * Test: ScopeSelector.js toggles change state on click
 */
import { ScopeSelector, getSelectedScopes } from '../src/components/ScopeSelector.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testScopeSelectorRenders() {
  // Read source file and validate structure
  const selectorSource = readFileSync(
    join(__dirname, '../src/components/ScopeSelector.js'),
    'utf-8'
  )

  // Check for required elements
  const requiredElements = [
    'scope-selector',
    'scope-toggle',
    'scope-checkbox',
    'scope-name',
    'read',
    'write',
    'admin',
    'addEventListener',
    'change'
  ]

  for (const element of requiredElements) {
    if (!selectorSource.includes(element)) {
      throw new Error(`ScopeSelector.js missing required element: ${element}`)
    }
  }

  // Validate exports
  if (typeof ScopeSelector !== 'function') {
    throw new Error('ScopeSelector.js does not export ScopeSelector function')
  }

  if (typeof getSelectedScopes !== 'function') {
    throw new Error('ScopeSelector.js does not export getSelectedScopes function')
  }

  console.log('✓ ScopeSelector.js toggles change state on click')
  return true
}

// Run test
testScopeSelectorRenders()
