# Xander Operator 🤖

AI developer agent that writes code and applies changes safely.

[![CI](https://github.com/GBOYEE/xander-operator/actions/workflows/ci.yml/badge.svg)](https://github.com/GBOYEE/xander-operator/actions)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](https://github.com/GBOYEE/xander-operator/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Problem

You need an AI that can actually implement changes in your codebase — not just chat, but *act*. But letting an LLM run wild is dangerous. How do you get the power of autonomous coding with safety?

## ✅ Solution

Xander Operator is a production‑ready AI agent that:

- **Plans** tasks using GSD methodology (Goal → Scope → Deliverables)
- **Executes** with controlled tools: file editing, git commits, browser automation (Playwright)
- **Remembers** context via SQLite vector memory for long‑running sessions
- **Rolls back** via automatic git commits after each successful step
- **Validates** results using structured outputs and optional human approval

All file operations are confined to a workspace. Shell commands are opt‑in. Designed for autonomous development, not just prototypes.

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Run agent (CLI)
xander-operator --task "Add authentication middleware to FastAPI app"

# Or start API server
uvicorn xander_operator.api.server:app --reload
# POST /run with {"task": "..."}

# Set model (default: phi3:mini for local speed)
export XANDER_OPERATOR_MODEL=phi3:medium
```

## 🏗️ Architecture

```mermaid
flowchart LR
    CLI[CLI / API] --> Broker[Task Broker]
    Broker --> Planner[Planner Agent]
    Planner --> Executor[Executor Agent]
    Executor --> Tools[Tool Registry]
    Tools --> FS[File System]
    Tools --> Git[Git]
    Tools --> Browser[Playwright]
    Executor --> Memory[Vector Memory]
    Executor --> Broker

    subgraph "Safety Controls"
        Approval[Approval Queue]
        DryRun[Dry Run Mode]
        Sandbox[Workspace Sandbox]
    end

    Broker --> Approval
    Executor --> DryRun
    Tools --> Sandbox
```

**Components:**

- **Task Broker** — queues tasks, tracks status, persists results
- **Planner Agent** — GSD planner: decomposes task into steps, selects tools
- **Executor Agent** — runs steps, calls tools, updates memory
- **Tool Registry** — browse, fill, code, reason (each with permission model)
- **Vector Memory** — Chroma/FAISS storage for context retrieval across sessions
- **Safety Layer** — dry‑run, approval workflows, workspace confinement

## 🔧 Tools

| Tool | Permission | Description |
|------|------------|-------------|
| `browse` | low | Fetch web pages, extract content |
| `fill` | medium | Form automation (Playwright) |
| `code` | high | Read/write files, apply patches |
| `reason` | low | LLM reasoning without action |

Tools can be enabled/disabled via config.

## 🧠 Model Selection

- **Local (Ollama):** `phi3:mini` (fast), `phi3:medium` (balanced), `llama3.1:8b` (powerful but slow)
- **OpenAI:** `gpt-4o-mini`, `gpt-4-turbo` (set `OPENAI_API_KEY`)

Change via `XANDER_OPERATOR_MODEL` env var.

## 🔒 Safety

- **Workspace sandbox** — agent can only access `$WORKDIR` (default: `/workspace`)
- **Git rollback** — every action creates a commit; revert with `git revert`
- **Shell opt‑in** — set `XANDER_ALLOW_SHELL=true` to enable shell commands
- **Dry run mode** — set `XANDER_DRY_RUN=true` to preview changes without writing
- **Approval queue** — medium/high actions can require manual review (configurable)

## 📊 Observability

- **API health** — `GET /health` (FastAPI)
- **Task status** — `GET /tasks` lists recent tasks and their state
- **Structured logs** — JSON output for log aggregation
- **Metrics** — `GET /metrics` (Prometheus format)

## 🧪 Testing & QA

```bash
# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov

# Coverage target: 85%
```

## 🚢 Deployment

```bash
# Docker Compose (recommended)
docker-compose up -d

# Or systemd
sudo cp xander-operator.service /etc/systemd/system/
sudo systemctl enable --now xander-operator
```

See `docker-compose.yml` for environment variables.

## 📚 Example API Usage

```bash
curl -X POST http://localhost:8000/run \\
  -H "Content-Type: application/json" \\
  -d '{"task": "Fix the lint errors in src/utils.py"}'
```

Response:

```json
{
  "task_id": "abc123",
  "status": "completed",
  "steps": [
    {"tool": "code", "description": "Fix import order", "files_changed": ["src/utils.py"]},
    {"tool": "code", "description": "Remove trailing whitespace", "files_changed": ["src/utils.py"]}
  ],
  "commit_sha": "def456",
  "summary": "Applied 2 changes; all lint errors resolved."
}
```

---

**Ready to build?** Let Xander handle the grunt work while you focus on architecture.
