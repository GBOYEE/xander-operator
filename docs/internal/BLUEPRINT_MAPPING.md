# Blueprint Mapping — "Eyes & Hands" to XANDER Operator

This document maps each concept from the quoted blueprint to our concrete design and files.

## 1. Intro (👀 See, ✋ Act)

- Blueprint: "Eyes = Browser + scraping + reading pages; Hands = Automation + clicking + typing + executing actions"
- Mapping:
  - Eyes → **Browser Agent** in `OPERATOR_ARCHITECTURE.md`, implemented in `operator.py` via `browse(url)`.
  - Hands → **Action Agent** in `OPERATOR_ARCHITECTURE.md`, implemented via `fill_form(url, selectors, values)`.
  - Scraping cleanup: optional **Smart Scraper** using BeautifulSoup (Phase 4).

---

## 2. Architecture Diagram

Blueprint:
```
YOU → ORCHESTRATOR → [BROWSER, RESEARCH, CODER, WRITER] → ACTION AGENT → REAL WORLD
```

Mapping:
- **YOU** = user / autonomy engine providing goals
- **ORCHESTRATOR** = `operator.py` (Phase 1), later `task_manager` + orchestrator
- **Agents** = Browser (done), Researcher (Phase 3), Coder/Writer (Phase 7)
- **ACTION AGENT** = separate layer (currently part of orchestrator in Phase 1; later its own module)
- **REAL WORLD** = websites, APIs

File: `OPERATOR_ARCHITECTURE.md` includes the full diagram and component breakdown.

---

## 3. Installation

Blueprint:
```
pip install playwright
playwright install
```

Mapping:
- Documented in `README.md` under Setup (not yet explicit; will add).
- We assume playwright installed on host.

---

## 4. Browser Agent (EYES)

Blueprint code:
```python
def browse(url):
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    content = page.content()
    browser.close()
    return content[:5000]
```

Mapping:
- Implemented in `operator.py` with slight improvements:
  - Returns `text` (inner_text) instead of raw HTML for cleaner extraction.
  - Still supports headless mode.
- Future: add `extract` field to specify selector.

---

## 5. Smart Scraper (BeautifulSoup)

Blueprint:
```python
from bs4 import BeautifulSoup
def extract_text(html):
  soup = BeautifulSoup(html, "html.parser")
  return soup.get_text()[:3000]
```

Mapping:
- Not implemented yet. Planned for **Phase 4** (Smart Scraper & Enhanced Browse).
- Could be optional dependency to keep Phase 1 minimal.

---

## 6. Action Agent (HANDS)

Blueprint code (anti-pattern):
```python
page.fill("input[name='username']", "your_username")
page.fill("input[name='password']", "your_password")
page.click("button[type='submit']")
```

Mapping:
- We **intentionally omitted** hard-coded credentials.
- Instead, `fill_form` uses task-provided values, and **requires human approval** before submit.
- This satisfies safety and DNA (no assumptions, no secrets in code).

---

## 7. Connect to Your Agent (enhanced_research)

Blueprint:
```python
def enhanced_research(task):
  web_results = researcher_agent(task)
  html = browse("https://example.com")
  return web_results + "\n\n[PAGE DATA]\n" + html[:1000]
```

Mapping:
- **Missing** in Phase 1.
- Will be added in **Phase 3** as a `research` task type with optional `follow_up_browse`.
- `researcher_agent` will use `web_search` tool + `browse` as needed.

---

## 8. Real Use Cases

Blueprint: Gitcoin bounty hunting, coding assistant, content writing, personal assistant.

Mapping:
- Documented as **Sample Tasks** in `README.md` (to be added).
- Will be first-class task types in later phases:
  - Coding → `code` tasks (Phase 7)
  - Writing → `write` tasks (Phase 7)
  - Personal assistant → combination of browse/fill/research.
  - Gitcoin bounties → specific automation scripts; may need custom agent.

---

## 9. Safety + Reality

Blueprint:
- Do NOT auto-submit, use real credentials without control, spam.
- Keep: human approval layer, logging system.

