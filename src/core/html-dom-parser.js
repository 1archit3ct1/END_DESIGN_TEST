/**
 * HTML DOM Parser — extracts data-key attributes and semantic structure.
 * Works in both browser and Node.js environments.
 */

/**
 * Parse HTML string and extract semantic elements.
 */
export function parseHTMLDOM(htmlString) {
  const items = []
  const steps = []

  // Extract data-key attributes using regex (works in Node.js and browser)
  const dataKeyRegex = /data-key=["']([^"']+)["']/gi
  const rustNoteRegex = /class=["'][^"']*rust-note[^"']*["'][^>]*>([^<]*)/gi
  const stepPanelRegex = /class=["'][^"']*(?:step-panel|step[-_])[^"']*["']/gi
  const dataStepRegex = /data-step=["']([^"']+)["']/gi

  let dataKeyMatch
  while ((dataKeyMatch = dataKeyRegex.exec(htmlString)) !== null) {
    const dataKey = dataKeyMatch[1]
    const matchStart = dataKeyMatch.index

    // Find surrounding context (200 chars before and after)
    const contextStart = Math.max(0, matchStart - 200)
    const contextEnd = Math.min(htmlString.length, matchStart + 500)
    const context = htmlString.substring(contextStart, contextEnd)

    // Extract name from element
    const nameMatch = context.match(/>([^<]{0,50}?)(?:<|&)/i)
    const name = nameMatch ? nameMatch[1].trim() : dataKey

    // Extract rust-note
    const rustNoteMatch = context.match(/class=["'][^"']*rust-note[^"']*["'][^>]*>([^<]*)/i)
    const rustNote = rustNoteMatch ? rustNoteMatch[1].trim() : ''

    // Extract step info
    const stepMatch = context.match(/data-step=["']([^"']+)["']/i) ||
      context.match(/class=["'][^"']*(step[-_]?\d+)[^"']*["']/i)
    const stepId = stepMatch ? (stepMatch[1] || `step${stepMatch[2]}`) : 'unknown'

    items.push({
      id: dataKey,
      name,
      description: rustNote,
      step: stepId,
      type: getItemType(dataKey),
      element: 'div'
    })
  }

  // Extract step panels
  const stepMatches = htmlString.matchAll(/<[^>]*(?:step-panel|step[-_]|data-step)[^>]*>([\s\S]*?)<\/[^>]*>/gi)
  for (const match of stepMatches) {
    const panelContent = match[1]
    const stepIdMatch = panelContent.match(/data-step=["']([^"']+)["']/i)
    const titleMatch = panelContent.match(/<(?:h[1-6]|span)[^>]*class=["'][^"']*(?:step-title|title)[^"']*["'][^>]*>([^<]*)/i)

    const stepId = stepIdMatch ? stepIdMatch[1] : ''
    const stepTitle = titleMatch ? titleMatch[1].trim() : ''

    if (stepId || stepTitle) {
      // Count artifacts in this step
      const artifactMatches = panelContent.matchAll(/class=["'][^"']*(?:artifact|btn)[^"']*["']/gi)
      const artifacts = Array.from(artifactMatches).map(m => ({
        class: m[0]
      }))

      steps.push({
        id: stepId || slugify(stepTitle),
        title: stepTitle,
        artifactCount: artifacts.length,
        artifacts
      })
    }
  }

  return { items, steps, totalItems: items.length, totalSteps: steps.length }
}

/**
 * Determine item type from data-key pattern.
 */
export function getItemType(dataKey) {
  if (dataKey.includes('rust_backend')) return 'backend'
  if (dataKey.includes('oauth_integration')) return 'integration'
  if (dataKey.includes('step1')) return 'step1'
  if (dataKey.includes('step2')) return 'step2'
  if (dataKey.includes('step3')) return 'step3'
  if (dataKey.includes('step4')) return 'step4'
  if (dataKey.includes('step5')) return 'step5'
  if (dataKey.includes('step6')) return 'step6'
  return 'general'
}

/**
 * Slugify string for IDs.
 */
function slugify(str) {
  return str.toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '')
    .substring(0, 50)
}

/**
 * Convert extracted items to DAG layers format.
 */
export function itemsToDAGLayers(items) {
  const grouped = {}

  items.forEach(item => {
    const layer = item.type || 'general'
    if (!grouped[layer]) grouped[layer] = []
    grouped[layer].push({
      id: item.id,
      name: item.name,
      type: 'fn',
      desc: item.description,
      layer,
      edges: []
    })
  })

  return Object.entries(grouped).map(([label, nodes]) => ({
    label: humanizeLayer(label),
    nodes
  }))
}

function humanizeLayer(layer) {
  const map = {
    backend: 'Backend / Rust',
    integration: 'OAuth Integrations',
    step1: 'Step 1: Connect',
    step2: 'Step 2: Verify',
    step3: 'Step 3: Workflow',
    step4: 'Step 4: ROI',
    step5: 'Step 5: Entitlement',
    step6: 'Step 6: Scaffold',
    general: 'General Tasks'
  }
  return map[layer] || layer
}
