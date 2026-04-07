# xander-operator API Reference

Base URL: `http://localhost:8000`

## Endpoints

- `GET /health` — service health
- `POST /run` — execute a task
  - Body: `{ "task": "string", "context": {} }`
  - Returns: `{ task_id, status, steps[], summary }`
- `GET /tasks` — list recent tasks
- `GET /tasks/{id}` — get task details
- `POST /tools` — list available tools (read-only)

All endpoints require `X-API-Key` header (set in config).
