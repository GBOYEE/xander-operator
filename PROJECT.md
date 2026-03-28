# Xander Operator — Autonomous AI Agent

## Vision

Build a reliable, self‑improving AI operator that can execute tasks (browse, fill forms, research, send notifications) autonomously, learn from experience, and integrate securely with external systems.

## Goals (v1)

- Robust task execution with approval gates when needed
- Flexible skill registry (reusable procedures)
- Memory retrieval and reflection to improve over time
- Secure outbound notifications (Telegram)
- Continuous operation with `--loop`

## Non‑Goals

- Not a full OpenClaw gateway (separate project)
- Not a multi‑agent swarm (future consideration)

## Tech Stack

- Python 3.12
- Playwright (browser automation)
- SQLite (task store)
- Ollama / OpenAI (LLM for research)
- sentence‑transformers + FAISS (vector memory)
- Telegram Bot API

## Current State

Core classes implemented:
- `Operator` (browser context manager)
- `TaskStore` (SQLite: tasks, params, next_action)
- `telegram.Telegram` (sendMessage/sendDocument with retries)
- `skills.Skills` (registry, seeded with integrate_telegram_module)
- `memory.load_relevant_memory` (search logs/MEMORY.md)
- `reflect()` writes `[REFLECT]` to daily logs
- CLI supports `--loop` for autonomous polling

Outstanding:
- Systemd service unit
- Webhook receiver to enqueue tasks from GitHub/CI
- Improved error classification and retry policies
- Dashboard for task monitoring
