#!/usr/bin/env python3
"""
XANDER Operator MVP — Eyes & Hands, production‑hardened.
Safe browser automation with human approval, vector memory, and structured daily logs.
"""

import json
import os
import sys
import sqlite3
import logging
import argparse
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from typing import Optional, Dict, Any, List

from playwright.sync_api import sync_playwright

# Optional vector memory
try:
    from vector_memory import index_task as vm_index_task, index_log_entry as vm_index_log, search_memory
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False

# Optional researcher agent
try:
    from researcher import research as researcher_research
    RESEARCHER_AVAILABLE = True
except ImportError:
    RESEARCHER_AVAILABLE = False

# ==================== CONFIGURATION ====================
def _get_workspace() -> Path:
    return Path(os.getenv("XANDER_WORKSPACE", Path.home() / ".openclaw" / "workspace")).expanduser()

WORKSPACE = _get_workspace()
MEMORY_DIR = WORKSPACE / "memory"
DB_FILE = MEMORY_DIR / "tasks.db"
LOG_FILE = MEMORY_DIR / f"{datetime.now():%Y-%m-%d}.md"

# Ensure memory directory exists
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# ==================== TASK STORE (SQLite) ====================
class TaskStore:
    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = Path(db_path)
        self._init_db()
        self._migrate_legacy()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    desc TEXT NOT NULL,
                    type TEXT NOT NULL,
                    url TEXT,
                    selectors TEXT,  -- JSON
                    values TEXT,     -- JSON
                    status TEXT DEFAULT 'pending',
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    attempts INTEGER DEFAULT 0,
                    last_error TEXT,
                    result TEXT  -- JSON
                )
            """)
            conn.commit()

    def _migrate_legacy(self):
        legacy = self.db_path.parent / "tasks.json"
        if legacy.exists():
            try:
                # Check if we already have tasks
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.execute("SELECT COUNT(*) FROM tasks")
                    count = cur.fetchone()[0]
                    if count > 0:
                        return  # already have data
                # Import legacy tasks
                data = json.loads(legacy.read_text())
                tasks = data.get("tasks", [])
                with sqlite3.connect(self.db_path) as conn:
                    for t in tasks:
                        selectors_json = json.dumps(t.get("selectors", {}))
                        values_json = json.dumps(t.get("values", {}))
                        result_json = json.dumps(t.get("result")) if t.get("result") is not None else None
                        conn.execute("""
                            INSERT OR REPLACE INTO tasks
                            (id, desc, type, url, selectors, values, status, created, attempts, last_error, result)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            t["id"],
                            t.get("task") or t.get("desc", ""),
                            t["type"],
                            t.get("url"),
                            selectors_json,
                            values_json,
                            t.get("status", "pending"),
                            t.get("created", datetime.utcnow().isoformat()),
                            t.get("attempts", 0),
                            t.get("last_error", ""),
                            result_json
                        ))
                    conn.commit()
                log.info(f"Migrated {len(tasks)} tasks from legacy tasks.json")
            except Exception as e:
                log.warning(f"Failed to migrate legacy tasks: {e}")

    def add_task(self, desc: str, task_type: str, url: Optional[str] = None,
                 selectors: Optional[Dict] = None, values: Optional[Dict] = None, **extra) -> str:
        task_id = str(uuid4())
        selectors_json = json.dumps(selectors or {})
        values_json = json.dumps(values or {})
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tasks (id, desc, type, url, selectors, values, status, created, attempts, last_error, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id, desc, task_type, url, selectors_json, values_json,
                'pending', datetime.utcnow().isoformat(), 0, '', None
            ))
            conn.commit()
        log.info(f"Added task {task_id[:8]}: {desc}")
        return task_id

    def get_pending(self) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM tasks WHERE status='pending' ORDER BY created LIMIT 1")
            row = cur.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cur.description]
            task = dict(zip(columns, row))
            # Parse JSON fields
            task['selectors'] = json.loads(task['selectors'] or '{}')
            task['values'] = json.loads(task['values'] or '{}')
            if task['result']:
                task['result'] = json.loads(task['result'])
            # Rename desc -> task for compatibility
            task['task'] = task.pop('desc')
            return task

    def get_task(self, task_id: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
            row = cur.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cur.description]
            task = dict(zip(columns, row))
            task['selectors'] = json.loads(task['selectors'] or '{}')
            task['values'] = json.loads(task['values'] or '{}')
            if task['result']:
                task['result'] = json.loads(task['result'])
            task['task'] = task.pop('desc')
            return task

    def update_task(self, task_id: str, updates: Dict):
        fields = []
        values = []
        for k, v in updates.items():
            if k in ('selectors', 'values') and isinstance(v, dict):
                v = json.dumps(v)
            elif k == 'result' and isinstance(v, (dict, list)):
                v = json.dumps(v)
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(task_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
            # Index in vector memory if available and relevant fields changed
            if VECTOR_AVAILABLE and ('result' in updates or 'status' in updates):
                try:
                    updated = self.get_task(task_id)
                    if updated:
                        vm_index_task(updated)
                except Exception as e:
                    log.warning(f"Vector indexing failed: {e}")
        log.info(f"Updated task {task_id[:8]}: {updates}")

# Default store (can be overridden by --workspace)
_task_store = TaskStore(DB_FILE)

# Backwards‑compatible function API
def add_task(task_desc, task_type, url=None, selectors=None, values=None, **extra):
    return _task_store.add_task(task_desc, task_type, url, selectors, values, **extra)

def load_tasks():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT * FROM tasks ORDER BY created")
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        tasks = []
        for row in rows:
            t = dict(zip(cols, row))
            t['selectors'] = json.loads(t['selectors'] or '{}')
            t['values'] = json.loads(t['values'] or '{}')
            if t['result']:
                t['result'] = json.loads(t['result'])
            t['task'] = t.pop('desc')
            tasks.append(t)
        return tasks

def get_next_task():
    return _task_store.get_pending()

def update_task(task_id, updates):
    return _task_store.update_task(task_id, updates)

def log(message: str):
    """Legacy logging function kept for compatibility."""
    logging.getLogger(__name__).info(message)

# ==================== OPERATOR CLASS ====================
class Operator:
    """
    Context manager for browser operations. Reuses a single browser instance
    for multiple tasks to reduce startup overhead.
    """
    def __init__(self, require_approval: bool = True):
        self.require_approval = require_approval
        self._playwright = None
        self._browser = None

    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def browse(self, url: str, max_chars: int = 5000) -> str:
        page = self._browser.new_page()
        try:
            page.goto(url, timeout=30000)
            text = page.inner_text("body")
            return text[:max_chars]
        finally:
            page.close()

    def fill_form(self, url: str, selectors: Dict[str, str], values: Dict[str, str]) -> bool:
        if self.require_approval and not request_approval(
            task_desc=f"fill {url}",
            url=url,
            action_details=f"Submit form fields: {list(selectors.keys())}"
        ):
            log.info("Form submission rejected by user")
            return False
        page = self._browser.new_page()
        try:
            page.goto(url, timeout=30000)
            for field, sel in selectors.items():
                val = values.get(field, "")
                page.fill(sel, val)
            # Try common submit selectors
            for sel in [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Send")'
            ]:
                try:
                    if page.query_selector(sel):
                        page.click(sel)
                        break
                except:
                    continue
            log.info("Form submitted successfully")
            return True
        except Exception as e:
            log.error(f"Form fill error: {e}")
            return False
        finally:
            page.close()

# ==================== APPROVAL GATE ====================
def request_approval(task_desc: str, url: str, action_details) -> bool:
    """
    Human approval gate. Override with XANDER_AUTO_APPROVE=true.
    """
    if os.getenv("XANDER_AUTO_APPROVE", "").lower() in ("1", "true", "yes"):
        return True
    print("\n" + "="*60)
    print(f"🔴 ACTION REQUIRES APPROVAL")
    print(f"Task: {task_desc}")
    print(f"URL:  {url}")
    print(f"Will: {action_details}")
    print("="*60)
    resp = input("Approve? (yes/no): ").strip().lower()
    return resp in ("yes", "y")

# ==================== ORCHESTRATOR ====================
def run_once():
    task = get_next_task()
    if not task:
        log.info("No pending tasks")
        return

    task_id = task["id"]

    # Validate task (v1.1.0: input validation & safety detectors)
    try:
        from . import detectors
        issues = detectors.validate_task(task)
        if issues:
            error_msg = "; ".join(issues)
            log.error(f"Task validation failed: {error_msg}")
            update_task(task_id, {"status": "failed", "last_error": error_msg})
            return
        safety_warnings = detectors.safety_check(task)
        if safety_warnings:
            log.warning(f"Safety warnings: {'; '.join(safety_warnings)}")
    except Exception as e:
        log.exception("Validation error")
        update_task(task_id, {"status": "failed", "last_error": f"validation error: {e}"})
        return

    update_task(task_id, {"status": "in_progress", "attempts": task.get("attempts", 0) + 1})
    log.info(f"Starting task {task_id[:8]}: {task['task']}")

    try:
        if task["type"] == "browse":
            with Operator(require_approval=True) as op:
                result = op.browse(task["url"])
            update_task(task_id, {"status": "done", "result": result[:1000]})
            log.info(f"Browse completed: {len(result)} chars")

        elif task["type"] == "fill":
            with Operator(require_approval=True) as op:
                success = op.fill_form(task["url"], task["selectors"], task["values"])
            new_status = "done" if success else "failed"
            update_task(task_id, {"status": new_status, "result": success})
            log.info(f"Fill form {'succeeded' if success else 'failed'}")

        elif task["type"] == "research":
            if not RESEARCHER_AVAILABLE:
                log.error("Researcher module not available")
                update_task(task_id, {"status": "failed", "last_error": "researcher missing"})
            else:
                query = task.get("query") or task.get("task")
                max_results = task.get("max_results", 5)
                follow_up = task.get("follow_up_browse", False)
                try:
                    result = researcher_research(query, max_results=max_results, follow_up_browse=follow_up)
                    if result.get("success"):
                        summary = f"research '{query}' → {len(result.get('sources', []))} sources"
                        log.info(summary)
                        update_task(task_id, {"status": "done", "result": {
                            "answer": result.get("answer", "")[:2000],
                            "sources": result.get("sources", [])[:10],
                            "first_page_text": result.get("first_page_text", "")[:1000] if result.get("first_page_text") else None
                        }})
                    else:
                        log.warning(f"Research failed: {result.get('answer')}")
                        update_task(task_id, {"status": "failed", "last_error": result.get("answer", "research error")})
                except Exception as e:
                    log.exception("Research exception")
                    update_task(task_id, {"status": "failed", "last_error": str(e)})
        else:
            log.warning(f"Unknown task type: {task['type']}")
            update_task(task_id, {"status": "failed", "last_error": "unknown type"})

    except Exception as e:
        log.exception("Unexpected error in run_once")
        update_task(task_id, {"status": "failed", "last_error": str(e)})

# ==================== CLI ====================
def main():
    parser = argparse.ArgumentParser(description="XANDER Operator")
    parser.add_argument("--workspace", type=str, help="Workspace directory (overrides XANDER_WORKSPACE)")
    parser.add_argument("--search", action="store_true", help="Search vector memory instead of running")
    parser.add_argument("query", nargs="*", help="Search query if --search")
    parser.add_argument("--top", type=int, default=5, help="Number of search results (default 5)")
    parser.add_argument("--auto-approve", action="store_true", help="Skip approval prompt (for CI)")
    parser.add_argument("--report", action="store_true", help="Generate HTML report after execution")
    args = parser.parse_args()

    # Override workspace if provided
    if args.workspace:
        os.environ["XANDER_WORKSPACE"] = args.workspace
        # Re‑compute paths
        global WORKSPACE, MEMORY_DIR, DB_FILE, LOG_FILE, _task_store
        WORKSPACE = _get_workspace()
        MEMORY_DIR = WORKSPACE / "memory"
        DB_FILE = MEMORY_DIR / "tasks.db"
        LOG_FILE = MEMORY_DIR / f"{datetime.now():%Y-%m-%d}.md"
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        # Reconfigure logging
        logging.getLogger().handlers = []
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(LOG_FILE, mode='a'), logging.StreamHandler(sys.stdout)]
        )
        _task_store = TaskStore(DB_FILE)

    if args.auto_approve:
        os.environ["XANDER_AUTO_APPROVE"] = "1"

    if args.search:
        if not VECTOR_AVAILABLE:
            print("❌ Vector memory dependencies not installed. Install sentence-transformers and faiss.")
            sys.exit(1)
        query = " ".join(args.query)
        if not query.strip():
            print("Usage: operator.py --search <query>")
            sys.exit(1)
        results = search_memory(query, k=args.top)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    log.info("🔧 Operator booting")
    run_once()
    if args.report:
        try:
            from . import reporter
            report_path = reporter.generate_report(store=_task_store)
            log.info(f"HTML report generated: {report_path}")
        except Exception as e:
            log.exception("Failed to generate HTML report")
    log.info("✅ Operator run complete")

if __name__ == "__main__":
    main()
