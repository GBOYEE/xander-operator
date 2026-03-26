#!/usr/bin/env python3
"""
XANDER Operator MVP — Eyes & Hands, DNA-compliant.
最小可行操作员：浏览、填充、人工审批、日志、任务跟踪。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

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

# ==================== CONFIG ====================
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
TASK_FILE = MEMORY_DIR / "tasks.json"
LOG_FILE = MEMORY_DIR / f"{datetime.now():%Y-%m-%d}.md"

# ==================== TASK MANAGER ====================
def load_tasks():
    if TASK_FILE.exists():
        try:
            data = json.loads(TASK_FILE.read_text())
            return data.get("tasks", [])
        except Exception as e:
            log(f"⚠️  Task load failed: {e}")
            return []
    return []

def save_tasks(tasks):
    data = {"tasks": tasks, "version": "0.1"}
    TASK_FILE.write_text(json.dumps(data, indent=2))

def get_next_task():
    tasks = load_tasks()
    for t in tasks:
        if t.get("status") == "pending":
            return t
    return None

def update_task(task_id, updates):
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks[i].update(updates)
            save_tasks(tasks)
            # Index this task if it has a result and vector memory available
            try:
                if VECTOR_AVAILABLE and ("result" in updates or "status" in updates):
                    # Re-fetch the updated task to include result
                    updated = load_tasks()
                    task_updated = next((tt for tt in updated if tt["id"] == task_id), None)
                    if task_updated:
                        vm_index_task(task_updated)
            except Exception:
                pass
            return True
    return False

def add_task(task_desc, task_type, url=None, selectors=None, values=None, **extra):
    task = {
        "id": str(uuid4()),
        "task": task_desc,
        "type": task_type,
        "url": url,
        "selectors": selectors or {},
        "values": values or {},
        "status": "pending",
        "created": datetime.now().isoformat(),
        "attempts": 0,
        "last_error": "",
        "result": None
    }
    task.update(extra)  # allow research-specific fields
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    return task["id"]

# ==================== LOGGING ====================
def log(message: str):
    """Append to daily memory log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] {message}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    # Index to vector memory if available
    try:
        if VECTOR_AVAILABLE:
            vm_index_log(entry, {"source": "daily_log", "date": LOG_FILE.stem})
    except Exception:
        pass  # vector indexing should not break logging

def request_approval(task_desc, url, action_details) -> bool:
    """
    Human approval gate. Blocks execution until explicit YES.
    Returns True if approved, False otherwise.
    """
    print("\n" + "="*60)
    print(f"🔴 ACTION REQUIRES APPROVAL")
    print(f"Task: {task_desc}")
    print(f"URL:  {url}")
    print(f"Will: {action_details}")
    print("="*60)
    resp = input("Approve? (yes/no): ").strip().lower()
    return resp in ("yes", "y")

# ==================== BROWSER AGENT (EYES) ====================
def browse(url: str, max_chars: int = 5000) -> str:
    """Navigate and return page content."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)
            content = page.content()
            text = page.inner_text("body")
            browser.close()
            return text[:max_chars]
        finally:
            browser.close()

def fill_form(url: str, selectors: dict, values: dict) -> bool:
    """Fill fields and submit after approval."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible for safety
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)

            # Fill each field
            for field, selector in selectors.items():
                value = values.get(field, "")
                page.fill(selector, value)

            # Approval before submit
            if not request_approval(
                task_desc=f"fill {url}",
                url=url,
                action_details=f"Submit form with keys: {list(selectors.keys())}"
            ):
                log("❌ Action rejected by user")
                return False

            # Find submit button if present
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Send")'
            ]
            for sel in submit_selectors:
                try:
                    if page.query_selector(sel):
                        page.click(sel)
                        break
                except:
                    continue

            log("✅ Form submitted successfully")
            return True
        except Exception as e:
            log(f"⚠️  Browser error: {e}")
            return False
        finally:
            browser.close()

# ==================== ORCHESTRATOR LOOP ====================
def run_once():
    task = get_next_task()
    if not task:
        log("💤 No pending tasks")
        return

    task_id = task["id"]
    update_task(task_id, {"status": "in_progress", "attempts": task.get("attempts", 0) + 1})

    log(f"▶️  Starting task {task_id[:8]}: {task['task']}")

    try:
        if task["type"] == "browse":
            result = browse(task["url"])
            summary = f"browse {task['url']} → {len(result)} chars"
            log(f"✅ {summary}")
            update_task(task_id, {"status": "done", "result": result[:1000]})

        elif task["type"] == "fill":
            success = fill_form(task["url"], task["selectors"], task["values"])
            if success:
                update_task(task_id, {"status": "done", "result": "submitted"})
            else:
                update_task(task_id, {"status": "failed", "last_error": "action rejected or error"})

        elif task["type"] == "research":
            if not RESEARCHER_AVAILABLE:
                log("❌ Researcher not available (missing dependencies)")
                update_task(task_id, {"status": "failed", "last_error": "researcher module missing"})
            else:
                query = task.get("query") or task.get("task")
                max_results = task.get("max_results", 5)
                follow_up = task.get("follow_up_browse", False)
                try:
                    result = researcher_research(query, max_results=max_results, follow_up_browse=follow_up)
                    if result.get("success"):
                        summary = f"research '{query}' → {len(result.get('sources', []))} sources"
                        log(f"✅ {summary}")
                        # Store only essential result to keep task size reasonable
                        update_task(task_id, {"status": "done", "result": {
                            "answer": result.get("answer", "")[:2000],
                            "sources": result.get("sources", [])[:10],
                            "first_page_text": result.get("first_page_text", "")[:1000] if result.get("first_page_text") else None
                        }})
                    else:
                        log(f"❌ research failed: {result.get('answer')}")
                        update_task(task_id, {"status": "failed", "last_error": result.get("answer", "research error")})
                except Exception as e:
                    log(f"💥 Research error: {e}")
                    update_task(task_id, {"status": "failed", "last_error": str(e)})

        else:
            log(f"❌ Unknown task type: {task['type']}")
            update_task(task_id, {"status": "failed", "last_error": "unknown type"})

    except Exception as e:
        err = str(e)
        log(f"💥 Unexpected error: {err}")
        update_task(task_id, {"status": "failed", "last_error": err})

def main():
    # Check for search mode
    if "--search" in sys.argv:
        if not VECTOR_AVAILABLE:
            print("❌ Vector memory dependencies not installed. Install sentence-transformers and faiss.")
            sys.exit(1)
        idx = sys.argv.index("--search")
        if len(sys.argv) <= idx + 1:
            print("Usage: operator.py --search <query>")
            sys.exit(1)
        query = " ".join(sys.argv[idx+1:])
        k = 5
        # Optional: --top N
        if "--top" in sys.argv:
            t_idx = sys.argv.index("--top")
            if len(sys.argv) > t_idx+1:
                try:
                    k = int(sys.argv[t_idx+1])
                except:
                    pass
        results = search_memory(query, k=k)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    log("🔧 Operator booting...")
    run_once()
    log("🛑 Operator run complete")

if __name__ == "__main__":
    main()
