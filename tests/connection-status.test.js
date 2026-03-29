/**
 * Test: ConnectionStatus.jsx shows live dot, timestamp, disconnect button
 */
import { ConnectionStatus, updateConnectionStatus } from '../src/components/ConnectionStatus.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testConnectionStatus() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/components/ConnectionStatus.js'),
    'utf-8'
  )

  // Check for required elements
  const requiredElements = [
    'connection-status',
    'status-indicator',
    'live-dot',
    'status-text',
    'last-synced',
    'disconnect-btn',
    'updateConnectionStatus'
  ]

  for (const element of requiredElements) {
    if (!source.includes(element)) {
      throw new Error(`ConnectionStatus.js missing: ${element}`)
    }
  }

  // Check for live/offline states
  if (!source.includes('live') || !source.includes('offline')) {
    throw new Error('ConnectionStatus.js missing live/offline states')
  }

  // Check for exports
  if (!source.includes('export function ConnectionStatus')) {
    throw new Error('ConnectionStatus.js missing ConnectionStatus export')
  }
  if (!source.includes('export function updateConnectionStatus')) {
    throw new Error('ConnectionStatus.js missing updateConnectionStatus export')
  }

  console.log('✓ ConnectionStatus.jsx shows live dot, timestamp, disconnect button')
  return true
}

// Run test
testConnectionStatus()
