/**
 * Test: html-dom-parser.js extracts data-key attributes from HTML
 */
import { parseHTMLDOM, itemsToDAGLayers } from '../src/core/html-dom-parser.js'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testHTMLDOMParser() {
  // Read source file and validate structure
  const source = readFileSync(
    join(__dirname, '../src/core/html-dom-parser.js'),
    'utf-8'
  )

  // Check for required exports
  const requiredExports = ['parseHTMLDOM', 'itemsToDAGLayers']
  for (const exp of requiredExports) {
    if (!source.includes(`export function ${exp}`)) {
      throw new Error(`html-dom-parser.js missing export: ${exp}`)
    }
  }

  // Check for required functionality
  const requiredComponents = [
    'data-key',
    'rust-note',
    'step-panel',
    'data-step',
    'regex'
  ]
  for (const component of requiredComponents) {
    if (!source.includes(component)) {
      throw new Error(`html-dom-parser.js missing: ${component}`)
    }
  }

  // Test with sample HTML
  const sampleHTML = `
    <html>
      <body>
        <div class="step-panel" data-step="step1">
          <h2 class="step-title">Connect Tools</h2>
          <div data-key="step1_connect.github_oauth2">
            <span class="name">GitHub OAuth</span>
            <div class="rust-note">GitHub OAuth2 flow implementation</div>
          </div>
          <div data-key="step1_connect.slack_oauth2">
            <span class="name">Slack OAuth</span>
            <div class="rust-note">Slack OAuth integration</div>
          </div>
        </div>
        <div class="step-panel" data-step="step2">
          <h2 class="step-title">Verify Prerequisites</h2>
          <div data-key="step2_verify.repo_check">
            <span class="name">Repo Check</span>
            <div class="rust-note">Verify repository structure</div>
          </div>
        </div>
        <div data-key="rust_backend.pkce_rfc7636">
          <span class="name">PKCE Implementation</span>
          <div class="rust-note">RFC 7636 PKCE SHA256 + base64url</div>
        </div>
      </body>
    </html>
  `

  const result = parseHTMLDOM(sampleHTML)

  // Validate extraction
  if (result.totalItems < 3) {
    throw new Error(`Expected at least 3 items, found ${result.totalItems}`)
  }

  // Check specific items extracted
  const hasGithub = result.items.some(i => i.id.includes('github_oauth2'))
  if (!hasGithub) {
    throw new Error('Failed to extract GitHub OAuth item')
  }

  const hasPkce = result.items.some(i => i.id.includes('pkce_rfc7636'))
  if (!hasPkce) {
    throw new Error('Failed to extract PKCE item')
  }

  // Test itemsToDAGLayers
  const layers = itemsToDAGLayers(result.items)
  if (!Array.isArray(layers) || layers.length === 0) {
    throw new Error('itemsToDAGLayers should return array of layers')
  }

  console.log('✓ html-dom-parser.js extracts data-key attributes from HTML')
  return true
}

// Run test
testHTMLDOMParser()
