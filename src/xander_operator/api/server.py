"""FastAPI server for xander-operator."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import CodingAgent
from .config import settings
import logging

logger = logging.getLogger("xander_operator.api")

app = FastAPI(title="Xander Operator", version="0.1.0")

class TaskRequest(BaseModel):
    task: str
    workdir: str = None

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": __import__('time').time(), "version": "0.1.0"}

@app.post("/run")
async def run_task(req: TaskRequest):
    workdir = Path(req.workdir) if req.workdir else settings.workdir
    agent = CodingAgent(workdir=workdir)
    result = agent.execute(req.task)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return result
