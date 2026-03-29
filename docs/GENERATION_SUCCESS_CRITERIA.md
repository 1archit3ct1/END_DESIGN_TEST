# Code Generation Success Criteria

This document defines the success criteria for the NextAura Hybrid Code Generator.

## Generation Success Criteria

### 1. All Tasks Processed
- **Criterion:** Every task in the DAG reaches a terminal state
- **Terminal States:** `done`, `blocked`, `failed`, `skipped`
- **Validation:** Check `task_status.json` - no tasks should remain in `pending` or `running` state

### 2. All Files Created
- **Criterion:** Each completed task generates at least one output file
- **Validation:** For each task with status `done`, verify `generatedFile` or `generatedFiles` field exists and file is present on disk

### 3. All Syntax Valid
- **Criterion:** All generated code passes syntax validation
- **Validation:** Syntax checker returns `is_valid=True` for all generated files
- **Languages Supported:** Python (.py), TypeScript/JavaScript (.ts, .tsx, .js, .jsx), Rust (.rs)

### 4. No Blocked Tasks (Optional)
- **Criterion:** Zero tasks in `blocked` state
- **Note:** Some blocked tasks may be acceptable depending on use case
- **Validation:** Count tasks with `status=blocked` in `task_status.json`

### 5. Output Structure Valid
- **Criterion:** Generated files follow expected directory structure
- **Validation:**
  - Rust files → `output/src-tauri/src/`
  - TypeScript files → `output/src/`
  - Python files → `output/src/` or `output/agent/`

### 6. Headers Present
- **Criterion:** All generated files contain auto-generated header comment
- **Validation:** File content contains "Auto-generated" string

## Metrics

### Success Rate
```
success_rate = (completed_tasks / total_tasks) * 100
```

**Thresholds:**
- ✅ Excellent: ≥ 95%
- ✅ Good: ≥ 80%
- ⚠️ Acceptable: ≥ 60%
- ❌ Poor: < 60%

### Generation Time
```
total_time = end_timestamp - start_timestamp
avg_task_time = total_time / completed_tasks
```

**Thresholds:**
- ✅ Excellent: < 5 seconds per task
- ✅ Good: < 15 seconds per task
- ⚠️ Acceptable: < 30 seconds per task
- ❌ Poor: > 30 seconds per task

## Test Validation

All success criteria are validated by tests in `tests/test_end_to_end.py`:

| Test | Criteria Validated |
|------|-------------------|
| `test_end_to_end_full_generation` | 1, 2, 5 |
| `test_end_to_end_with_failures` | 1, 4 |
| `test_end_to_end_resume_from_checkpoint` | 1, 3 |
| `test_output_structure_validation` | 2, 5, 6 |
| `test_all_tasks_reach_terminal_state` | 1 |
| `test_validate_success_criteria` | All |

## Completion Signal

When all tasks complete:

1. **State Updates:**
   - `meta.loopActive` → `false`
   - `meta.completedAt` → ISO timestamp

2. **Build Report:**
   ```
   DONE — Build complete: X/Y tasks successful, Z/Z tests passed
   Success Rate: XX.X%
   Duration: XX.XX seconds
   ```

3. **Exit Code:**
   - `0` if all tasks successful
   - `1` if any tasks failed
