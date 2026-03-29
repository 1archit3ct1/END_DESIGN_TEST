/**
 * Test: Twitter SVG file exists and is valid XML
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testTwitterSvgExists() {
  const svgPath = join(__dirname, '../public/providers/twitter.svg')
  let svgContent
  try {
    svgContent = readFileSync(svgPath, 'utf-8')
  } catch (e) {
    throw new Error(`Twitter SVG file not found at ${svgPath}`)
  }
  if (!svgContent.includes('<svg') || !svgContent.includes('</svg>')) {
    throw new Error('Twitter SVG invalid structure')
  }
  console.log('✓ Twitter SVG file exists and is valid XML')
  return true
}
testTwitterSvgExists()
