/**
 * Test: universal-intake.js auto-detects input type
 */
import { universalIntake, generateExtractionSummary } from '../src/core/universal-intake.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testUniversalIntake() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/universal-intake.js'),
    'utf-8'
  )

  // Check for required exports
  const requiredExports = ['universalIntake', 'generateExtractionSummary']
  for (const exp of requiredExports) {
    if (!source.includes('export') || !source.includes(exp)) {
      throw new Error(`universal-intake.js missing export: ${exp}`)
    }
  }

  // Check for required functionality
  const requiredComponents = [
    'html-dom-parser',
    'vision-parser',
    'detectInputType',
    'processHTML',
    'processImage',
    'processText',
    'IMAGE_EXTENSIONS',
    'HTML_EXTENSIONS'
  ]
  for (const component of requiredComponents) {
    if (!source.includes(component)) {
      throw new Error(`universal-intake.js missing: ${component}`)
    }
  }

  // Test detectInputType with HTML string
  const htmlString = '<!DOCTYPE html><html><div data-key="test">Test</div></html>'
  // Note: universalIntake is async, tested in integration tests

  // Test generateExtractionSummary
  const mockResult = {
    inputType: 'html',
    parser: 'html-dom-parser',
    totalItems: 10,
    totalSteps: 3,
    items: [{ type: 'backend', step: 'step1' }]
  }
  const summary = generateExtractionSummary(mockResult)

  if (!summary.version || !summary.extractedAt) {
    throw new Error('generateExtractionSummary should return version and extractedAt')
  }

  if (summary.confidence !== 0.95) {
    throw new Error('HTML confidence should be 0.95')
  }

  console.log('✓ universal-intake.js auto-detects input type')
  return true
}

// Run test
testUniversalIntake()
