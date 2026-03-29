/**
 * Universal Intake — routes input to DOM or Vision parser based on file type.
 * Supports: HTML files, images (PNG, JPG, GIF), and text specs.
 */

import { parseHTMLDOM, itemsToDAGLayers as htmlToDAG } from './html-dom-parser.js'
import { parseImageWithVision, visionItemsToDAGLayers } from './vision-parser.js'

const IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp']
const HTML_EXTENSIONS = ['html', 'htm']

/**
 * Auto-detect input type and route to appropriate parser.
 */
export async function universalIntake(inputSource) {
  const inputType = detectInputType(inputSource)

  switch (inputType) {
    case 'html':
      return processHTML(inputSource)
    case 'image':
      return processImage(inputSource)
    case 'text':
      return processText(inputSource)
    default:
      throw new Error(`Unknown input type: ${inputType}`)
  }
}

/**
 * Detect input type from source.
 */
function detectInputType(source) {
  // Check if it's a file path
  if (typeof source === 'string' && (source.includes('/') || source.includes('\\') || source.includes('.'))) {
    const ext = getFileExtension(source)

    if (IMAGE_EXTENSIONS.includes(ext)) return 'image'
    if (HTML_EXTENSIONS.includes(ext)) return 'html'
  }

  // Check if it's HTML content
  if (typeof source === 'string' && source.trim().startsWith('<')) {
    if (source.includes('<!DOCTYPE') || source.includes('<html') || source.includes('<!doctype')) {
      return 'html'
    }
  }

  // Check if it's an image blob/buffer
  if (source instanceof Blob || source instanceof ArrayBuffer) {
    return 'image'
  }

  // Default to text
  return 'text'
}

/**
 * Process HTML file or string.
 */
async function processHTML(source) {
  let htmlContent

  if (typeof source === 'string' && source.startsWith('<')) {
    htmlContent = source
  } else {
    // Read file
    if (typeof window !== 'undefined') {
      const response = await fetch(source)
      htmlContent = await response.text()
    } else {
      const { readFileSync } = await import('fs')
      htmlContent = readFileSync(source, 'utf-8')
    }
  }

  const result = parseHTMLDOM(htmlContent)
  const layers = htmlToDAG(result.items)

  return {
    ...result,
    layers,
    inputType: 'html',
    parser: 'html-dom-parser'
  }
}

/**
 * Process image file.
 */
async function processImage(source) {
  const result = await parseImageWithVision(source)
  const layers = visionItemsToDAGLayers(result.items)

  return {
    ...result,
    layers,
    inputType: 'image',
    parser: 'vision-parser'
  }
}

/**
 * Process text spec (fallback).
 */
async function processText(source) {
  // Import the text parser dynamically
  const { parseDesignToDAG } = await import('./parser.js')

  let textContent
  if (typeof source === 'string' && source.startsWith('<')) {
    textContent = source
  } else {
    // Read file
    if (typeof window !== 'undefined') {
      const response = await fetch(source)
      textContent = await response.text()
    } else {
      const { readFileSync } = await import('fs')
      textContent = readFileSync(source, 'utf-8')
    }
  }

  const layers = parseDesignToDAG(textContent, 'freeform')
  const allNodes = layers.flatMap(l => l.nodes)

  return {
    items: allNodes,
    steps: [],
    totalItems: allNodes.length,
    totalSteps: 0,
    layers,
    inputType: 'text',
    parser: 'parser.js'
  }
}

/**
 * Get file extension from path.
 */
function getFileExtension(filePath) {
  const match = filePath.match(/\.([a-zA-Z0-9]+)$/)
  return match ? match[1].toLowerCase() : ''
}

/**
 * Generate extraction summary.
 */
export function generateExtractionSummary(result) {
  return {
    version: '1.0',
    extractedAt: new Date().toISOString(),
    source: {
      type: result.inputType,
      parser: result.parser
    },
    statistics: {
      totalItems: result.totalItems,
      totalSteps: result.totalSteps,
      itemsByType: groupByType(result.items),
      itemsByStep: groupByStep(result.items)
    },
    confidence: calculateConfidence(result)
  }
}

function groupByType(items) {
  return items.reduce((acc, item) => {
    const type = item.type || 'unknown'
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {})
}

function groupByStep(items) {
  return items.reduce((acc, item) => {
    const step = item.step || 'unknown'
    acc[step] = (acc[step] || 0) + 1
    return acc
  }, {})
}

function calculateConfidence(result) {
  // Higher confidence for DOM parsing (exact data extraction)
  // Lower confidence for vision (OCR + interpretation)
  if (result.inputType === 'html') return 0.95
  if (result.inputType === 'image') return 0.75
  return 0.85
}
