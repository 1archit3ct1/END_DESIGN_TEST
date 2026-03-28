// exporter.js — downloads generated artifacts to disk

/**
 * Download a single text file.
 */
export function downloadText(filename, content) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  triggerDownload(blob, filename)
}

/**
 * Download a JSON object as a .json file.
 */
export function downloadJSON(filename, obj) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: 'application/json' })
  triggerDownload(blob, filename)
}

/**
 * Download all artifacts as a flat bundle (individual files, no zip dep needed).
 * In a real deployment you'd use JSZip here. For now, downloads each file individually.
 */
export function downloadBundle(components, layers) {
  const allNodes = layers.flatMap(l => l.nodes)

  // Download each artifact with a staggered delay so browser doesn't block
  components.forEach((c, i) => {
    if (!c.raw) return
    setTimeout(() => downloadText(c.title, c.raw), i * 300)
  })

  // Also always emit dag.json and task_status.json
  const hasDAG = components.some(c => c.type === 'dag')
  const hasTask = components.some(c => c.type === 'status')

  if (!hasDAG) {
    setTimeout(() => downloadJSON('dag.json', {
      version: '1.0',
      generated: new Date().toISOString(),
      nodes: allNodes,
    }), components.length * 300)
  }

  if (!hasTask) {
    const fnNodes = allNodes.filter(n => n.type === 'fn')
    const root = allNodes.find(n => n.type === 'root') || { id: 'root', name: 'SystemRoot' }
    setTimeout(() => downloadJSON('task_status.json', {
      version: '1.0',
      generated: new Date().toISOString(),
      meta: { root: root.id, rootName: root.name, loopActive: false, completedAt: null },
      tasks: fnNodes.map(n => ({ id: n.id, name: n.name, status: 'pending', hash: null, retries: 0, result: null })),
    }), (components.length + 1) * 300)
  }
}

/**
 * Copy text to clipboard.
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    return false
  }
}

// ── INTERNAL ─────────────────────────────────────────────────────────
function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
