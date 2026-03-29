/**
 * Test: oauth.css contains styles for all OAuth components
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testOAuthCss() {
  const cssPath = join(__dirname, '../src/styles/oauth.css')
  
  let cssContent
  try {
    cssContent = readFileSync(cssPath, 'utf-8')
  } catch (e) {
    throw new Error(`oauth.css not found at ${cssPath}`)
  }

  // Check for required component styles
  const requiredSelectors = [
    '.provider-grid',
    '.provider-card',
    '.scope-selector',
    '.workflow-gate',
    '.connection-status',
    '.live-dot',
    '.connect-button',
    '.disconnect-button',
    '.unlock-button',
    '.checklist-item'
  ]

  for (const selector of requiredSelectors) {
    if (!cssContent.includes(selector)) {
      throw new Error(`oauth.css missing selector: ${selector}`)
    }
  }

  // Check for required CSS features
  const requiredFeatures = [
    'display: grid',
    'flex',
    'border-radius',
    'transition',
    '@keyframes'
  ]

  for (const feature of requiredFeatures) {
    if (!cssContent.includes(feature)) {
      throw new Error(`oauth.css missing feature: ${feature}`)
    }
  }

  console.log('✓ oauth.css contains styles for all OAuth components')
  return true
}

// Run test
testOAuthCss()
