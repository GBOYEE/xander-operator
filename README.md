# xander-operator — AI Automation Engine

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](docker-compose.yml)
[![CI](https://github.com/GBOYEE/xander-operator/actions/workflows/ci.yml/badge.svg)](https://github.com/GBOYEE/xander-operator/actions)
[![Coverage](https://img.shields.io/codecov/c/github/GBOYEE/xander-operator)](https://codecov.io/gh/GBOYEE/xander-operator)

**Reusable AI primitives for automating real-world tasks.** xander-operator provides browser automation, research, and task execution with human approval gates, vector memory, and structured reporting.

<p align="center">
  <img src="https://raw.githubusercontent.com/GBOYEE/xander-operator/main/screenshots/workflow.png" alt="xander-operator automation workflow" width="700"/>
</p>

## ✨ Features

- 🤖 **Browser Automation** — Playwright-powered navigation, form filling, data extraction
- 🧠 **LLM Reasoning** — Integrates with OpenAI or Ollama for decision-making
- 💾 **Vector Memory** — Context awareness across long-running tasks (Chroma/FAISS)
- ✅ **Human Approval Gates** — Safety checks before sensitive actions
- 📊 **HTML Reports** — Rich, shareable reports with screenshots and logs
- 🐳 **Docker Ready** — Run headless in CI or production

## 🚀 Quick Start

```bash
git clone https://github.com/GBOYEE/xander-operator.git
cd xander-operator
pip install -e .
xander-operator --task "Summarize the latest news about AI"
```

Or as an API server:
```bash
uvicorn xander_operator.api.server:app --reload
# POST /run with {"task": "..."}
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

See [docs/architecture.md](docs/architecture.md) for component details.

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| Orchestration | Custom agent runtime (GSD planning) |
| LLM | OpenAI, Anthropic, Ollama (via OpenRouter) |
| Memory | Chroma / FAISS |
| Browser | Playwright (headless) |
| API | FastAPI |
| Storage | SQLite (state) + file system |
| DevOps | Docker, pre-commit hooks, CI |

## 🧪 Testing & CI

```bash
pytest tests/ -v --cov=xander_operator
```

CI runs on every push: `black`, `ruff`, `mypy`, tests, coverage.

## 📚 Documentation

- [Getting Started](docs/README.md)
- [API Reference](docs/api.md)
- [Tools Catalog](docs/tools.md)
- [Contributing](CONTRIBUTING.md)

## 🎯 Roadmap

- [ ] MCP (Model Context Protocol) integration
- [ ] Multi-agent teams (orchestrate multiple xander-operator instances)
- [ ] Cloud browser provider (Browserless, Zyte)
- [ ] Distributed memory cluster
- [ ] Plugin marketplace

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We especially need help with:
- Additional browser tools (PDF parsing, captcha solving)
- Memory backends (Pinecone, Weaviate integrations)
- Better report templates

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
Built by <a href="https://github.com/GBOYEE">Oyebanji Adegboyega</a> • 
<a href="https://gboyee.github.io">Portfolio</a> • 
<a href="https://twitter.com/Gboyee_0">@Gboyee_0</a>
</p>
