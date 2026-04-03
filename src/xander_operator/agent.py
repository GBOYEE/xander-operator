"""Coding agent that uses LLM to generate and apply code changes."""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

from .config import settings
from .tools.file_tool import FileTool
from .tools.git_tool import GitTool

logger = logging.getLogger("xander_operator.agent")

class CodingAgent:
    def __init__(self, workdir: Path = None):
        self.workdir = workdir or settings.workdir
        self.file_tool = FileTool(self.workdir)
        self.git_tool = GitTool(self.workdir)
        # Ensure repo
        if not (self.workdir / ".git").exists():
            self.git_tool.init()

    def execute(self, task: str) -> Dict[str, Any]:
        """Main entry: generate code changes and apply them."""
        try:
            # 1. Generate plan (for now single step)
            plan = self._plan(task)
            # 2. Apply changes
            result = self._apply_changes(plan)
            # 3. Commit
            commit_res = self.git_tool.commit(f"xander-operator: {task[:50]}", allow_empty=True)
            result["commit"] = commit_res
            result["status"] = "success"
            return result
        except Exception as e:
            logger.exception("Task failed")
            return {"status": "error", "error": str(e)}

    def _plan(self, task: str) -> Dict[str, Any]:
        """Use LLM to produce a file modification plan."""
        prompt = self._build_prompt(task)
        response = self._call_llm(prompt)
        # Expect JSON: [{"file": "path", "content": "..."}]
        try:
            plan = json.loads(response)
            if not isinstance(plan, list):
                raise ValueError("plan not list")
            return {"modifications": plan}
        except Exception as e:
            logger.error(f"LLM output invalid: {response}")
            raise

    def _build_prompt(self, task: str) -> str:
        return f"""
You are an AI developer. Given the task: "{task}", output a JSON array of file modifications.
Each modification has:
- "file": relative path inside the workspace
- "content": full new content of that file (replace if exists, create if not)

Only output valid JSON, nothing else.
Example:
[
  {{"file": "app.py", "content": "print('Hello')"}}
]
"""

    @retry(stop=stop_after_attempt(settings.max_retries), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_llm(self, prompt: str) -> str:
        # Try Ollama first
        try:
            resp = requests.post(
                f"{settings.ollama_url}/api/generate",
                json={"model": settings.model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            logger.warning(f"Ollama failed: {e}")
            # Fallback to OpenAI if key set
            if settings.openai_api_key:
                import openai
                client = openai.OpenAI(api_key=settings.openai_api_key)
                r = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                )
                return r.choices[0].message.content
            raise

    def _apply_changes(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        files_written = []
        for mod in plan["modifications"]:
            file_path = mod["file"]
            content = mod["content"]
            # Safety: ensure file within workdir
            self.file_tool.write(file_path, content)
            files_written.append(file_path)
        return {"files_written": files_written}
