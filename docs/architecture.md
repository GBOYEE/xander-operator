# xander-operator Architecture

## Overview

xander-operator is a modular AI automation engine. It separates concerns into:

- **Planner**: Breaks tasks into steps (uses LLM)
- **Executor**: Runs steps by calling tools
- **Tool Registry**: Browse, fill, code, reason (each with permission level)
- **Memory**: Vector store for context (Chroma or FAISS)
- **Safety**: Approval queue, dry-run mode, workspace sandbox

## Data Flow

1. User submits task via CLI or API (`/run`)
2. Planner decomposes into tool calls
3. Executor runs each step, logs outcome
4. Memory updated with new context
5. Results returned; git commit created if changes made

## Deployment

- Docker image available
- Systemd service for background operation
- FastAPI server for remote usage

## Configuration

Environment variables:
- `XANDER_OPERATOR_MODEL` — LLM model (default: phi3:mini)
- `XANDER_WORKDIR` — workspace path (default: /workspace)
- `XANDER_DRY_RUN` — preview changes without writing
- `XANDER_ALLOW_SHELL` — enable shell commands (default: false)
- `OPENAI_API_KEY` — for OpenAI models
