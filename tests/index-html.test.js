/**
 * Test: index.html contains OAuth redirect meta tags
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testIndexHtmlOAuthMeta() {
  const htmlPath = join(__dirname, '../index.html')
  
  let htmlContent
  try {
    htmlContent = readFileSync(htmlPath, 'utf-8')
  } catch (e) {
    throw new Error(`index.html not found at ${htmlPath}`)
  }

  // Check for OAuth redirect meta tags
  const requiredMeta = [
    'oauth-redirect-uri',
    '/oauth/callback',
    'oauth-providers',
    'google',
    'github',
    'twitter',
    'instagram',
    'discord',
    'meta'
  ]

  for (const meta of requiredMeta) {
    if (!htmlContent.includes(meta)) {
      throw new Error(`index.html missing OAuth meta: ${meta}`)
    }
  }

  console.log('✓ index.html contains OAuth redirect meta tags')
  return true
}

// Run test
testIndexHtmlOAuthMeta()
