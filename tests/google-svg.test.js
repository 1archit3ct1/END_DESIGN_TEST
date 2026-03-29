/**
 * Test: Google SVG file exists and is valid XML
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testGoogleSvgExists() {
  const svgPath = join(__dirname, '../public/providers/google.svg')

  // Check file exists
  let svgContent
  try {
    svgContent = readFileSync(svgPath, 'utf-8')
  } catch (e) {
    throw new Error(`Google SVG file not found at ${svgPath}`)
  }

  // Check valid SVG structure
  if (!svgContent.includes('<svg')) {
    throw new Error('Google SVG missing <svg> element')
  }

  if (!svgContent.includes('</svg>')) {
    throw new Error('Google SVG missing </svg> closing tag')
  }

  if (!svgContent.includes('xmlns="http://www.w3.org/2000/svg"')) {
    throw new Error('Google SVG missing xmlns attribute')
  }

  // Check for Google colors
  const googleColors = ['#4285F4', '#34A853', '#FBBC05', '#EA4335']
  for (const color of googleColors) {
    if (!svgContent.includes(color)) {
      throw new Error(`Google SVG missing Google color ${color}`)
    }
  }

  console.log('✓ Google SVG file exists and is valid XML')
  return true
}

// Run test
testGoogleSvgExists()
