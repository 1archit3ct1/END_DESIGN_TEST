# Universal Intake Setup Guide

## Overview

The Universal Intake system extracts tasks from **any input type**:
- **HTML files** — Parses `data-key` attributes and `rust-note` divs
- **Images/Screenshots** — Uses LLaVA vision model to read UI elements
- **Text specs** — Uses heuristic parser for freeform text

---

## Setup

### 1. Install Vision Model

```bash
# LLaVA 7B (recommended for most systems)
ollama pull llava:7b

# Or LLaVA 32B (if you have 32GB+ VRAM)
ollama pull llava:34b
```

### 2. Configure Environment

Edit `.env`:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:latest
OLLAMA_CODE_MODEL=codellama:7b
OLLAMA_VISION_MODEL=llava:7b
```

### 3. Verify Ollama is Running

```bash
ollama list
# Should show llava:7b in the list
```

---

## Usage

### Extract from HTML File

```bash
# Extracts data-key attributes, rust-note divs, step panels
node src/cli/extract.js gui_status.html --out=./extraction
```

**Output files:**
- `extraction/extraction.json` — All extracted items
- `extraction/operator_overrides.json` — For manual review
- `extraction/projection_graph.json` — DAG for agent consumption

### Extract from Screenshot

```bash
# Uses LLaVA to read UI elements from image
node src/cli/extract.js screenshot.png --out=./extraction
```

### Extract from Text Spec

```bash
# Uses heuristic parser for freeform text
node src/cli/extract.js design.md --out=./extraction
```

---

## Extraction Output Format

### extraction.json

```json
{
  "version": "1.0",
  "extractedAt": "2026-03-28T...",
  "source": {
    "type": "html",
    "parser": "html-dom-parser"
  },
  "statistics": {
    "totalItems": 75,
    "totalSteps": 6,
    "itemsByType": { "backend": 12, "integration": 8, "step1": 15 },
    "itemsByStep": { "step1": 15, "step2": 10, "step3": 20 }
  },
  "confidence": 0.95,
  "items": [
    {
      "id": "rust_backend.pkce_rfc7636",
      "name": "PKCE Implementation",
      "description": "RFC 7636 PKCE SHA256 + base64url",
      "step": "unknown",
      "type": "backend"
    }
  ],
  "steps": [...],
  "layers": [...]
}
```

### projection_graph.json

```json
{
  "version": "1.0",
  "nodes": [
    {
      "id": "P00",
      "label": "PKCE Implementation",
      "kind": "fn",
      "layer": "Backend / Rust",
      "status": "red",
      "confidence": 0.9,
      "source_id": "rust_backend.pkce_rfc7636"
    }
  ],
  "edges": [...],
  "status": "conformance_pending"
}
```

---

## Confidence Scores

| Input Type | Confidence | Why |
|------------|------------|-----|
| HTML (data-key) | 95% | Exact attribute extraction |
| Image (LLaVA) | 75% | OCR + interpretation |
| Text (heuristic) | 85% | Pattern matching |

---

## Troubleshooting

### "Cannot find module 'fs'"

Run in Node.js environment, not browser.

### "Vision API error"

1. Ensure Ollama is running: `ollama list`
2. Check model exists: `ollama list | grep llava`
3. Verify host in `.env`: `OLLAMA_HOST=http://localhost:11434`

### "0 items extracted" from HTML

1. Check HTML has `data-key` attributes
2. Verify file encoding is UTF-8
3. Try: `node src/cli/extract.js gui_status.html` (full path)

### Low confidence on image extraction

- Use higher resolution screenshots
- Ensure UI text is clearly visible
- Consider using HTML extraction if available

---

## Next Steps

After extraction:

1. **Review** `operator_overrides.json` — Add manual corrections
2. **Run generator** — `node src/cli/generate.js extraction/projection_graph.json`
3. **Check task queue** — Tasks promoted to `SPAWN/STOP/.orchestrator/task_queue.json`
4. **Start agent** — Agent reads `prompt.md` and begins implementation

---

## Architecture

```
Input File
    ↓
[Universal Intake]
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│  HTML Parser    │  Vision Parser  │  Text Parser    │
│  (data-key)     │  (LLaVA)        │  (regex)        │
└─────────────────┴─────────────────┴─────────────────┘
    ↓
[extraction.json] → [operator_overrides.json] → [projection_graph.json]
    ↓
[Agent Loop] → [task_status.json] → [prompt.md]
```
