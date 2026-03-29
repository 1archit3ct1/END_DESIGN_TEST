# NextAura EndDesign — Autonomous Code Generation Suite

NextAura EndDesign is a powerful design-to-function pipeline that converts UI specifications into complete, production-ready codebases using a hybrid autonomous agent loop.

**The Workflow:**  
`Design Spec` → `Ingestor` → `DAG` → `Hybrid Agent Loop` → `Verified Source Code`

---

## 🚀 The Core Systems

### 1. EndDesign Ingestor (The Architect)
The Ingestor maps UI elements, buttons, and nodes from a design spec to a machine-readable **Directed Acyclic Graph (DAG)**.
- **Design-to-Function Mapping:** Every UI element is backward-chained to its root capability (UI → Handler → Function → I/O → Root).
- **Artifact Generation:** Produces `dag.json` (structural map) and `task_status.json` (execution plan).
- **Interface:** Available as a web-based dashboard (Vite/React) and a CLI tool.

### 2. NextAura Hybrid Agent (The Builder)
A Python-powered autonomous engine that executes the `task_status.json` plan, building the repository file-by-file.
- **Hybrid Intelligence:** Uses a smart router to choose between **Deterministic Templates** (high-reliability code for known patterns) and **LLM Generation** (`codellama:7b` via Ollama) for custom logic.
- **Self-Healing Loop:** Automatically validates generated code (Syntax/Lints), retrying with modified prompts if errors are detected.
- **Context Awareness:** Manages cross-file imports, type hints, and project-wide consistency.

---

## 🛠️ Stack

### Frontend & CLI (Ingestor)
- **Runtime:** Node.js (Vite + React)
- **Logic:** Vanilla JS for core parser/renderer
- **Output:** JSON DAGs, Markdown prompts, and React scaffolds

### Backend Agent (Builder)
- **Runtime:** Python 3.x
- **LLM Engine:** Ollama (`codellama:7b` or `mistral`)
- **Validation:** Built-in Python/JS syntax checkers
- **Architecture:** Topological sort task queue with dependency resolution

---

## 📂 Repository Structure

```text
STOP/
├── agent/                  # NextAura Hybrid Agent System
│   ├── python_agent.py     # Main autonomous loop entry
│   ├── hybrid_router.py    # Route to Template vs LLM
│   ├── llm_coder.py        # Ollama API integration
│   ├── syntax_check.py     # Code validation & verification
│   ├── state_manager.py    # task_status.json orchestration
│   └── templates/          # High-reliability code templates
├── src/                    # Ingestor UI & Core Logic
│   ├── components/         # BuildConsole, FileTree, CodePreview
│   ├── core/               # Parser, Generator, Renderer
│   └── cli/                # ingest.js, generate.js
├── data/                   # Design specs & samples
├── output/                 # The target for generated code
└── tests/                  # Agent & UI verification tests
```

---

## ⚡ Setup & Usage

### 1. Ingestor Setup (Node)
```bash
npm install
npm run dev
```
1. Open `http://localhost:5173`.
2. Paste a design spec or drop a file.
3. Click **Ingest & Map** to generate your DAG and Task List.

### 2. Agent Setup (Python)
Ensure [Ollama](https://ollama.ai/) is running with `codellama:7b`.
```bash
# Start the autonomous build from the generated DAG
python agent/python_agent.py --dag extraction/projection_graph.json
```

### 3. Monitoring
Use the **Build Console** in the UI to monitor the agent in real-time as it:
- Selects the next pending task.
- Generates code via LLM or Template.
- Validates syntax and writes files to `./output/`.
- Updates `task_status.json` until completion.

---

## 📄 Core Artifacts

| File | Purpose |
|------|---------|
| `dag.json` | The architectural blueprint (Nodes, Edges, Triggers). |
| `task_status.json` | The "Plan of Record" — tracks agent progress and results. |
| `prompt.md` | High-level agent personality and instruction set. |
| `./output/` | The final generated repository (React, Tauri, Rust, etc.). |

---

## 🔮 Roadmap
- [ ] Multi-agent orchestration for parallelized generation.
- [ ] Figma/AdobeXD direct API integration.
- [ ] Integrated Diff-viewer for manual code review before commit.
- [ ] Web-based LLM parameter tuning in the Build Console.
- [ ] MCP (Model Context Protocol) tool integration for real-time environment feedback.
