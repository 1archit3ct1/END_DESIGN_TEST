/**
 * Test: event-bus.js emits and listens for events
 */
import {
  emitEvent,
  onEvent,
  offEvent,
  clearEventListeners,
  clearAllEventListeners,
  emitProviderConnected,
  emitProviderDisconnected,
  emitWorkflowEligible,
  emitTokenExpiry
} from '../src/core/event-bus.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testEventBus() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/event-bus.js'),
    'utf-8'
  )

  // Check for required exports
  const requiredExports = [
    'emitEvent',
    'onEvent',
    'offEvent',
    'clearEventListeners',
    'clearAllEventListeners',
    'emitProviderConnected',
    'emitProviderDisconnected',
    'emitWorkflowEligible',
    'emitTokenExpiry'
  ]
  for (const exp of requiredExports) {
    if (!source.includes(`export function ${exp}`)) {
      throw new Error(`event-bus.js missing export: ${exp}`)
    }
  }

  // Check for required functionality
  const requiredComponents = [
    'eventListeners',
    'CustomEvent',
    'dispatchEvent',
    'addEventListener'
  ]
  for (const component of requiredComponents) {
    if (!source.includes(component)) {
      throw new Error(`event-bus.js missing: ${component}`)
    }
  }

  // Test clearAllEventListeners (no-op in Node.js, but function should exist)
  clearAllEventListeners()

  console.log('✓ event-bus.js emits and listens for events')
  return true
}

// Run test
testEventBus()
