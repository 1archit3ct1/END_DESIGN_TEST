/**
 * Test: ProviderGrid.js renders 6 provider cards
 */
import { ProviderGrid, getProviders } from '../src/components/ProviderGrid.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testProviderGridRenders() {
  // Read source file and validate structure
  const gridSource = readFileSync(
    join(__dirname, '../src/components/ProviderGrid.js'),
    'utf-8'
  )

  // Check for required elements
  const requiredElements = [
    'provider-grid',
    'provider-card-wrapper',
    'data-provider',
    'ProviderCard',
    'getProviders',
    'google',
    'github',
    'twitter',
    'instagram',
    'discord',
    'meta'
  ]

  for (const element of requiredElements) {
    if (!gridSource.includes(element)) {
      throw new Error(`ProviderGrid.js missing required element: ${element}`)
    }
  }

  // Check provider count
  const providerMatches = gridSource.match(/id:\s*'(google|github|twitter|instagram|discord|meta)'/g)
  if (!providerMatches || providerMatches.length !== 6) {
    throw new Error(`ProviderGrid should have 6 providers, found ${providerMatches?.length || 0}`)
  }

  // Validate exports
  if (typeof ProviderGrid !== 'function') {
    throw new Error('ProviderGrid.js does not export ProviderGrid function')
  }

  if (typeof getProviders !== 'function') {
    throw new Error('ProviderGrid.js does not export getProviders function')
  }

  // Verify getProviders returns 6 providers
  const providers = getProviders()
  if (providers.length !== 6) {
    throw new Error(`getProviders should return 6 providers, found ${providers.length}`)
  }

  console.log('✓ ProviderGrid.js renders 6 provider cards')
  return true
}

// Run test
testProviderGridRenders()
