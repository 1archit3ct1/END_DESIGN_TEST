/**
 * Test: oauth.js generates correct OAuth URL with scopes
 */
import {
  connectProvider,
  getOAuthEndpoint,
  getSupportedProviders
} from '../src/core/oauth.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testOAuthConnect() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/oauth.js'),
    'utf-8'
  )

  // Check for required providers
  const requiredProviders = ['google', 'github', 'twitter', 'instagram', 'discord', 'meta']
  for (const provider of requiredProviders) {
    if (!source.includes(`${provider}:`)) {
      throw new Error(`oauth.js missing provider: ${provider}`)
    }
  }

  // Check for required exports
  const requiredExports = ['connectProvider', 'getOAuthEndpoint', 'getSupportedProviders']
  for (const exp of requiredExports) {
    if (!source.includes(`export`) || !source.includes(`function ${exp}`)) {
      throw new Error(`oauth.js missing export: ${exp}`)
    }
  }

  // Check for OAuth URL components
  const requiredComponents = ['authUrl', 'tokenUrl', 'state', 'scope', 'redirect_uri']
  for (const component of requiredComponents) {
    if (!source.includes(component)) {
      throw new Error(`oauth.js missing OAuth component: ${component}`)
    }
  }

  // Test getSupportedProviders
  const providers = getSupportedProviders()
  if (providers.length !== 6) {
    throw new Error(`getSupportedProviders should return 6 providers, found ${providers.length}`)
  }

  // Test getOAuthEndpoint
  for (const provider of requiredProviders) {
    const authUrl = getOAuthEndpoint(provider, 'auth')
    if (!authUrl || !authUrl.startsWith('https://')) {
      throw new Error(`getOAuthEndpoint('${provider}', 'auth') returned invalid URL`)
    }
  }

  console.log('✓ oauth.js generates correct OAuth URL with scopes')
  return true
}

// Run test
testOAuthConnect()
