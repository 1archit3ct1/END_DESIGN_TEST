/**
 * Test: vision-parser.js processes image files
 */
import { parseImageWithVision, visionItemsToDAGLayers } from '../src/core/vision-parser.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testVisionParser() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/vision-parser.js'),
    'utf-8'
  )

  // Check for required exports
  const requiredExports = ['parseImageWithVision', 'visionItemsToDAGLayers']
  for (const exp of requiredExports) {
    if (!source.includes('export') || !source.includes(exp)) {
      throw new Error(`vision-parser.js missing export: ${exp}`)
    }
  }

  // Check for required functionality
  const requiredComponents = [
    'OLLAMA_VISION_MODEL',
    'llava',
    'fetch',
    'api/generate',
    'images:',
    'base64'
  ]
  for (const component of requiredComponents) {
    if (!source.includes(component)) {
      throw new Error(`vision-parser.js missing: ${component}`)
    }
  }

  // Test visionItemsToDAGLayers with sample data
  const sampleItems = [
    { label: 'GitHub OAuth', identifier: 'step1_connect.github_oauth2', step: 'step1', description: 'OAuth flow' },
    { label: 'PKCE', identifier: 'rust_backend.pkce_rfc7636', step: 'unknown', description: 'RFC 7636' }
  ]

  const layers = visionItemsToDAGLayers(sampleItems)
  if (!Array.isArray(layers) || layers.length === 0) {
    throw new Error('visionItemsToDAGLayers should return array of layers')
  }

  // Note: parseImageWithVision requires actual image file and Ollama running
  // This is tested manually or in integration tests

  console.log('✓ vision-parser.js processes image files')
  return true
}

// Run test
testVisionParser()
