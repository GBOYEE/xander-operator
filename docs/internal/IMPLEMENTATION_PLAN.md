# Implementation Plan — XANDER Operator MVP

Phased rollout: minimal first, then iterative enhancements aligned with DNA.

---

## Phase 0: Documentation (Now)

**Goal:** Establish design and contracts before code.

Deliverables:
- [x] OPERATOR_ARCHITECTURE.md
- [x] PROTOCOLS.md
- [x] TASK_QUEUE_SPEC.md
- [x] SAFETY.md
- [ ] IMPLEMENTATION_PLAN.md (this doc finalization)

**Review:** User approval of architecture before proceeding.

---

## Phase 1: Foundation (MVP — Current)

**Goal:** Single-script operator that can browse and fill forms with approval.

Deliverables:
- [x] operator.py (initial version)
- [x] memory/tasks.json template
- [x] Basic logging to daily file

**Acceptance Criteria:**
- Can add a `browse` task → runs headless, returns text, logs success.
- Can add a `fill` task → opens visible browser, fills fields, prompts for approval, submits if yes, logs outcome.
- Fails gracefully on errors, writes to `last_error`, marks `failed`.
- Daily log contains clear timestamps and messages.

**Limitations:**
- Task manager uses simple load/save (no atomic claims)
- No researcher, coder, writer agents
- No multi-task orchestration (one run = one task)
- No heartbeat/autonomy (manual run)

---

## Phase 2: Task Manager Module

**Goal:** Replace simple load/save with full task_manager API.

Deliverables:
- `task_manager.py` implementing:
  - `add_task`, `get_next_task`, `claim_task`, `update_task`, `add_subtask`, `list_tasks`, `retry_failed`
- Append-only `task_log.jsonl`
- Migration script to move existing tasks.json to new format (version 0.2)
- Unit tests (pytest) for core task flows

**Acceptance Criteria:**
- operator.py uses task_manager instead of direct JSON.
- claim_task prevents multiple in_progress for same task.
- task_log.jsonl persists every mutation.
- Tests pass for create → claim → update → retry.

---

## Phase 3: Researcher Agent

**Goal:** Add web search integration.

Deliverables:
- `researcher.py` agent:
  - `research(query, max_results=5)` → uses `web_search` tool
  - Returns structured sources + answer
- New task type `research` in task spec
- Orchestrator dispatch branch for research
- Optional `follow_up_browse` to visit first result

**Acceptance Criteria:**
- Task type `research` executes and returns answer with sources.
- Result stored in task.result.
- Logged appropriately.

---

## Phase 4: Smart Scraper & Enhanced Browse

**Goal:** Clean HTML extraction and configurable behaviors.

Deliverables:
- Optional BeautifulSoup integration in browser agent: `extract_text(html)` helper.
- `browse` task spec gains `extract` field (CSS selector or 'text' or 'all').
- Screenshot option (`screenshot: true`) saves PNG to `memory/screenshots/`.
- Better error messages (selector not found, timeout).

**Acceptance Criteria:**
- Can extract specific elements by CSS selector.
- Screenshots saved when requested.
- Operator still DNA-compliant (no assumptions, logs).

---

## Phase 5: Human Approval & Telegram Integration

**Goal:** Enable remote control and notifications.

Deliverables:
- OpenClaw Telegram skill integration: operator can be triggered via `/do <task_id>` or `/run`.
- Approval messages sent to user chat; replies `/approve` or `/deny` interpreted.
- Operator can run as background daemon (loop with sleep) when triggered persistently.
- Heartbeat file check (optional).

**Acceptance Criteria:**
- User can start operator from Telegram.
- Approval prompts appear in chat; user responds; operator respects decision.
- Operator can run in continuous loop (configurable interval).

---

## Phase 6: Autonomy Engine (Idle Initiative)

**Goal:** Generate tasks from goals without waiting.

Deliverables:
- `autonomy.py` module:
  - Periodically (idle hook) reads `MEMORY.md` and pending goals.
  - Breaks goals into tasks using structured thinking.
  - Submits tasks to queue via task_manager.
  - Respects rate limits and dependencies.
- Configuration: which goals are active, generation frequency.

**Acceptance Criteria:**
- With no pending tasks, operator generates next logical task for current project.
- New task appears in tasks.json with reasonable spec.
- Logs "autonomy suggestion: ..."

---

## Phase 7: Coder & Writer Agents (Optional)

**Goal:** Support creation tasks.

Deliverables:
- `coder.py`: generate code from spec using templates or LLM calls.
- `writer.py`: draft content from topic + research notes.
- Task types `code` and `write` implemented.
- Templates stored in `templates/` directory.

**Acceptance Criteria:**
- Code tasks produce runnable files.
- Writer tasks produce markdown drafts.
- Both types log outputs and store results.

---

## Phase 8: Production Hardening

**Goal:** Make it robust for revenue-critical usage.

Deliverables:
- Error handling: retries with backoff, circuit breaker patterns.
- Metrics: success rate per agent, task duration.
- Health check endpoint (if running as daemon).
- Backup/restore for tasks and logs.
- Improved secrets management: integrate OpenClaw vault or .env with encryption.

**Acceptance Criteria:**
- System runs for 30 days without manual intervention.
- Alerts on repeated failures.
- Can restore from backup without data loss.

---

## Staging Strategy

- **Week 1:** Phase 1 + one real task delivered (revenue).
- **Week 2:** Phase 2 + Phase 3 (research capability).
- **Week 3:** Phase 4 + Phase 5 (Telegram control).
- **Week 4:** Phase 6 (autonomy) + refine based on usage.
- **Month 2:** Phase 7–8 as needed.

KEEP IT SIMPLE. Ship early. Iterate with user feedback.

---

## Dependencies

- Playwright installed (`pip install playwright && playwright install chromium`)
- Python 3.10+
- Optional: BeautifulSoup (`pip install beautifulsoup4`)
- OpenClaw Telegram integration (phase 5)

---

## Success Metrics

- Tasks completed / week
- Average time from creation to completion
- Approval latency (time to /approve)
- Autonomy task acceptance rate (user keeps them)

---

Begin with Phase 0 review. Ready to move to Phase 1 implementation upon approval.
