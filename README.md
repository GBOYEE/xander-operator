# XANDER Operator

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status: MVP](https://img.shields.io/badge/status-MVP-green)

> An AI agent with eyes & hands: browse, fill forms, research, and remember.

XANDER is a DNA‑driven autonomous operator that can fetch web pages, submit forms with human approval, perform web research, and recall past actions via semantic vector memory.

---

## ✨ Features

- **🌐 Browse** – Fetch page content, extract text, headless or visible
- **📝 Fill** – Automate form submissions with human approval gate
- **🔍 Research** – Web search (DuckDuckGo) + optional deep dive on first result
- **🧠 Vector Memory** – Semantic recall over task history and logs (bge-base-en)
- **📓 Daily Logging** – Append‑only markdown records
- **📦 Task Queue** – JSON‑based, human‑editable, simple CRUD
- **🛡️ DNA Compliant** – Truth‑first, no assumptions, document everything, structured thinking

---

## 🚀 Quickstart

```bash
# 1. Install dependencies
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
playwright install chromium

# 2. Create a task in memory/tasks.json (see examples)

# 3. Run the operator
python3 xander_operator.py

# 4. Search memory (optional, requires vector deps)
python3 xander_operator.py --search "your query" --top 5
```

Detailed guide: [docs/quickstart.md](docs/quickstart.md)
Sample tasks: [docs/sample_tasks.json](docs/sample_tasks.json)

---

## 📁 Project Structure

```
workspace/
├── xander_operator.py   # Main orchestrator
├── researcher.py         # Research agent (DuckDuckGo)
├── vector_memory.py      # Optional vector memory (bge-base-en + FAISS)
├── scripts/
│   └── add_task.py       # CLI helper to add tasks
├── memory/               # Task queue & daily logs (gitignored)
├── docs/
│   ├── quickstart.md
│   ├── sample_tasks.json
│   └── internal/         # Design docs, specs, DNA, architecture
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📝 Task Format

Add JSON objects to `memory/tasks.json`:

### Browse

```json
{
  "id": "uuid",
  "type": "browse",
  "task": "Fetch example.com",
  "url": "https://example.com",
  "status": "pending",
  "created": "2025-03-26T12:00:00Z",
  "attempts": 0,
  "last_error": "",
  "result": null
}
```

### Fill

```json
{
  "id": "uuid",
  "type": "fill",
  "task": "Submit contact form",
  "url": "https://example.com/contact",
  "selectors": { "name": "input[name='name']" },
  "values": { "name": "XANDER" },
  "status": "pending",
  "created": "2025-03-26T12:00:00Z",
  "attempts": 0,
  "last_error": "",
  "result": null
}
```
Note: `fill` requires explicit approval before submission.

### Research

```json
{
  "id": "uuid",
  "type": "research",
  "task": "Find AI automation trends",
  "query": "AI automation trends 2024",
  "max_results": 5,
  "follow_up_browse": false,
  "status": "pending",
  "created": "2025-03-26T12:00:00Z",
  "attempts": 0,
  "last_error": "",
  "result": null
}
```

---

## 🛡️ Safety

- All `fill` tasks require explicit approval before submission.
- No hard‑coded credentials; use environment variables.
- Browser runs visible for fill actions; headless for browse.
- All actions logged; errors captured with context.

---

## 🧭 DNA Core Directives

1. Truth‑first: verify before acting.
2. Research before action.
3. Document everything.
4. Structured thinking.
5. Memory building.
6. Initiative mode.
7. Accountability system.
8. No assumptions.
9. Context awareness.
10. Efficiency.

Full text: [docs/internal/DNA.md](docs/internal/DNA.md)

---

## 📚 Documentation (Internal)

Design specifications, protocols, and implementation plans are located in `docs/internal/`:

- Architecture & components
- Protocols & schemas
- Safety policies
- Task queue spec
- Implementation roadmap
- Autonomy directives

---

## 📄 License

MIT. See `LICENSE` for details.

---

Built with ❤️ by XANDER, your Personal AI Partner.

---

## Usage

### Run the operator once

```bash
cd /root/.openclaw/workspace
python3 xander_operator.py
```

It will:
1. Fetch the first `pending` task.
2. If `type` is `browse` → open headless browser, extract page text, log result, mark `done`.
3. If `type` is `fill` → open visible browser, fill fields, **ask for approval** before submit, then submit if yes, log outcome, mark `done` or `failed`.
4. Append a log entry to `memory/YYYY-MM-DD.md`.
5. Exit.

### Search memory (vector semantic recall)

If you install optional dependencies:

```bash
pip install sentence-transformers faiss-cpu
```

Then you can semantically search across task results and daily logs:

```bash
python3 xander_operator.py --search "competitor price March" --top 5
```

Results are printed as JSON with scores and metadata.

Note: First search will be slow while the model loads (~400MB). Subsequent searches are fast.

### Create tasks

Edit `memory/tasks.json` manually with the task format shown above.

(We'll build a CLI helper later.)

---

## Approval Gate

For any form submission (type `fill`), the operator prints details and asks:

```
Approve? (yes/no):
```

No action is taken without explicit `yes`. This satisfies DNA safety rule: human approval layer for sensitive actions.

---

## Logging

Each run appends to the daily memory file:

```
[2025-03-26 13:15] ▶️  Starting task 123e4567: Check product price
[2025-03-26 13:15] ✅ browse https://shop.example.com/item/123 → 3421 chars
[2025-03-26 13:15] 🛑 Operator run complete
```

If errors occur, they are logged with warnings.

---

## DNA Compliance Checklist

| Directive | How it's met |
|-----------|--------------|
| TRUTH-FIRST | No guessing; we actually browse and extract real data |
| RESEARCH BEFORE ACTION | For fill tasks, human reviews details before approval |
| DOCUMENT EVERYTHING | Daily logs capture outcomes; task updates persist state |
| STRUCTURED THINKING | Task schema enforces structure; clear branching by type |
| MEMORY BUILDING | Daily logs feed MEMORY.md; task history is persistent |
| INITIATIVE MODE | (future: heartbeat polling) |
| ACCOUNTABILITY SYSTEM | Task queue with status, attempts, errors |
| NO ASSUMPTIONS | Approval required for form submit; errors caught |
| CONTEXT AWARENESS | Task carries URL, selectors, values; operator respects them |
| EFFICIENCY | Reusable code; single script; no infrastructure |

---

## Next Steps (Roadmap)

1. **Add Telegram trigger** — run operator via `/do task_id` from Telegram.
2. **Enhance task manager** — `claim_next_task(agent_type)`, priorities, subtasks.
3. **Add research agent** — search + scrape + summarize.
4. **Build coder/writer agents** — reuse templates.
5. **Integrate MEMORY.md** — distill daily logs into long-term memory periodically.

---

## Philosophy

Simple systems survive. This MVP is deliberately minimal: one file, one dependency (Playwright), one queue (JSON). It can be understood, modified, and trusted. Complexity comes later, only when needed.

---

XANDER 🦊 — Your Personal AI Partner
DNA-driven, OpenClaw-native
