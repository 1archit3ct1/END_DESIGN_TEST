#!/usr/bin/env node
/**
 * CLI Extract — extracts tasks from HTML or image files.
 * Usage: node src/cli/extract.js <file> [--out ./output]
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { universalIntake, generateExtractionSummary } from '../core/universal-intake.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const args = process.argv.slice(2)
const inputFile = args.find(a => !a.startsWith('--'))
const outFlag = args.find(a => a.startsWith('--out='))?.split('=')[1] || './output'

if (!inputFile) {
  console.error(`
Usage: node src/cli/extract.js <file> [--out=./output]

Supported formats:
  - HTML files (.html, .htm) — extracts data-key attributes
  - Images (.png, .jpg, .gif) — uses LLaVA vision model
  - Text specs (.md, .txt) — uses heuristic parser

Examples:
  node src/cli/extract.js gui_status.html
  node src/cli/extract.js screenshot.png --out=./extraction
  node src/cli/extract.js design.md
`)
  process.exit(1)
}

async function run() {
  console.log(`\n🔍 Extracting from: ${inputFile}`)

  try {
    // Run universal intake
    const result = await universalIntake(inputFile)

    // Generate summary
    const summary = generateExtractionSummary(result)

    // Create output directory
    fs.mkdirSync(outFlag, { recursive: true })

    // Write extraction.json
    const extractionPath = path.join(outFlag, 'extraction.json')
    const extractionData = {
      ...summary,
      items: result.items,
      steps: result.steps,
      layers: result.layers
    }
    fs.writeFileSync(extractionPath, JSON.stringify(extractionData, null, 2))
    console.log(`✓ Wrote ${extractionPath}`)

    // Write operator_overrides.json (for manual review)
    const overridesPath = path.join(outFlag, 'operator_overrides.json')
    const overridesData = {
      version: '1.0',
      reviewedAt: null,
      overrides: [],
      notes: 'Review extracted items and add overrides as needed'
    }
    fs.writeFileSync(overridesPath, JSON.stringify(overridesData, null, 2))
    console.log(`✓ Wrote ${overridesPath}`)

    // Write projection_graph.json
    const graphPath = path.join(outFlag, 'projection_graph.json')
    const graphData = buildProjectionGraph(result.layers)
    fs.writeFileSync(graphPath, JSON.stringify(graphData, null, 2))
    console.log(`✓ Wrote ${graphPath}`)

    // Print summary
    console.log(`\n📊 Extraction Summary:`)
    console.log(`   Input Type: ${result.inputType}`)
    console.log(`   Parser: ${result.parser}`)
    console.log(`   Total Items: ${result.totalItems}`)
    console.log(`   Total Steps: ${result.totalSteps}`)
    console.log(`   Confidence: ${(summary.confidence * 100).toFixed(0)}%`)
    console.log(`\n✅ Extraction complete. Output in ${outFlag}/`)

  } catch (error) {
    console.error(`\n❌ Extraction error: ${error.message}`)
    console.error(error.stack)
    process.exit(1)
  }
}

/**
 * Build projection graph from layers.
 */
function buildProjectionGraph(layers) {
  const nodes = []
  const edges = []
  let nodeId = 0

  layers.forEach((layer, layerIndex) => {
    layer.nodes.forEach(node => {
      nodes.push({
        id: `P${String(nodeId).padStart(2, '0')}`,
        label: node.name,
        kind: node.type,
        layer: layer.label,
        status: 'red',
        confidence: 0.9,
        source_id: node.id,
        description: node.desc || ''
      })

      // Link to previous node
      if (nodeId > 0) {
        edges.push({
          from: `P${String(nodeId - 1).padStart(2, '0')}`,
          to: `P${String(nodeId).padStart(2, '0')}`,
          type: 'sequential'
        })
      }

      nodeId++
    })
  })

  return {
    version: '1.0',
    generated: new Date().toISOString(),
    nodes,
    edges,
    totalNodes: nodes.length,
    totalEdges: edges.length,
    status: 'conformance_pending'
  }
}

run()
