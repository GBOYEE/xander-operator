# Xander Operator 🤖

AI developer agent that writes code and applies changes safely.

[![CI](https://github.com/GBOYEE/xander-operator/actions/workflows/ci.yml/badge.svg)](https://github.com/GBOYEE/xander-operator/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- LLM‑driven code generation (Ollama or OpenAI)
- Git‑backed changes with automatic commits
- Safe file operations confined to workspace
- FastAPI server for remote invocation
- Docker support with health checks
- Pre‑commit hooks (black, flake8, isort, mypy)
- CI: lint, test, Safety scan, coverage

## Quick Start

```bash
# Install
pip install -e .

# Run agent
xander-operator --task "create a README.md with project description"

# Or start API
uvicorn xander_operator.api.server:app --reload
```

## Configuration

Environment variables:

- `XANDER_OPERATOR_WORKDIR` — path to workspace (default: `/workspace`)
- `OLLAMA_URL` — local LLM endpoint (default: `http://localhost:11434`)
- `OPENAI_API_KEY` — optional fallback
- `XANDER_OPERATOR_MODEL` — model name (default: `phi3`)
- `XANDER_DRY_RUN` — if true, no files written
- `XANDER_ALLOW_SHELL` — if true, agent may run shell (opt‑in)

## API

`POST /run` — `{"task": "string"}` → result with files written and commit SHA.

## Safety

- All file writes are confined to `workdir`.
- Git history allows rollback.
- Shell commands disabled by default.

## License

MIT
