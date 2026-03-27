# xander-operator

> AI-powered operator for safe, auditable browser automation and research — with vector memory, LLM synthesis, HTML reporting, and human-in-the-loop approval gates.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/GBOYEE/xander-operator/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Release v1.1.0-dev](https://img.shields.io/github/v/release/GBOYEE/xander-operator?label=dev)](https://github.com/GBOYEE/xander-operator/releases)

## Problem

Building reliable browser automation scripts is hard:
- Flaky selectors and dynamic content cause crashes
- Safety checks (e.g., "don't submit without human review") are ad‑hoc
- No persistent memory across tasks (vector store optional)
- Hard to audit what the agent actually did
- Research tasks used to return raw snippets only

## Solution

`xander-operator` is a modular Python orchestrator that:
- Uses Playwright for stable web interaction (browse, fill, click)
- Enforces human approval before sensitive actions
- Optionally stores context in a vector database (Chroma/FAISS) for recall
- Logs every step to a structured daily memory file
- Provides a CLI to search past actions by similarity
- Synthesizes research answers with an LLM (OpenAI or Ollama) and caches results
- Generates HTML reports for quick review
- Validates tasks before execution and performs safety checks

Result: A safety‑first, production‑ready agent you can trust with real workflows.

## Features

- **Browse & interact** – Navigate pages, fill forms, extract data.
- **Approval gates** – Pauses for human confirmation before key actions.
- **Vector memory** – Optional Chroma/FAISS backend for semantic recall.
- **LLM research** – Intelligent synthesis of search results using OpenAI or Ollama, with response caching.
- **HTML reporter** – Generate beautiful, self‑contained HTML reports of recent tasks.
- **Safety detectors** – Input validation and URL safety checks to prevent common mistakes.
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

# 2. Configure optional LLM (OpenAI or Ollama)
export OPENAI_API_KEY="sk-..."    # or
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# 3. (Optional) Configure vector memory
cp .env.example .env
# Edit .env to set VECTOR_BACKEND=chromadb or faiss

# 4. Run a demo task
python -m xander_operator.cli --report  # runs one pending task and then produces HTML report
# Or drop a JSON task into memory/tasks.json and let the operator loop pick it up
# Search memory:
python -m xander_operator.cli --search "your query" --top 5
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
    H --> L[HTML Reporter]
```

## Usage Example

```python
from xander_operator import Operator

# Initialize (vector store and LLM are optional)
op = Operator(require_approval=True)

# Define a task
task = {
    "id": "demo-1",
    "type": "browse",
    "url": "https://example.com",
    "selectors": {"title": "h1"},
}

result = op.run(task)
print(result.get("extracted", {}).get("title") or result)
```

For research with LLM synthesis:

```python
from xander_operator import add_task

add_task(
    task_desc="Summarize AI trends",
    task_type="research",
    query="latest advancements in large language models 2025",
    max_results=5,
    follow_up_browse=True
)
```

## Project Structure

```
xander-operator/
├── xander_operator/
│   ├── __init__.py      # Core orchestrator (Operator, TaskStore, CLI main)
│   ├── cli.py           # Entry point wrapper
│   ├── llm.py           # LLM client with caching (OpenAI/Ollama)
│   ├── detectors.py     # Input validation and safety checks
│   └── reporter.py      # HTML report generator
├── researcher.py        # Web search + LLM synthesis agent
├── vector_memory.py     # Optional vector store wrapper (Chroma/FAISS)
├── memory/
│   ├── tasks.db         # SQLite task store (auto-created)
│   ├── llm_cache.db    # LLM response cache (auto-created)
│   └── YYYY-MM-DD.md    # Daily log (auto-created)
├── memory/reports/      # HTML reports (auto-created when using --report)
├── tests/
│   ├── test_detectors.py
│   ├── test_llm.py
│   ├── test_operator.py
│   └── test_reporter.py
├── .github/
│   └── workflows/
│       └── ci.yml       # Lint + install + pytest
├── requirements.txt
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## HTML Reports

After running tasks, generate an HTML report:

```bash
python -m xander_operator.cli --report
```

The report includes a summary (task counts by status/type) and a detailed table of recent tasks. Reports are saved to `memory/reports/` with timestamps.

## Detectors

Tasks are automatically validated before execution. Invalid tasks (missing fields, unsafe URLs, etc.) are rejected and marked as failed. Additional safety warnings (e.g., password fields) are logged. You can also invoke detectors manually:

```python
from xander_operator.detectors import validate_task, safety_check

issues = validate_task(task_dict)
warnings = safety_check(task_dict)
```

## Testing

```bash
pytest -q
```

CI runs on every push: ruff lint, install check, pytest.

## Release & Versioning

We tag stable releases (e.g., `v1.1.0`). See [CHANGELOG.md](CHANGELOG.md) for updates.

## Contributing

PRs welcome. Please:
- Format with `black` and sort imports with `isort`
- Add tests for new features
- Update README/CHANGELOG as needed

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT. See [LICENSE](LICENSE).
