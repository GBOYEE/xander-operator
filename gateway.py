"""Xander Operator Gateway — FastAPI control plane with observability."""
import os
import time
import uuid
import logging
import threading
import sqlite3
import json
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from xander_operator import TaskStore, run_once, DB_FILE, VECTOR_AVAILABLE, _init_vector

logger = logging.getLogger("xander-operator.gateway")

APP_VERSION = "1.1.0"
ENV = os.getenv("XANDER_ENV", "production")

# Shared store
DB_PATH = Path(os.getenv("XANDER_DB", DB_FILE))
store = TaskStore(DB_PATH)

# Global HTTP metrics
http_metrics = {
    "requests_total": 0,
    "requests_failed": 0,
}

# Operator control globals
_operator_running = False
_operator_thread = None
_operator_lock = threading.Lock()

def _run_operator_loop():
    while _operator_running:
        try:
            if not VECTOR_AVAILABLE:
                _init_vector()
            run_once()
        except Exception as e:
            logger.exception("Operator loop error")
            time.sleep(5)

def start_operator():
    """Start the background operator loop (idempotent)."""
    global _operator_running, _operator_thread
    with _operator_lock:
        if _operator_running:
            return False
        _operator_running = True
        _operator_thread = threading.Thread(target=_run_operator_loop, daemon=True)
        _operator_thread.start()
        logger.info("Operator loop started")
        return True

def stop_operator():
    """Stop the background operator loop."""
    global _operator_running, _operator_thread
    with _operator_lock:
        if not _operator_running:
            return False
        _operator_running = False
        if _operator_thread:
            _operator_thread.join(timeout=5)
        logger.info("Operator loop stopped")
        return True

def create_app() -> FastAPI:
    app = FastAPI(title="Xander Operator Gateway", version=APP_VERSION)

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.time()
        http_metrics["requests_total"] += 1
        try:
            resp = await call_next(request)
            elapsed = time.time() - start
            logger.info("http completed", extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": resp.status_code,
                "ms": int(elapsed*1000)
            })
            resp.headers["X-Request-ID"] = request_id
            return resp
        except Exception as exc:
            http_metrics["requests_failed"] += 1
            logger.error("http failed", extra={
                "request_id": request_id,
                "error": str(exc)
            }, exc_info=True)
            raise

    @app.get("/health")
    async def health():
        try:
            with sqlite3.connect(store.db_path) as conn:
                conn.execute("SELECT 1")
            return {
                "status": "ok",
                "timestamp": time.time(),
                "version": APP_VERSION,
                "environment": ENV,
                "operator_running": _operator_running,
            }
        except Exception as e:
            return JSONResponse(status_code=503, content={"status": "error", "detail": str(e)})

    @app.get("/metrics")
    async def metrics_endpoint():
        # Count tasks
        try:
            with sqlite3.connect(store.db_path) as conn:
                cur = conn.execute("SELECT COUNT(*) FROM tasks")
                total = cur.fetchone()[0]
                cur = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='done'")
                succeeded = cur.fetchone()[0]
                cur = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='failed'")
                failed = cur.fetchone()[0]
        except Exception as e:
            logger.error("Metrics DB error: %s", e)
            total = succeeded = failed = 0

        return {
            "http_requests_total": http_metrics["requests_total"],
            "http_requests_failed": http_metrics["requests_failed"],
            "tasks_total": total,
            "tasks_succeeded": succeeded,
            "tasks_failed": failed,
            "operator_running": _operator_running,
        }

    @app.get("/tasks")
    async def list_tasks(limit: int = 20, status: Optional[str] = None):
        with sqlite3.connect(store.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM tasks"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            query += " ORDER BY created DESC LIMIT ?"
            params.append(limit)
            cur = conn.execute(query, params)
            rows = cur.fetchall()
            result = []
            for r in rows:
                t = dict(r)
                t['selectors'] = json.loads(t['selectors'] or '{}')
                t['field_values'] = json.loads(t['field_values'] or '{}')
                if t['result']:
                    t['result'] = json.loads(t['result'])
                if t.get('params'):
                    t['params'] = json.loads(t['params'])
                t['task'] = t.pop('description')
                result.append(t)
            return result

    @app.post("/tasks")
    async def create_task(task: dict):
        desc = task.get("description") or task.get("task")
        ttype = task.get("type")
        url = task.get("url")
        selectors = task.get("selectors")
        values = task.get("values")
        if not desc or not ttype:
            raise HTTPException(status_code=400, detail="description and type required")
        task_id = store.add_task(desc, ttype, url, selectors, values, **task.get('params', {}))
        return {"id": task_id, "status": "queued"}

    @app.get("/tasks/{task_id}")
    async def get_task(task_id: str):
        t = store.get_task(task_id)
        if not t:
            raise HTTPException(status_code=404, detail="Task not found")
        return t

    @app.post("/tasks/{task_id}/cancel")
    async def cancel_task(task_id: str):
        t = store.get_task(task_id)
        if not t:
            raise HTTPException(status_code=404, detail="Task not found")
        if t['status'] in ('done', 'failed'):
            return {"status": "already finished"}
        store.update_task(task_id, {"status": "failed", "last_error": "cancelled by user"})
        return {"status": "cancelled"}

    @app.post("/operators/start")
    async def api_start_operator():
        started = start_operator()
        return {"status": "started" if started else "already running"}

    @app.post("/operators/stop")
    async def api_stop_operator():
        stopped = stop_operator()
        return {"status": "stopped" if stopped else "not running"}

    return app

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    uvicorn.run(
        "gateway:app",
        host="0.0.0.0",
        port=int(os.getenv("XANDER_PORT", 8080)),
        reload=ENV == "development",
    )
