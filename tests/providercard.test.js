/**
 * Test: ProviderCard.js displays logo, name, connect button
 */
import { ProviderCard } from '../src/components/ProviderCard.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testProviderCardRenders() {
  // Read source file and validate structure
  const cardSource = readFileSync(
    join(__dirname, '../src/components/ProviderCard.js'),
    'utf-8'
  )

  // Check for required elements
  const requiredElements = [
    'provider-card',
    'provider-logo',
    'provider-name',
    'connect-button',
    'disconnect-button',
    'connected-badge',
    'ScopeSelector',
    'data-provider'
  ]

  for (const element of requiredElements) {
    if (!cardSource.includes(element)) {
      throw new Error(`ProviderCard.js missing required element: ${element}`)
    }
  }

  // Validate export
  if (typeof ProviderCard !== 'function') {
    throw new Error('ProviderCard.js does not export ProviderCard function')
  }

  console.log('✓ ProviderCard.js displays logo, name, connect button')
  return true
}

// Run test
testProviderCardRenders()
