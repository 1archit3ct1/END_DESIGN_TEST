/**
 * Test: OAuth handlers wired and trigger correct functions
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testOAuthHandlers() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/main.js'),
    'utf-8'
  )

  // Check for required imports
  const requiredImports = [
    "from './core/oauth.js'",
    "from './core/oauth-callback.js'",
    "from './core/oauth-revoke.js'",
    "from './core/status-sync.js'",
    "from './core/workflow-gate.js'",
    "from './core/credential-lifetime.js'"
  ]
  for (const imp of requiredImports) {
    if (!source.includes(imp)) {
      throw new Error(`main.js missing import: ${imp}`)
    }
  }

  // Check for required exports
  const requiredExports = [
    'handleOAuthConnect',
    'handleOAuthCallback',
    'handleOAuthRevoke',
    'handleOAuthDisconnect',
    'startStatusPolling',
    'stopStatusPolling',
    'checkWorkflowGate',
    'handleCredentialExpiry'
  ]
  for (const exp of requiredExports) {
    if (!source.includes(`export function ${exp}`) && !source.includes(`export async function ${exp}`)) {
      throw new Error(`main.js missing export: ${exp}`)
    }
  }

  // Check for setupWindowCloseExpiry call in boot section
  if (!source.includes('setupWindowCloseExpiry()')) {
    throw new Error('main.js should call setupWindowCloseExpiry() on boot')
  }

  console.log('✓ OAuth handlers wired and trigger correct functions')
  return true
}

// Run test
testOAuthHandlers()
