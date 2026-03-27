"""Tests for reporter module."""
import pytest
from pathlib import Path
from xander_operator.reporter import generate_report, load_tasks_for_report
from xander_operator import TaskStore
import tempfile
import sqlite3

def test_generate_report_creates_file(tmp_path: Path):
    db_path = tmp_path / "test.db"
    store = TaskStore(db_path=db_path)
    # Add a couple of tasks
    store.add_task("Test browse task", "browse", url="https://example.com")
    store.add_task("Test fill task", "fill", url="https://example.com/form", selectors={"name":"#name"}, values={"name":"Xander"})
    # Generate report
    out_dir = tmp_path / "reports"
    report_path = generate_report(output_dir=out_dir, store=store)
    assert report_path.exists()
    content = report_path.read_text()
    assert "XANDER Operator Report" in content
    assert "Test browse task" in content
    assert "Test fill task" in content

def test_load_tasks_for_report_returns_parsed_tasks(tmp_path: Path):
    db_path = tmp_path / "test.db"
    store = TaskStore(db_path=db_path)
    task_id = store.add_task("Another task", "research", url="https://example.com")
    tasks = load_tasks_for_report(store)
    assert len(tasks) >= 1
    t = tasks[-1]
    assert t["id"] == task_id
    assert t["task"] == "Another task"
    assert t["type"] == "research"
    assert "selectors" in t and isinstance(t["selectors"], dict)
    assert "values" in t and isinstance(t["values"], dict)
