// parser.js — converts design specs into layered DAGs
// Supports: HTML (data-key), JSON DAG, freeform text, markdown, UI descriptions

import { parseHTMLDOM, itemsToDAGLayers } from './html-dom-parser.js'

/**
 * Top-level entry. Returns an array of layers, each with { label, nodes[] }.
 * Layers ordered: UI → Functions → I/O → Root (root at bottom of visual stack).
 */
export function parseDesignToDAG(text, type = 'freeform') {
  if (!text || !text.trim()) return []

  // Detect HTML and use DOM parser
  if (isHTML(text)) {
    return parseHTMLWithDOM(text)
  }

  if (type === 'dag') {
    try {
      const parsed = JSON.parse(text)
      return buildFromJSONDAG(parsed)
    } catch (e) {
      // Fall through to heuristic parser
    }
  }

  return heuristicParse(text)
}

/**
 * Check if text is HTML.
 */
function isHTML(text) {
  const trimmed = text.trim()
  return trimmed.startsWith('<') && (
    trimmed.startsWith('<!DOCTYPE') ||
    trimmed.startsWith('<!doctype') ||
    trimmed.startsWith('<html') ||
    trimmed.includes('data-key=') ||
    trimmed.includes('<head>') ||
    trimmed.includes('<body>')
  )
}

/**
 * Parse HTML using DOM parser for data-key extraction.
 */
function parseHTMLWithDOM(text) {
  try {
    const result = parseHTMLDOM(text)
    if (result.items && result.items.length > 0) {
      return itemsToDAGLayers(result.items)
    }
  } catch (e) {
    console.warn('DOM parser failed, falling back to heuristic:', e.message)
  }
  // Fallback to heuristic if DOM parsing fails
  return heuristicParse(text)
}

// ── JSON DAG FORMAT ───────────────────────────────────────────────────
function buildFromJSONDAG(obj) {
  // Standard { nodes, edges } format
  if (obj.nodes && Array.isArray(obj.nodes)) {
    const grouped = {}
    for (const n of obj.nodes) {
      const layer = n.layer || n.type || 'fn'
      if (!grouped[layer]) grouped[layer] = []
      grouped[layer].push({
        id: n.id || slugify(n.name || n.label),
        name: n.label || n.name || n.id,
        type: n.type || 'fn',
        desc: n.desc || n.description || '',
        layer,
        edges: n.edges || [],
      })
    }
    return Object.entries(grouped).map(([label, nodes]) => ({ label: humanizeLayer(label), nodes }))
  }

  // Tree / nested object format
  return treeToLayers(obj)
}

function treeToLayers(obj, depth = 0) {
  const layers = []
  const rootKey = Object.keys(obj)[0]
  if (!rootKey) return layers

  layers.push({
    label: 'Root Capability',
    nodes: [{ id: 'root', name: rootKey, type: 'root', desc: '', layer: 'root', edges: [] }]
  })

  const children = obj[rootKey]
  if (children && typeof children === 'object') {
    const fnNodes = Object.keys(children).map(k => ({
      id: slugify(k),
      name: k,
      type: 'fn',
      desc: typeof children[k] === 'string' ? children[k] : '',
      layer: 'fn',
      edges: ['root'],
    }))
    if (fnNodes.length) layers.unshift({ label: 'Functions', nodes: fnNodes })
  }

  return layers
}

// ── HEURISTIC TEXT PARSER ─────────────────────────────────────────────
function heuristicParse(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)

  const uiNodes = []
  const fnNodes = []
  const ioNodes = []
  const seen = new Set()

  // Patterns
  const uiRx = /\[([^\]]+)\]/g
  const fnRx = /\b(parse|fetch|load|save|export|import|create|delete|update|select|filter|sort|auth|connect|emit|trigger|execute|resolve|compute|validate|redirect|check|sync|ingest|generate|map|register|invoke|dispatch)\b/gi
  const ioRx = /\b(api|endpoint|webhook|event|callback|token|credential|hash|json|csv|pdf|file|db|store|cache|log|trace|signal|status)\b/gi

  for (const line of lines) {
    // UI elements — bracket notation
    for (const m of line.matchAll(uiRx)) {
      const raw = m[1].trim()
      // Skip nested markers, short artifacts
      if (raw.length < 2 || raw.length > 60) continue
      // Handle "Label: sub, sub" — expand
      const parts = raw.split(/[,|>]/).map(s => s.trim()).filter(Boolean)
      for (const part of parts) {
        const id = `ui_${slugify(part)}`
        if (!seen.has(id) && uiNodes.length < 14) {
          seen.add(id)
          uiNodes.push({ id, name: part, type: 'ui', desc: `Surface element`, layer: 'ui', edges: [] })
        }
      }
    }

    // Function nodes from verbs
    for (const m of line.matchAll(fnRx)) {
      const verb = m[0].toLowerCase()
      // Get surrounding context (30 chars after)
      const ctx = line.substring(m.index, m.index + 50).trim()
      const id = `fn_${slugify(ctx.substring(0, 20))}`
      if (!seen.has(id) && fnNodes.length < 10) {
        seen.add(id)
        fnNodes.push({ id, name: capitalize(verb), type: 'fn', desc: ctx.substring(verb.length).trim().replace(/^[\s:\-→]+/, '').substring(0, 60), layer: 'fn', edges: [] })
      }
    }

    // I/O nodes
    for (const m of line.matchAll(ioRx)) {
      const word = m[0].toLowerCase()
      const id = `io_${word}`
      if (!seen.has(id) && ioNodes.length < 6) {
        seen.add(id)
        ioNodes.push({ id, name: word.toUpperCase(), type: 'io', desc: 'Data / transport boundary', layer: 'io', edges: [] })
      }
    }
  }

  // Root — first meaningful heading
  const headingLine = lines.find(l => /^(#|UI|Design|Workflow|Root|Screen|Flow|Trigger)/i.test(l))
  const rootName = headingLine
    ? headingLine.replace(/^[#\-\*\s]+/, '').substring(0, 50)
    : 'SystemRoot'

  const rootNode = { id: 'root', name: rootName, type: 'root', desc: 'Root capability — everything derives from here', layer: 'root', edges: [] }

  // Wire edges (UI → fn → io → root)
  uiNodes.forEach((n, i) => { n.edges = [fnNodes[i % fnNodes.length]?.id].filter(Boolean) })
  fnNodes.forEach((n, i) => { n.edges = [ioNodes[i % Math.max(ioNodes.length, 1)]?.id || 'root'] })
  ioNodes.forEach(n => { n.edges = ['root'] })

  const layers = []
  if (uiNodes.length) layers.push({ label: 'UI / Surface', nodes: uiNodes })
  if (fnNodes.length) layers.push({ label: 'Functions / Handlers', nodes: fnNodes })
  if (ioNodes.length) layers.push({ label: 'I/O / Boundaries', nodes: ioNodes })
  layers.push({ label: 'Root Capability', nodes: [rootNode] })

  return layers
}

// ── HELPERS ────────────────────────────────────────────────────────────
function slugify(str = '') {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '').substring(0, 30)
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

function humanizeLayer(layer) {
  const map = { ui: 'UI / Surface', fn: 'Functions / Handlers', io: 'I/O / Boundaries', root: 'Root Capability' }
  return map[layer] || layer
}
