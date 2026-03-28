"""Tests for operator core: TaskStore, add_task, request_approval."""
import pytest  # noqa: F401
import os
from xander_operator import TaskStore, get_next_task, update_task, request_approval

def test_taskstore_add_and_get(tmp_path):
    db_path = tmp_path / "tasks.db"
    store = TaskStore(db_path=db_path)
    task_id = store.add_task("Test task", "browse", url="https://example.com")
    task = store.get_task(task_id)
    assert task["task"] == "Test task"
    assert task["type"] == "browse"
    assert task["url"] == "https://example.com"
    assert task["status"] == "pending"

def test_add_task_and_get_next(tmp_path):
    db_path = tmp_path / "tasks.db"
    store = TaskStore(db_path=db_path)
    store.add_task("Only task", "browse", url="https://a.com")
    task = store.get_pending()
    assert task is not None
    assert task["task"] == "Only task"
    # After marking in_progress, get_pending should return None (no other pending)
    store.update_task(task["id"], {"status": "in_progress"})
    task2 = store.get_pending()
    assert task2 is None

def test_approval_auto(monkeypatch):
    monkeypatch.setenv("XANDER_AUTO_APPROVE", "1")
    assert request_approval("test", "http://example.com", "do something") is True
    if "XANDER_AUTO_APPROVE" in os.environ:
        del os.environ["XANDER_AUTO_APPROVE"]

def test_approval_reject(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'no')
    assert request_approval("test", "http://example.com", "do something") is False
