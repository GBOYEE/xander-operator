#!/usr/bin/env python3
"""
HTML Report Generator — Render task history and summaries using Jinja2.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import jinja2

from . import TaskStore

log = logging.getLogger(__name__)

def _get_workspace() -> Path:
    return Path(os.getenv("XANDER_WORKSPACE", Path.home() / ".openclaw" / "workspace")).expanduser()

def generate_report(
    output_dir: Path = None,
    title: str = "XANDER Operator Report",
    recent_days: int = 1,
    store: TaskStore = None
) -> Path:
    """
    Generate an HTML report of recent tasks.
    Returns the path to the generated file.
    """
    if output_dir is None:
        output_dir = _get_workspace() / "memory" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    if store is None:
        store = TaskStore()

    # Fetch tasks from the store (all, we'll filter in template if needed)
    try:
        tasks = load_tasks_for_report(store)
    except Exception as e:
        log.exception("Failed to load tasks for report")
        tasks = []

    # Prepare report data
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = {
        "total": len(tasks),
        "status_counts": {},
        "types": {}
    }
    for t in tasks:
        status = t.get("status", "unknown")
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
        ttype = t.get("type", "unknown")
        summary["types"][ttype] = summary["types"].get(ttype, 0) + 1

    # Render template
    template_str = _get_default_template()
    template = jinja2.Template(template_str)
    html = template.render(
        title=title,
        report_date=report_date,
        summary=summary,
        tasks=tasks
    )

    # Write to file
    filename = f"report-{datetime.now():%Y%m%d-%H%M%S}.html"
    out_path = output_dir / filename
    out_path.write_text(html, encoding="utf-8")
    log.info(f"Generated HTML report: {out_path}")
    return out_path

def load_tasks_for_report(store: TaskStore) -> List[Dict[str, Any]]:
    """
    Load tasks from the store with parsed JSON fields.
    """
    # Use the store's internal DB query to get all tasks
    db_path = store.db_path
    import sqlite3
    tasks = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM tasks ORDER BY created DESC")
        for row in cur.fetchall():
            t = dict(row)
            t['selectors'] = json.loads(t['selectors'] or '{}')
            t['values'] = json.loads(t.pop('field_values') or '{}')
            if t['result']:
                try:
                    t['result'] = json.loads(t['result'])
                except json.JSONDecodeError:
                    t['result'] = str(t['result'])[:1000]
            else:
                t['result'] = None
            # Rename description -> task
            t['task'] = t.pop('description')
            tasks.append(t)
    return tasks

def _get_default_template() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: sans-serif; margin: 2rem; background: #f9f9f9; color: #333; }
        h1 { color: #2c3e50; }
        .summary { background: #fff; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        table { width: 100%; border-collapse: collapse; background: #fff; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f0f0f0; font-weight: 600; }
        tr:hover { background: #f9f9f9; }
        .status-done { color: green; font-weight: bold; }
        .status-failed { color: red; font-weight: bold; }
        .status-pending { color: orange; }
        .status-in_progress { color: blue; }
        .footer { margin-top: 2rem; font-size: 0.8rem; color: #777; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Generated: {{ report_date }}</p>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total tasks: <strong>{{ summary.total }}</strong></p>
        <h3>By Status</h3>
        <ul>
        {% for status, count in summary.status_counts.items() %}
            <li>{{ status }}: {{ count }}</li>
        {% endfor %}
        </ul>
        <h3>By Type</h3>
        <ul>
        {% for ttype, count in summary.types.items() %}
            <li>{{ ttype }}: {{ count }}</li>
        {% endfor %}
        </ul>
    </div>

    <h2>Task List</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Created</th>
                <th>Type</th>
                <th>Description</th>
                <th>URL</th>
                <th>Status</th>
                <th>Result / Error</th>
            </tr>
        </thead>
        <tbody>
        {% for t in tasks %}
            <tr>
                <td>{{ t.id[:8] }}</td>
                <td>{{ t.created }}</td>
                <td>{{ t.type }}</td>
                <td>{{ t.task }}</td>
                <td><a href="{{ t.url }}" target="_blank">{{ t.url[:50] if t.url else '' }}</a></td>
                <td class="status-{{ t.status }}">{{ t.status }}</td>
                <td>
                    {% if t.status == 'done' %}
                        {% if t.result is string %}
                            {{ t.result[:200] }}
                        {% elif t.result is mapping and t.result.answer is defined %}
                            {{ t.result.answer[:200] }}
                        {% else %}
                            <pre>{{ t.result is mapping | tojson }}{% if t.result is mapping %}{{ t.result.answer[:200] if t.result.answer }}{% endif %}</pre>
                        {% endif %}
                    {% elif t.last_error %}
                        {{ t.last_error[:200] }}
                    {% else %}
                        &nbsp;
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
        </tbody>
    </table>

    <div class="footer">
        Generated by xander-operator v1.1.0
    </div>
</body>
</html>"""
