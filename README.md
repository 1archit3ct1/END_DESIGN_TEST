# EndDesign Ingestor

Design-to-function DAG mapper and agent loop scaffold generator.

**What it solves:** Every UI element, every button, every node in a design has to backward-chain to a root capability. UI → Handler → Function → I/O → Root. Once that mapping exists as machine-readable artifacts (`dag.json` + `task_status.json`), an agent loop can consume it without ambiguity.

---

## Stack

```
enddesign/
├── index.html              # Entry point
├── vite.config.js
├── package.json
├── src/
│   ├── main.js             # App boot + event wiring
│   ├── styles/
│   │   └── main.css
│   ├── data/
│   │   └── samples.js      # Built-in design specs
│   └── core/
│       ├── parser.js       # Design spec → layered DAG
│       ├── generator.js    # DAG → React / prompt.md / dag.json / task_status.json
│       ├── renderer.js     # DOM rendering (no framework)
│       └── exporter.js     # File download helpers
│   └── cli/
│       ├── ingest.js       # CLI: parse design → dag.json
│       └── generate.js     # CLI: dag.json → scaffold artifacts
├── data/                   # Drop your own design specs here
└── docs/
    └── DAG_FORMAT.md
```

---

## Setup

```bash
npm install
npm run dev
```

Open `http://localhost:5173`

---

## Usage — Browser

1. Paste a design spec (UI description, JSON DAG, markdown doc) or drop a file
2. Select design type and output target
3. Click **Ingest & Map**
4. DAG renders center — click any node to inspect its backward chain
5. Right panel shows generated components
6. **Export All** downloads: `prompt.md`, `dag.json`, `task_status.json`, React components

---

## Usage — CLI

```bash
# Parse a design file → dag.json
node src/cli/ingest.js data/my-design.md --type=ui --out=./output

# Generate scaffold from dag.json
node src/cli/generate.js output/dag.json --target=full --out=./output
```

---

## Output Artifacts

| File | Purpose |
|------|---------|
| `dag.json` | Machine-readable DAG with nodes, edges, triggerMap |
| `task_status.json` | Agent loop state file — read/write on each iteration |
| `prompt.md` | Agent instructions referencing the DAG |
| `*.jsx` | React components pre-wired to handler functions |

---

## DAG Format

```json
{
  "version": "1.0",
  "root": "root-node-id",
  "nodes": [
    { "id": "btn_export", "name": "Export", "type": "ui", "layer": "ui", "edges": ["fn_export"] },
    { "id": "fn_export", "name": "Export", "type": "fn", "layer": "fn", "edges": ["io_csv"] },
    { "id": "io_csv", "name": "CSV", "type": "io", "layer": "io", "edges": ["root"] },
    { "id": "root", "name": "SystemRoot", "type": "root", "layer": "root", "edges": [] }
  ],
  "triggerMap": {
    "btn_export": { "event": "onClick", "maps_to": "fn_export" }
  }
}
```

---

## Agent Loop Pattern

```
prompt.md loaded
  → read task_status.json
  → find first task with status: "pending"
  → execute
  → write result + hash back to task_status.json
  → repeat until all done
  → emit DONE
```

The plan is a file, not a conversation. The loop is dumb and fast.

---

## Next

- [ ] Add JSZip for single-file bundle export
- [ ] SVG edge rendering between DAG nodes
- [ ] Import from Figma JSON export
- [ ] Integrate with NextAura workflow-app as ingest step
- [ ] Write dag.json → MCP tool call map