Mapping:
- **Human approval**: implemented in `fill_form` via `request_approval()` (Phase 1).
- **Logging**: daily logs + task updates (Phase 1).
- **No auto-submit**: we only submit after explicit yes.
- **No hard-coded credentials**: anti-pattern avoided by design.

---

## 10. Upgrade Brain (Critical) — Real-World Interaction Rules

Blueprint rules:
- Always read before acting
- Extract relevant data only
- Confirm before executing sensitive actions
- Log every action taken

Mapping:
- **Read before act**: `browse` reads page; `fill` fills then asks.
- **Extract relevant only**: by default returns full text; later `extract` field will allow selectivity.
- **Confirm before sensitive**: approval gate for fill (all are high-risk per SAFETY.md).
- **Log every action**: done via `log()` to daily file and task status updates.

---

## 11. Optional Insane Upgrades

Blueprint:
- Screen control
- Vision (screenshots)
- Auto GitHub interaction
- Telegram control panel
- Multi-step reasoning

Mapping:
- **Screenshots**: Phase 4 (browser agent enhancement).
- **Telegram control panel**: Phase 5 (OpenClaw skill integration).
- **Auto GitHub**: could be custom agent (Phase 7 or later).
- **Multi-step reasoning**: inherent in task breakdown; maybe enhanced with autofill patterns.
- **Voice & Yoruba personality**: handled at orchestrator output layer possibly; not needed for operator core.

---

## 12. What You Have Now (Blueprint Summary)

Blueprint: Brain (multi-agent system), Memory (vector + files), Awareness (web search).

Mapping:
- **Brain**: Orchestrator (Phase 1) + plan for agents.
- **Memory**: Daily logs (`memory/YYYY-MM-DD.md`) + task queue; no vector store; MEMORY.md will be curated later (Phase 6).
- **Awareness**: `web_search` tool exists in OpenClaw; we'll integrate in Phase 3 as researcher agent.

---

## 13. Task Manager Snippet

Blueprint:
```python
TASK_FILE = "memory/tasks.json"
load_tasks(), save_tasks(), add_task(task), get_next_task()
```

Mapping:
- Implemented in Phase 1 but simple.
- Full spec in `TASK_QUEUE_SPEC.md` (version 0.2) to be implemented in **Phase 2**.
- Phase 2 adds claim, update, subtasks, journaling.

---

## Additional DNA Alignment Not Explicit in Blueprint

Our design adds:
- **Risk registry** and approval gate (SAFETY.md).
- **Append-only journal** for audit (TASK_QUEUE_SPEC.md).
- **Context field** in tasks for project awareness.
- **Dependencies** for multi-step tasks.
- **Owner** field to distinguish user vs agent tasks.
- **Autonomy engine** (Phase 6) based on `AUTONOMY.md`.

---

## Gaps Relative to Blueprint

| Missing in our design | Blueprint mention | Phase to add |
|-----------------------|-------------------|--------------|
| BeautifulSoup scraper | Smart Scraper | Phase 4 |
| researcher_agent implementation | CONNECT section | Phase 3 |
| enhanced_research task type | CONNECT section | Phase 3 |
| Vector memory | "Memory (vector + files)" | Defer (not needed for MVP) |
| Multi-agent system fully separated | Orchestrator → agents | Gradual (Phases 3, 7) |
| Telegram control panel | OPTIONAL INSANE UPGRADE | Phase 5 |
| Auto GitHub interaction | OPTIONAL INSANE UPGRADE | Custom later |

We deliberately defer these to keep complexity low and deliver revenue faster.

---

## Conclusion

The blueprint's core concepts are fully represented in our design, with improvements for safety and DNA compliance. The difference is staging: we ship a minimal working operator first, then add research, code, writer, and control interfaces as needed.

All decisions documented in `OPERATOR_ARCHITECTURE.md`, `PROTOCOLS.md`, `TASK_QUEUE_SPEC.md`, `SAFETY.md`, `IMPLEMENTATION_PLAN.md`.
