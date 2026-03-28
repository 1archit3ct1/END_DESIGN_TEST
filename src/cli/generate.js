#!/usr/bin/env node
// cli/generate.js — generate scaffold artifacts from a dag.json
// Usage: node src/cli/generate.js <dag.json> [--target full|react|prompt|dag_json|task_json] [--out ./output]

import fs from 'fs'
import path from 'path'
import { generateComponents } from '../core/generator.js'

const args = process.argv.slice(2)
const inputFile = args.find(a => !a.startsWith('--'))
const targetFlag = args.find(a => a.startsWith('--target='))?.split('=')[1] || 'full'
const outFlag = args.find(a => a.startsWith('--out='))?.split('=')[1] || './output'

if (!inputFile) {
  console.error('Usage: node src/cli/generate.js <dag.json> [--target=full|react|prompt|dag_json|task_json] [--out=./output]')
  process.exit(1)
}

const dagData = JSON.parse(fs.readFileSync(inputFile, 'utf-8'))

// Support both flat nodes[] and layered { layers[] } formats
let layers = dagData.layers
if (!layers && dagData.nodes) {
  const grouped = {}
  for (const n of dagData.nodes) {
    const l = n.layer || n.type || 'fn'
    if (!grouped[l]) grouped[l] = []
    grouped[l].push(n)
  }
  layers = Object.entries(grouped).map(([label, nodes]) => ({ label, nodes }))
}

if (!layers || !layers.length) {
  console.error('No layers found in DAG file')
  process.exit(1)
}

const components = generateComponents(layers, targetFlag)

fs.mkdirSync(outFlag, { recursive: true })

for (const c of components) {
  if (!c.raw) continue
  const outPath = path.join(outFlag, c.title)
  fs.writeFileSync(outPath, c.raw)
  console.log(`✓ Generated ${outPath}`)
}

console.log(`\n✓ Done. ${components.length} artifacts written to ${outFlag}/`)
