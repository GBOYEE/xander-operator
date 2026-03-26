# XANDER Operator

> An AI agent with eyes & hands: browse, fill forms, research, and remember.

XANDER is a DNA‑driven autonomous operator that can fetch web pages, submit forms with human approval, perform web research, and recall past actions via semantic vector memory.

---

## ✨ Features

- **Browse** – Fetch page content, extract text, headless or visible
- **Fill** – Automate form submissions with human approval gate
- **Research** – Web search + optional deep dive on first result
- **Vector Memory** – Semantic recall over task history and logs
- **Daily Logging** – Append-only markdown records
- **Task Queue** – JSON‑based, human‑editable
- **DNA Compliant** – Truth‑first, no assumptions, document everything

---

## 🚀 Quickstart

```bash
# 1. Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. Create a task in memory/tasks.json (see examples)

# 3. Run the operator
python3 xander_operator.py

# 4. Search memory (optional, requires vector deps)
python3 xander_operator.py --search "your query" --top 5
```

---

## 📁 Project Structure

```
workspace/
├── xander_operator.py   # Main orchestrator
├── researcher.py         # Research agent (DuckDuckGo)
├── vector_memory.py      # Optional vector memory (bge-base-en + FAISS)
├── memory/
│   ├── tasks.json        # Task queue
│   └── 2026-03-26.md    # Daily log
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📝 Task Format

Add JSON objects to `memory/tasks.json`:

```json
{
  "id": "uuid",
  "type": "browse | fill | research",
  "task": "Description",
  "status": "pending",
  "created": "2025-03-26T12:00:00Z"
}
```

**Browse**
```json
{ "type": "browse", "url": "https://example.com" }
```

**Fill**
```json
{
  "type": "fill",
  "url": "https://example.com/contact",
  "selectors": { "name": "input[name='name']" },
  "values": { "name": "XANDER" }
}
```

**Research**
```json
{
  "type": "research",
  "query": "AI automation trends 2024",
  "max_results": 5,
  "follow_up_browse": false
}
```

---

## 🛡️ Safety

- All `fill` tasks require explicit approval before submission.
- No hard‑coded credentials; use environment variables.
- Browser runs visible for fill actions; headless for browse.
- All actions logged; errors captured with context.

---

## 📊 DNA Core Directives

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

*(Full text in `DNA.md`)*

---

## 🧭 Roadmap

- Phase 1: MVP (browse, fill, research, vector) — **done**
- Phase 2: Enhanced task manager (claims, journaling)
- Phase 3: Telegram control panel
- Phase 4: Coder & Writer agents
- Phase 5: Autonomy engine

---

## 📄 License

MIT. See `LICENSE` for details.

---

Built with ❤️ by XANDER, your Personal AI Partner.
