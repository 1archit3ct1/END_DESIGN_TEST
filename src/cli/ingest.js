#!/usr/bin/env node
// cli/ingest.js — run EndDesign ingestor from command line
// Usage: node src/cli/ingest.js <input-file> [--type ui|dag|workflow|freeform] [--out ./output]

import fs from 'fs'
import path from 'path'
import { parseDesignToDAG } from '../core/parser.js'

const args = process.argv.slice(2)
const inputFile = args.find(a => !a.startsWith('--'))
const typeFlag = args.find(a => a.startsWith('--type='))?.split('=')[1] || 'freeform'
const outFlag = args.find(a => a.startsWith('--out='))?.split('=')[1] || './output'

if (!inputFile) {
  console.error('Usage: node src/cli/ingest.js <input-file> [--type=ui|dag|workflow] [--out=./output]')
  process.exit(1)
}

const text = fs.readFileSync(inputFile, 'utf-8')
const layers = parseDesignToDAG(text, typeFlag)

console.log(`\n✓ Parsed ${layers.reduce((s, l) => s + l.nodes.length, 0)} nodes across ${layers.length} layers\n`)

layers.forEach(layer => {
  console.log(`  [${layer.label}]`)
  layer.nodes.forEach(n => {
    console.log(`    ${n.type.padEnd(5)} → ${n.name} ${n.desc ? '— ' + n.desc.substring(0, 40) : ''}`)
  })
  console.log()
})

// Write dag.json
fs.mkdirSync(outFlag, { recursive: true })
const dagPath = path.join(outFlag, 'dag.json')
fs.writeFileSync(dagPath, JSON.stringify({ version: '1.0', generated: new Date().toISOString(), layers }, null, 2))
console.log(`✓ Wrote ${dagPath}`)
