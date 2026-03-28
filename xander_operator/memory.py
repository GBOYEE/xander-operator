"""Memory retrieval for XANDER operator.

Searches:
- MEMORY.md (curated long-term)
- daily logs in memory/YYYY-MM-DD.md
- tasks.db (recent tasks)

Returns top relevant snippets for a given query.
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

def _get_workspace() -> Path:
    return Path(os.getenv("XANDER_WORKSPACE", Path.home() / ".openclaw" / "workspace")).expanduser()

WORKSPACE = _get_workspace()
MEMORY_DIR = WORKSPACE / "memory"
DB_FILE = MEMORY_DIR / "tasks.db"

def search_memory_text(query: str, texts: List[str], top_k: int = 5) -> List[Dict]:
    """Simple keyword-based search; returns matches with naive score."""
    results = []
    q = query.lower()
    for text in texts:
        score = text.lower().count(q)
        if score > 0:
            results.append({"text": text, "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def load_relevant_memory(task: Dict[str, Any], max_logs: int = 3) -> List[str]:
    """Load memory snippets relevant to the current task."""
    query = task.get("task") or task.get("description", "")
    if not query:
        return []
    snippets = []

    # 1. Search MEMORY.md if exists
    mem_path = WORKSPACE / "MEMORY.md"
    if mem_path.exists():
        try:
            content = mem_path.read_text()
            # Split into sections by ## headers
            sections = [s.strip() for s in content.split('## ') if s.strip()]
            for sec in sections:
                if query.lower() in sec.lower():
                    snippets.append(f"MEMORY: {sec[:200]}...")
        except Exception as e:
            pass

    # 2. Search recent daily logs
    today = datetime.now().date()
    for i in range(max_logs):
        day = today - timedelta(days=i)
        log_path = MEMORY_DIR / f"{day:%Y-%m-%d}.md"
        if log_path.exists():
            try:
                lines = log_path.read_text().splitlines()
                for line in lines:
                    if query.lower() in line.lower():
                        snippets.append(f"LOG[{day:%Y-%m-%d}]: {line[:200]}")
            except Exception:
                pass

    # 3. Search tasks.db for past similar tasks (type, description)
    try:
        if DB_FILE.exists():
            conn = sqlite3.connect(DB_FILE)
            cur = conn.execute("SELECT description, type, result FROM tasks ORDER BY created DESC LIMIT 100")
            for desc, ttype, result_json in cur.fetchall():
                if query.lower() in desc.lower():
                    snippets.append(f"TASK: {desc} (type={ttype})")
            conn.close()
    except Exception:
        pass

    return snippets[:10]
