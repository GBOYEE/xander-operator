# Project: Xander Operator

## Project Reference

- Repository: GBOYEE/xander-operator
- Branch: master

## Core Value

An autonomous AI operator that can browse, research, remember, and execute complex multi-step tasks with minimal human guidance.

## Target Users

Developers, researchers, AI engineers who want to automate workflows.

## Requirements

### Functional
- Execute skills and commands on behalf of user
- Browse web pages and extract information
- Reason about tasks and decompose into steps
- Maintain persistent memory (vector + SQLite)
- Support plugin skills architecture

### Non-Functional
- Secure credential handling (no hardcoded secrets)
- Rate limiting and retry logic for API calls
- Configurable via YAML
- Extensible agent architecture

## Constraints

- Python 3.11+ only
- No GUI required (CLI/agent mode only)
- Optional LLM backends: OpenAI, Ollama

## Technical Stack

- Python, Pydantic, FastAPI (optional API)
- ChromaDB or FAISS for memory
- Playwright/Selenium for browsing
- OpenAI API or local LLM (Ollama)

## Dependencies

- ASYNC HTTP libraries
- Browser automation drivers

## Interfaces

- CLI: `xander-operator --task "research X"`
- API (optional): `/execute`, `/status`, `/memory`

## Acceptance Criteria

- Operator can complete a multi-step research task end-to-end
- Memory persists across restarts
- Skills can be added without modifying core
- Configuration reloadable without restart

---

*Last updated: 2026-03-29*