#!/usr/bin/env python3
"""
Helper to add tasks to memory/tasks.json from CLI.
Usage: python3 add_task.py --type browse --url https://example.com --desc "Task desc"
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
import uuid

TASK_FILE = Path("memory/tasks.json")

def load_tasks():
    if TASK_FILE.exists():
        try:
            data = json.loads(TASK_FILE.read_text())
            return data.get("tasks", [])
        except Exception:
            return []
    return []

def save_tasks(tasks):
    TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"tasks": tasks, "version": "0.1"}
    TASK_FILE.write_text(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Add a task to the operator queue")
    parser.add_argument("--type", required=True, choices=["browse", "fill", "research"], help="Task type")
    parser.add_argument("--desc", required=True, help="Task description")
    parser.add_argument("--url", help="URL (for browse/fill)")
    parser.add_argument("--query", help="Query (for research)")
    parser.add_argument("--max-results", type=int, default=5, help="Max results for research")
    parser.add_argument("--follow-up-browse", action="store_true", help="Browse first result after research")
    parser.add_argument("--selectors", type=json.loads, default="{}", help='JSON selectors map, e.g. \'{"name":"input[name=n]"}')
    parser.add_argument("--values", type=json.loads, default="{}", help='JSON values map')
    args = parser.parse_args()

    task = {
        "id": str(uuid.uuid4()),
        "task": args.desc,
        "type": args.type,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "attempts": 0,
        "last_error": "",
        "result": None
    }

    if args.url:
        task["url"] = args.url
    if args.query:
        task["query"] = args.query
    if args.max_results:
        task["max_results"] = args.max_results
    if args.follow_up_browse:
        task["follow_up_browse"] = True
    if args.selectors:
        task["selectors"] = args.selectors
    if args.values:
        task["values"] = args.values

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ Added task {task['id'][:8]} – {args.desc}")

if __name__ == "__main__":
    main()
