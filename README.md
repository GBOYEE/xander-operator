# xander-operator

> AI-powered operator for safe, auditable browser automation and research — with vector memory and human-in-the-loop approval gates.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/GBOYEE/xander-operator/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Release v1.0.1](https://img.shields.io/github/v/release/GBOYEE/xander-operator?label=stable)](https://github.com/GBOYEE/xander-operator/releases)

## Problem

Building reliable browser automation scripts is hard:
- Flaky selectors and dynamic content cause crashes
- Safety checks (e.g., “don’t submit without human review”) are ad‑hoc
- No persistent memory across tasks (vector store optional)
- Hard to audit what the agent actually did

## Solution

`xander-operator` is a modular Python orchestrator that:
- Uses Playwright for stable web interaction (browse, fill, click)
- Enforces human approval before sensitive actions
- Optionally stores context in a vector database (Chroma/FAISS) for recall
- Logs every step to a structured daily memory file
- Provides a CLI to search past actions by similarity

Result: A safety‑first, production‑ready agent you can trust with real workflows.

## Features

- **Browse & interact** – Navigate pages, fill forms, extract data.
- **Approval gates** – Pauses for human confirmation before key actions.
- **Vector memory** – Optional Chroma/FAISS backend for semantic recall.
- **Structured logging** – JSON‑lines logs with timestamps, task IDs, outcomes.
- **CLI search** – Query past runs by natural language.
- **Extensible** – Add new operators (API calls, file ops) by subclassing `BaseOperator`.

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/GBOYEE/xander-operator.git
cd xander-operator
pip install -r requirements.txt
playwright install chromium

# 2. Configure optional vector memory (or skip for now)
cp .env.example .env
# Edit .env to set VECTOR_BACKEND=chromadb or faiss

# 3. Run a demo task
python -m operator.cli search "fetch example.com homepage"
# Or drop a JSON task into memory/tasks.json and let the operator loop pick it up
```

## Demo

![Operator demo: fetching example.com and logging result](docs/demo.gif)

*(The GIF shows the CLI starting, executing a browse task, pausing for approval, and writing to the daily memory log.)*

## Architecture

```mermaid
flowchart TD
    A[CLI / Scheduler] --> B[Operator]
    B --> C{Action Type}
    C -->|browse| D[Playwright Browser]
    C -->|research| E[Web Search + LLM]
    C -->|fill| F[Form Interactor]
    B --> G[Approval Gate]
    G -->|approved| H[Execute]
    G -->|rejected| I[Log & Abort]
    H --> J[Vector Memory (optional)]
    H --> K[Daily Memory Log]
```

## Usage Example

```python
from operator import Operator
from memory import VectorStore

# Initialize with optional vector memory
store = VectorStore(backend="chromadb")
op = Operator(vector_store=store, require_approval=True)

# Define a task
task = {
    "id": "demo-1",
    "type": "browse",
    "url": "https://example.com",
    "selectors": {"title": "h1"},
}

result = op.run(task)
print(result["extracted"]["title"])  # → "Example Domain"
```

## Project Structure

```
xander-operator/
├── operator/
│   ├── cli.py           # Entry point, task loop
│   ├── core.py          # Operator class, approval logic
│   ├── actions.py       # browse, fill, click implementations
│   └── safety.py        # Approval gate UI
├── memory/
│   ├── vector.py        # Vector store wrapper (Chromadb/FAISS)
│   ├── logger.py        # JSON-lines daily logger
│   └── tasks.json       # Pending task queue
├── tests/
│   └── test_core.py     # Minimal pytest suite
├── docs/
│   └── demo.gif
├── .github/
│   └── workflows/
│       └── ci.yml       # Lint + install + pytest
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE
```

## Testing

```bash
pytest -q
```

CI runs on every push: ruff lint, install check, pytest.

## Release & Versioning

We tag stable releases (e.g., `v1.0.1`). See [CHANGELOG.md](CHANGELOG.md) for updates.

## Contributing

PRs welcome. Please:
- Format with `black` and sort imports with `isort`
- Add tests for new features
- Update README/CHANGELOG as needed

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT. See [LICENSE](LICENSE).
