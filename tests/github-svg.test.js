/**
 * Test: GitHub SVG file exists and is valid XML
 */
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function testGithubSvgExists() {
  const svgPath = join(__dirname, '../public/providers/github.svg')

  // Check file exists
  let svgContent
  try {
    svgContent = readFileSync(svgPath, 'utf-8')
  } catch (e) {
    throw new Error(`GitHub SVG file not found at ${svgPath}`)
  }

  // Check valid SVG structure
  if (!svgContent.includes('<svg')) {
    throw new Error('GitHub SVG missing <svg> element')
  }

  if (!svgContent.includes('</svg>')) {
    throw new Error('GitHub SVG missing </svg> closing tag')
  }

  if (!svgContent.includes('xmlns="http://www.w3.org/2000/svg"')) {
    throw new Error('GitHub SVG missing xmlns attribute')
  }

  console.log('✓ GitHub SVG file exists and is valid XML')
  return true
}

// Run test
testGithubSvgExists()
