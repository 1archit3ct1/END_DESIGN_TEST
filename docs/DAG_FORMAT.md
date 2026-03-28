# DAG Format — EndDesign Ingestor

## Node Types

| Type | Layer | Purpose |
|------|-------|---------|
| `ui` | UI / Surface | Buttons, inputs, cards — everything the user touches |
| `fn` | Functions / Handlers | The handler each UI element maps to |
| `io` | I/O / Boundaries | APIs, files, tokens, data stores |
| `root` | Root Capability | The top-level intent — everything derives from here |

## Edge Direction

Edges flow **downward**: UI → fn → io → root

This means:
- Clicking a button (UI) triggers a handler (fn)
- The handler calls an API or writes a file (io)
- All IO traces back to the root capability

## triggerMap

Maps UI node IDs to their immediate function handler:

```json
"triggerMap": {
  "ui_export_button": { "event": "onClick", "maps_to": "fn_export" },
  "ui_connect_button": { "event": "onClick", "maps_to": "fn_connect" }
}
```

This is the key artifact for automation. The agent loop reads triggerMap to know what to call without understanding the UI.

## task_status.json Contract

```json
{
  "tasks": [
    {
      "id": "fn_export",
      "name": "Export",
      "status": "pending | running | done | blocked",
      "hash": null,
      "retries": 0,
      "result": null,
      "updatedAt": null
    }
  ],
  "meta": {
    "root": "root",
    "loopActive": false,
    "completedAt": null
  }
}
```

## Loop Contract

1. Agent reads `task_status.json`
2. Finds first task with `status: "pending"`
3. Executes it
4. Writes `{ status: "done", hash: "<sha256 of output>", result: "...", updatedAt: "<iso>" }`
5. If error: `{ status: "blocked", retries: n }`
6. Loop continues until all tasks are `"done"` or `"blocked"`
7. Agent emits completion signal
