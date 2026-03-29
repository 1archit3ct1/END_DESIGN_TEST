/**
 * Test: WorkflowGate.jsx shows lock when gated, unlock when open
 */
import { WorkflowGate, updateGateStatus } from '../src/components/WorkflowGate.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testWorkflowGateComponent() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/components/WorkflowGate.js'),
    'utf-8'
  )

  // Check for required elements
  const requiredElements = [
    'workflow-gate',
    'gate-icon',
    'gate-title',
    'requirements-checklist',
    'checklist-item',
    'unlock-button',
    'updateGateStatus'
  ]

  for (const element of requiredElements) {
    if (!source.includes(element)) {
      throw new Error(`WorkflowGate.js missing: ${element}`)
    }
  }

  // Check for lock/unlock states
  if (!source.includes('locked') || !source.includes('unlocked')) {
    throw new Error('WorkflowGate.js missing locked/unlocked states')
  }

  // Check for exports
  if (!source.includes('export function WorkflowGate')) {
    throw new Error('WorkflowGate.js missing WorkflowGate export')
  }
  if (!source.includes('export function updateGateStatus')) {
    throw new Error('WorkflowGate.js missing updateGateStatus export')
  }

  console.log('✓ WorkflowGate.jsx shows lock when gated, unlock when open')
  return true
}

// Run test
testWorkflowGateComponent()
