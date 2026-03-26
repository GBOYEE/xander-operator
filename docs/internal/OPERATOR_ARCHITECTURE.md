# XANDER Operator Architecture

## Vision

A modular, DNA-compliant “eyes & hands” system: perceive web pages, reason about tasks, take approved actions, learn from results, and operate autonomously toward user goals.

## Core Principles (from DNA)

- Truth-first: always verify with real sources
- Research before action: validate approach
- Document everything: persistent logs
- Structured thinking: break down problems
- Memory building: update long-term memory
- Initiative mode: suggest next steps when idle
- Accountability system: track goals, tasks, missed actions
- No assumptions: ask → research → confirm
- Context awareness: relate to current project
- Efficiency: reuse, automate, template

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                      USER / you                          │
└───────────────────────┬─────────────────────────────────┘
                        │ goals, approvals, feedback
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR (brain)                   │
│  • Receives goals from user or autonomy engine         │
│  • Breaks goals into tasks                              │
│  • Dispatches tasks to appropriate agent               │
│  • Enforces approval gates for high-risk actions       │
│  • Logs outcomes, updates memory                        │
└───────┬─────────────┬─────────────┬─────────────┬──────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌──────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────┐
│ Browser Agent│ │Researcher  │ │ Coder    │ │ Writer     │
│ (EYES)       │ │ Agent      │ │ Agent    │ │ Agent      │
│              │ │            │ │          │ │            │
│ • Navigate   │ │• Search    │ │• Write   │ │• Draft     │
│ • Extract    │ │• Scrape    │ │  code    │ │  content   │
│ • Screenshot │ │• Summarize │ │• Test    │ │• Format    │
└──────┬───────┘ └─────┬──────┘ └────┬─────┘ └─────┬──────┘
       │               │              │              │
       └───────────────┴──────────────┴──────────────┘
                        │
                        ▼
            ┌─────────────────────┐
            │   Action Agent      │
            │   (HANDS)           │
            │                     │
            │ • Fill forms        │
            │ • Click buttons     │
            │ • Submit            │
            │ • Execute commands  │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │   REAL WORLD        │
            │   websites, files,  │
            │   APIs, systems     │
            └─────────────────────┘
```

## Data Flow

1. **Goal Intake**
   - User provides goal via chat
   - Autonomy engine generates tasks during idle periods
2. **Task Breakdown**
   - Orchestrator uses STRUCTURED THINKING:
     - Goal → Constraints → Options → Best decision
   - Produces one or more task objects, each with:
     - type (browse, research, fill, code, write, etc.)
     - parameters (url, selectors, values, prompts)
     - context (project, priority, dependencies)
3. **Agent Selection**
   - Orchestrator routes task to agent based on type
   - Each agent runs in isolation, returns JSON result
4. **Execution**
   - EYES agents (browser, researcher) read-only, no approval needed
   - HANDS agents (action) always require human approval unless explicitly whitelisted low-risk
5. **Logging**
   - Every step writes to daily memory file
   - Task status updated in task queue
6. **Memory Update**
   - Significant outcomes distilled into MEMORY.md
   - Learnings stored (templates, selector strategies, error patterns)
7. **Feedback Loop**
   - If task fails, orchestrator can retry (up to max attempts) or mark failed
   - If idle, autonomy engine analyzes goals → generates new tasks

## Component Details

### Orchestrator (operator.py)

**Responsibilities:**
- Load tasks from `memory/tasks.json`
- Pick next pending task (respecting dependencies)
- Call correct agent function
- Handle exceptions, enforce retry limits
- Update task status, record result
- Write to daily log

**Runtime:**
- Single-run (reactive) initially; later daemon with heartbeat
- No complex threads; simple loop

### Browser Agent (EYES)

- Uses Playwright
- Two modes:
  - `browse(url)` → returns full page text (headless)
  - `screenshot(url, path)` → captures PNG (visible for debug)
- Returns: `{ "success": true, "content": "...", "url": "...", "error": null }`
- Errors include stack trace and screenshot path

### Researcher Agent

- Integrates `web_search` tool
- For a query, fetch top N results, summarize each, produce concise answer
- Returns: `{ "query": "...", "sources": [...], "answer": "..." }`
- Optionally can follow up with `browse()` on first result (enhanced_research)

### Coder Agent

- Takes specification, uses templates to generate code
- May run in sandboxed environment (future)
- Returns: `{ "files": { "main.py": "...", ... }, "tests": "..." }`

### Writer Agent

- Takes topic, research notes, outline → produce draft
- Format: markdown, plain text, or platform-specific
- Returns: `{ "title": "...", "body": "..." }`

### Action Agent (HANDS)

- Wrapper around Playwright with approval gate
- Supported actions:
  - `fill_form(url, selectors, values)` → submit after approval
  - `click(selector)` → click element
  - `download(url, dest)` → save file (only after approval)
- Risk registry determines approval requirement:
  - High: form submit, navigation away from site, download
  - Low: fill without submit, read-only clicks

### Task Queue (`memory/tasks.json`)

Enhanced schema (see TASK_QUEUE_SPEC.md).

### Memory System

- Daily logs: `memory/YYYY-MM-DD.md` — chronological
- Long-term: `MEMORY.md` — curated insights, project context, user preferences
- Task history: `memory/tasks.json` + `memory/task_log.json` (append-only for recovery)

## Safety & Security

- Human approval for all HANDS actions by default
- Never hard-code credentials; use environment variables or secret manager
- Browser actions run with `headless=False` initially for transparency
- All external requests logged with URL and timestamp
- No auto-retry for failed sensitive actions without re-approval

## Tech Stack

- Python 3.10+
- Playwright (`pip install playwright && playwright install`)
- Requests/httpx (if needed)
- Optional: BeautifulSoup (scraping cleanup)
- Storage: JSON files initially; later SQLite for queryability

## Deployment

- Run on host (same machine as OpenClaw) initially
- No containers for MVP; later Docker for isolation
- Trigger via:
  - CLI: `python operator.py`
  - Telegram integration (phase 3)
  - Cron (periodic tasks)
  - Heartbeat (background daemon)

## Open Questions (To Resolve)

- Should we use `web_search` tool directly or wrap it?
- Where do we store credentials (OpenClaw config? .env file?)
- How to handle selectors that change (dynamic CSS)? resilience strategy.
- Should operator run as daemon or on-demand? (Start on-demand, later background)
- Do we need separate task file per project or single global? (Single with context field)
- How to handle multi-step tasks (workflows)? (subtasks or state machine)

---

Next: Detailed specs for protocols, task queue, safety, and implementation plan.
