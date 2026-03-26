# Task Queue Specification

## Storage

File: `memory/tasks.json`

Structure:
```json
{
  "version": "0.2",
  "tasks": [
    { /* task object */ }
  ]
}
```

Additionally, for recovery, an append-only journal `memory/task_log.jsonl` stores every change (create, update, status change) with timestamp and diff.

## Task Object (Full)

See PROTOCOLS.md for complete schema. Key fields:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | uuid4 | yes | immutable |
| type | enum | yes | browse, research, fill, code, write, custom |
| description | string | yes | human-readable |
| context | object | no | project, goal, dependencies |
| spec | object | yes | type-specific parameters |
| status | enum | yes | pending, in_progress, done, failed, blocked, cancelled |
| priority | int | no | 1–5, default 3 |
| created | ISO8601 | yes |
| updated | ISO8601 | yes |
| attempts | int | no | default 0 |
| max_attempts | int | no | default 3 |
| last_error | string | no |
| result | any | no |
| requires_approval | bool | no | default based on risk registry |
| owner | string | no | "user", "system", "agent_name"; default "user" |

## API (Task Manager Module)

### `add_task(description, type, spec, context=None, priority=3) -> task_id`
- Serializes task, sets timestamps, saves.

### `get_next_task(agent_type=None, project=None) -> task | None`
- Filters: status=pending, optionally by type or project
- Respects dependencies: only return if all deps are `done`
- Order: priority desc, created asc

### `claim_task(task_id, agent_name) -> bool`
- Atomic claim: sets `status=in_progress`, `owner=agent_name`
- Prevents multiple agents from working same task
- Returns false if already claimed or status changed

### `update_task(task_id, updates) -> bool`
- Partial update; merges into task
- Auto-updates `updated` timestamp
- Validates status transition rules (e.g., cannot go from `done` → `in_progress` without reset)

### `add_subtask(parent_id, description, type, spec) -> task_id`
- Creates child task linked to parent
- Parent must be in_progress; child can be pending

### `list_tasks(filters) -> [tasks]`
- Filters: status, type, project, owner, created_after, etc.

### `retry_failed(task_id) -> bool`
- If task status=failed and attempts < max_attempts, reset to pending and clear error.

## Risk Registry (Determines `requires_approval`)

```python
RISK_LEVELS = {
  "browse": "low",
  "research": "low",
  "code": "medium",
  "write": "low",
  "fill": "high",
  "custom": "medium"  # depends on payload
}

APPROVAL_REQUIRED = {
  "high": True,
  "medium": False,  # can be overridden per task
  "low": False
}
```

Agents must consult risk registry before performing action; if `requires_approval=True`, orchestrator sends approval request and waits for user command.

## Transitions

Valid status flow:

```
pending → in_progress → (done | failed | blocked)
         ↘ cancel → cancelled
         ↘ retry → in_progress (if failed, attempts < max)
```

- `pending`: created, not started
- `in_progress`: claimed by an agent
- `done`: completed successfully
- `failed`: terminated with error; may be retried
- `blocked`: waiting on external input (e.g., approval)
- `cancelled': user cancelled

## Concurrency

For single-process operator, no locking needed. For multi-agent scenario later, use file lock or SQLite transactions.

## Journaling

Every mutation writes a line to `task_log.jsonl`:
```json
{
  "ts": "ISO",
  "op": "create | update | claim | status_change",
  "task_id": "uuid",
  "diff": { "field": "old->new" }  // or full before/after
}
```

This enables recovery and audit.

---

Implement this spec as a `task_manager.py` module with the above API. The orchestrator will import and use it instead of the simple load/save functions.
