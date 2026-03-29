/**
 * Vision Parser — sends screenshots/images to LLaVA for semantic extraction.
 * Uses Ollama's LLaVA multimodal model to read UI elements from images.
 */

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434'
const OLLAMA_VISION_MODEL = process.env.OLLAMA_VISION_MODEL || 'llava:7b'

/**
 * Extract UI elements from image using LLaVA.
 */
export async function parseImageWithVision(imagePath) {
  const imageBuffer = await readFileAsBase64(imagePath)

  const prompt = `Analyze this UI screenshot and extract all functional elements. For each element, identify:
1. The element's purpose (button, input, panel, etc.)
2. Any visible text labels
3. Any data attributes or identifiers (like data-key, id, class names)
4. The step or section it belongs to

Format the output as JSON with this structure:
{
  "elements": [
    {
      "type": "button|input|panel|card|etc",
      "label": "visible text",
      "identifier": "any data-key or id found",
      "step": "step1|step2|etc or unknown",
      "description": "what this element does"
    }
  ],
  "steps": ["step1 title", "step2 title"],
  "totalElements": count
}

Be precise. If you see data-key attributes, extract them exactly as written.
If you see rust-note or description text next to elements, include it.`

  const response = await fetch(`${OLLAMA_HOST}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: OLLAMA_VISION_MODEL,
      prompt: prompt,
      images: [imageBuffer],
      stream: false
    })
  })

  if (!response.ok) {
    throw new Error(`Vision API error: ${response.statusText}`)
  }

  const data = await response.json()
  const extracted = parseVisionResponse(data.response)

  return {
    items: extracted.elements || [],
    steps: extracted.steps || [],
    totalItems: extracted.totalElements || 0,
    source: 'vision',
    model: OLLAMA_VISION_MODEL
  }
}

/**
 * Parse LLaVA response text into structured data.
 */
function parseVisionResponse(responseText) {
  try {
    // Try to extract JSON from response
    const jsonMatch = responseText.match(/\{[\s\S]*\}/)
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0])
    }
  } catch (e) {
    console.warn('Failed to parse vision response as JSON, using fallback')
  }

  // Fallback: extract key patterns from text
  const elements = []
  const lines = responseText.split('\n')

  for (const line of lines) {
    if (line.includes('data-key') || line.includes('-') || line.match(/^\d+\./)) {
      elements.push({
        type: 'extracted',
        label: line.trim(),
        identifier: extractIdentifier(line),
        step: extractStep(line),
        description: line.trim()
      })
    }
  }

  return {
    elements,
    steps: [],
    totalElements: elements.length
  }
}

/**
 * Extract identifier from text line.
 */
function extractIdentifier(line) {
  const match = line.match(/data-key["']?\s*[:=]\s*["']?([a-zA-Z0-9_.]+)/i)
  return match ? match[1] : slugify(line.substring(0, 30))
}

/**
 * Extract step from text line.
 */
function extractStep(line) {
  const match = line.match(/step[-_]?(\d+)/i)
  return match ? `step${match[1]}` : 'unknown'
}

/**
 * Read file as base64 string.
 */
async function readFileAsBase64(path) {
  // Browser environment
  if (typeof window !== 'undefined') {
    const response = await fetch(path)
    const blob = await response.blob()
    return await blobToBase64(blob)
  }

  // Node.js environment
  const { readFileSync } = await import('fs')
  const buffer = readFileSync(path)
  return buffer.toString('base64')
}

/**
 * Convert blob to base64.
 */
function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result.split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

/**
 * Slugify string.
 */
function slugify(str) {
  return str.toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '')
    .substring(0, 30)
}

/**
 * Convert vision-extracted items to DAG layers.
 */
export function visionItemsToDAGLayers(items) {
  const grouped = {}

  items.forEach(item => {
    const layer = item.step || 'general'
    if (!grouped[layer]) grouped[layer] = []
    grouped[layer].push({
      id: item.identifier || slugify(item.label),
      name: item.label,
      type: 'fn',
      desc: item.description || '',
      layer,
      edges: []
    })
  })

  return Object.entries(grouped).map(([label, nodes]) => ({
    label: label.replace(/_/g, ' ').toUpperCase(),
    nodes
  }))
}
