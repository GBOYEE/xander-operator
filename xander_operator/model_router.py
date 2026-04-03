#!/usr/bin/env python3
"""
Model Router — dynamically select LLM model per task for XANDER Operator.

Reads routing config from $XANDER_WORKSPACE/skills/model-router/config.yaml
(if present) and sets OPENAI_MODEL / OLLAMA_BASE_URL accordingly before
LLM calls. Designed to work with xander_operator.llm.generate_response.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

def _get_workspace() -> Path:
    return Path(os.getenv("XANDER_WORKSPACE", Path.home() / ".openclaw" / "workspace")).expanduser()

def load_routing_config() -> Dict:
    cfg_path = _get_workspace() / "skills" / "model-router" / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path) as f:
            return yaml.safe_load(f) or {}
    return {}

def infer_task_tags(task: Dict[str, Any]) -> list[str]:
    tags = []
    ttype = task.get("type", "")
    if ttype:
        tags.append(ttype)
    desc = task.get("task", "").lower()
    if any(k in desc for k in ["code", "function", "python", "script", "program"]):
        tags.append("code")
    if any(k in desc for k in ["reason", "decide", "plan", "think"]):
        tags.append("reason")
    if any(k in desc for k in ["summarize", "summary", "brief"]):
        tags.append("summarize")
    if any(k in desc for k in ["research", "find", "search", "lookup"]):
        tags.append("research")
    if any(k in desc for k in ["chat", "talk", "conversation", "ask"]):
        tags.append("chat")
    return tags

def route_model(task: Dict[str, Any]) -> Dict[str, str]:
    config = load_routing_config()
    rules = config.get("routing_rules", [])
    tags = infer_task_tags(task)

    for rule in rules:
        rule_tags = rule.get("task_types", [])
        if any(tag in rule_tags for tag in tags):
            provider = rule.get("provider", "ollama")
            return {"model": rule["model"], "provider": provider}

    default_model = config.get("default", "phi3:mini")
    provider = "openai" if default_model.startswith(("stepfun/", "openai/")) else "ollama"
    return {"model": default_model, "provider": provider}

def apply_router(task: Dict[str, Any]) -> None:
    """Set OPENAI_MODEL and OLLAMA_BASE_URL based on routing rules."""
    routing = route_model(task)
    model = routing["model"]
    provider = routing["provider"]

    os.environ["OPENAI_MODEL"] = model
    if provider == "ollama":
        os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:11434"
        os.environ.pop("OPENAI_API_KEY", None)
    else:
        os.environ.pop("OLLAMA_BASE_URL", None)
        # OPENAI_API_KEY should be set externally if needed

    # Log the routing decision (using standard logging)
    import logging
    log = logging.getLogger(__name__)
    log.info(f"[ModelRouter] task_type={task.get('type')} model={model} provider={provider}")

# Standalone test
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    tasks = [
        {"type": "research", "task": "Find latest AI news"},
        {"type": "browse", "task": "Visit https://example.com"},
        {"type": "fill", "task": "Fill login form"},
        {"type": "code", "task": "Write Python function to reverse list"},
        {"type": "unknown", "task": "Do something weird"},
    ]
    for t in tasks:
        apply_router(t)
        print(f"{t['type']}: OPENAI_MODEL={os.environ.get('OPENAI_MODEL')}, OLLAMA_BASE_URL={os.environ.get('OLLAMA_BASE_URL')}")