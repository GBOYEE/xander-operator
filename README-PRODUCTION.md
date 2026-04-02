# Xander Operator — Production Guide

Autonomous coding agent with browser automation, vector memory, and LLM integration. Deploy as a service with observability.

## Architecture

```mermaid
graph TD
    Client --> Gateway[FastAPI Gateway]
    Gateway --> DB[(SQLite Tasks)]
    Operator -->|polls| DB
    Operator --> Browser[Playwright]
    Operator --> Memory[Vector Memory (optional)]
    Operator --> LLM[Ollama/OpenAI]

    subgraph "Xander Operator"
        Gateway
        Operator
    end
```

Components:
- **Gateway** (`gateway.py`) — HTTP API: create tasks, list, cancel, health/metrics, operator start/stop
- **Operator** (`xander_operator/`) — background loop that executes tasks (browse, fill, research, send_telegram)
- **Vector Memory** (`vector_memory.py`) — optional semantic search (sentence-transformers + FAISS)
- **Task Store** — SQLite (`tasks.db`) persistent queue

---

## Quick Start (Production)

```bash
# Clone and install
git clone https://github.com/GBOYEE/xander-operator.git
cd xander-operator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# With Docker Compose (recommended)
docker-compose up -d
# Gateway on http://localhost:8080
# Operator starts automatically

# Without Docker
export XANDER_DB=./data/tasks.db
python gateway.py  # starts FastAPI
python -m xander_operator --loop  # in another terminal
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health, operator status |
| `GET` | `/metrics` | Counters: tasks_total, tasks_succeeded, tasks_failed, operator_running |
| `GET` | `/tasks` | List tasks (query params: `limit`, `status`) |
| `POST` | `/tasks` | Create task (JSON body: `description`, `type`, `url`, `selectors`, `values`, `params`) |
| `GET` | `/tasks/{id}` | Get task details |
| `POST` | `/tasks/{id}/cancel` | Cancel pending task |
| `POST` | `/operators/start` | Start operator loop (background) |
| `POST` | `/operators/stop` | Stop operator loop |

Task types: `browse`, `fill`, `research`, `send_telegram`, `send_telegram_file`. See README for payload details.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `XANDER_ENV` | `production` | `development` enables reload |
| `XANDER_PORT` | `8080` | Gateway port |
| `XANDER_DB` | `~/.openclaw/workspace/tasks.db` | SQLite DB path |
| `XANDER_WORKSPACE` | `~/.openclaw/workspace` | Workspace root for memory/logs |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama for LLM tasks |
| `XANDER_AUTO_APPROVE` | false | Skip human approval (use with caution) |

---

## Docker Compose

```bash
docker-compose up -d
```

Services:
- `gateway` — FastAPI on port 8080
- `operator` — background task consumer (depends on gateway)

Volumes:
- `./data:/data` — tasks.db
- `./memory:/app/memory` — logs, vector index

---

## Observability

- **Health**: `GET /health` includes operator running state
- **Metrics**: `GET /metrics` returns counters
- **Logs**: Structured logs to stdout; operator writes daily logs to `memory/YYYY-MM-DD.md`
- **Vector Memory**: optional semantic search; install `sentence-transformers` and `faiss` to enable

---

## Upgrading

1. Pull latest code
2. Rebuild: `docker-compose build --pull`
3. Restart: `docker-compose up -d`

Backup `data/` and `memory/` regularly.

---

## Security

- Use strong `OLLAMA_HOST` if exposed externally (keep internal)
- Consider adding API key auth to gateway endpoints (future)
- Operator actions require approval unless `XANDER_AUTO_APPROVE=true`
- Browser automation runs headless Chromium; ensure system has dependencies

---

## Testing

```bash
pip install -e .[dev]
pytest tests/ -v
mypy . --ignore-missing-imports
```

---

## License

MIT — see `LICENSE`.
