import pytest
from fastapi.testclient import TestClient
from gateway import create_app, store

client = TestClient(create_app())

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.1.0"

def test_metrics():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "http_requests_total" in data
    assert "tasks_total" in data

def test_create_and_get_task():
    # Create a task
    resp = client.post("/tasks", json={"description": "Test task", "type": "browse", "url": "https://example.com"})
    assert resp.status_code == 200
    task_id = resp.json()["id"]
    # Retrieve it
    resp2 = client.get(f"/tasks/{task_id}")
    assert resp2.status_code == 200
    t = resp2.json()
    assert t["description"] == "Test task"
    assert t["type"] == "browse"
    assert t["status"] == "pending"

def test_list_tasks():
    resp = client.get("/tasks?limit=5")
    assert resp.status_code == 200
    tasks = resp.json()
    assert isinstance(tasks, list)

def test_cancel_task():
    # Create
    resp = client.post("/tasks", json={"description": "Cancel me", "type": "fill", "url": "https://example.com/form"})
    task_id = resp.json()["id"]
    # Cancel
    resp2 = client.post(f"/tasks/{task_id}/cancel")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "cancelled"
    # Verify status
    resp3 = client.get(f"/tasks/{task_id}")
    assert resp3.json()["status"] == "failed"

def test_operator_control():
    # Start operator
    resp = client.post("/operators/start")
    assert resp.status_code == 200
    assert resp.json()["status"] == "started"
    # Second start returns already running
    resp2 = client.post("/operators/start")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "already running"
    # Stop
    resp3 = client.post("/operators/stop")
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "stopped"
    # Second stop
    resp4 = client.post("/operators/stop")
    assert resp4.status_code == 200
    assert resp4.json()["status"] == "not running"
