# Protocols & Contracts

This document defines the JSON schemas used between components: orchestrator ↔ agents, task storage, and logging format.

## 1. Task Object

```json
{
  "id": "uuid4",
  "type": "browse | research | fill | code | write | custom",
  "description": "Human-readable one-liner",
  "context": {
    "project": "optional project identifier",
    "goal": "higher-level goal this task serves",
    "dependencies": ["task_id1", "task_id2"]
  },
  "spec": {
    // type-specific parameters (see below)
  },
  "status": "pending | in_progress | done | failed | blocked | cancelled",
  "priority": 1 (low) – 5 (high),
  "created": "ISO8601",
  "updated": "ISO8601",
  "attempts": 0,
  "max_attempts": 3,
  "last_error": "string if failed",
  "result": { /* agent-specific output */ },
  "requires_approval": true | false,
  "owner": "user | agent_name | system"
}
```

### type-specific spec shapes

- **browse**: `{ "url": "https://...", "extract": "CSS selector or 'all'", "screenshot": false }`
- **research**: `{ "query": "...", "max_results": 5, "follow_up_browse": true }`
- **fill**: `{ "url": "...", "selectors": { "field_name": "css selector" }, "values": { "field_name": "value" }, "submit": true }`
- **code**: `{ "language": "python", "spec": "...", "tests": "..." }`
- **write**: `{ "topic": "...", "format": "md|txt", "outline": [...], "sources": [...] }`
- **custom**: `{ "agent": "name", "payload": { ... } }`

## 2. Agent Result Object

All agents must return JSON with at least:

```json
{
  "success": true | false,
  "task_id": "uuid",
  "agent": "browser | researcher | coder | writer | action",
  "timestamp": "ISO8601",
  "output": { /* type-specific data */ },
  "error": "string if failed",
  "logs": ["line1", "line2"]  // optional debug lines
}
```

### Output Shapes

- **browser**: `{ "url": "...", "content": "...", "screenshot": "/path/to/file.png" }`
- **researcher**: `{ "query": "...", "answer": "...", "sources": [{ "title": "...", "url": "...", "snippet": "..." }] }`
- **code**: `{ "files": { "main.py": "...", ... }, "tests_passed": false }`
- **write**: `{ "title": "...", "body": "...", "word_count": 0 }`
- **action**: `{ "action_taken": "fill_form", "url": "...", "approved": true, "result": "submitted|failed" }`

## 3. Log Entry Format (Daily Log)

Each line in `memory/YYYY-MM-DD.md`:

```
[YYYY-MM-DD HH:MM] TAG message
```

Tags:
- `▶️` — task start
- `✅` — success
- `❌` — failure
- `⚠️` — warning
- `🔴` — approval request
- `💤` — idle
- `🔧` — system event
- `📝` — memory update

Example:
```
[2025-03-26 13:15] ▶️  Starting task 123e4567: Check price
[2025-03-26 13:15] ✅ browse https://shop.example.com → 3421 chars
[2025-03-26 13:15] 📝 Added insight to MEMORY.md
```

## 4. Approval Message (to user)

When HANDS agent needs approval, orchestrator outputs to chat:

```
🔴 ACTION REQUIRES APPROVAL
Task: Submit contact form
URL:  https://contact.example.com
Will: Fill fields (name, email, message) and submit
Reply: /approve <task_id> or /deny <task_id>
```

User replies with `/approve 123e4567` or `/deny 123e4567`. Operator polls or waits accordingly.

## 5. Error Format

```json
{
  "task_id": "uuid",
  "stage": "browse | fill | approval | log",
  "code": "TIMEOUT | NETWORK | SELECTOR_NOT_FOUND | APPROVAL_DENIED | UNEXPECTED",
  "message": "Human-readable",
  "details": { ... optional structured info ... }
}
```

## 6. Autonomy Engine Output

When generating tasks from goals, the engine produces a plan:

```json
{
  "goal": "Track competitor prices weekly",
  "plan": [
    { "task": "browse product page", "spec": { "url": "...", "extract": ".price" } },
    { "task": "store result", "spec": { "format": "csv", "append": true } }
  ],
  "schedule": "weekly"
}
```

## 7. Inter-agent Communication (future)

When we add message queue:

Command envelope:
```json
{
  "envelope": {
    "id": "uuid",
    "timestamp": "ISO",
    "source": "orchestrator",
    "destination": "browser_agent",
    "correlation_id": "uuid (for tracing)"
  },
  "payload": { ... task spec or result ... }
}
```

---

All contracts must be versioned (`protocol_version: "0.1"`) to allow evolution.
