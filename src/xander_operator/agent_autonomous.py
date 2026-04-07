"""Enhanced CodingAgent with autonomous execution and auto-reporting."""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

from .config import settings
from .tools.file_tool import FileTool
from .tools.git_tool import GitTool
from skills.telegram.send_file import send_file_with_config

logger = logging.getLogger("xander_operator.agent")

# Anti-perfection guardrails
MAX_ITERATIONS = 2
OUTPUTS_DIR = Path("/outputs")  # or configurable

class CodingAgent:
    def __init__(self, workdir: Path = None):
        self.workdir = workdir or settings.workdir
        self.file_tool = FileTool(self.workdir)
        self.git_tool = GitTool(self.workdir)
        self.task_id = str(uuid.uuid4())[:8]
        self.iterations = 0
        # Ensure repo
        if not (self.workdir / ".git").exists():
            self.git_tool.init()

    def execute(self, task: str) -> Dict[str, Any]:
        """
        Execute a task with autonomous finalization.
        Flow: RECEIVE → EXECUTE → SAVE → SEND → LOG → DONE
        """
        logger.info(f"[{self.task_id}] Starting task: {task}")
        start_time = datetime.utcnow()

        try:
            # Iterative execution with cap
            result = None
            while self.iterations < MAX_ITERATIONS:
                self.iterations += 1
                logger.info(f"[{self.task_id}] Iteration {self.iterations}/{MAX_ITERATIONS}")

                # EXECUTE: generate plan and apply
                plan = self._plan(task)
                apply_result = self._apply_changes(plan)

                # VALIDATE: check if output meets requirements
                if self._validate_result(apply_result):
                    # SAVE output to organized location
                    output_path = self._save_output(task, apply_result)

                    # SEND via Telegram (auto)
                    telegram_result = self._send_to_telegram(output_path, task)

                    # LOG completion
                    log_entry = self._log_completion(task, output_path, telegram_result, start_time)

                    # COMMIT to git
                    commit_msg = f"xander-operator: {task[:50]} (auto)"
                    commit_res = self.git_tool.commit(commit_msg, allow_empty=False)

                    return {
                        "status": "done",
                        "task_id": self.task_id,
                        "output_path": str(output_path),
                        "telegram_sent": telegram_result.get("ok", False),
                        "commit": commit_res,
                        "log_entry": log_entry,
                        "iterations": self.iterations,
                        "summary": f"Task completed and delivered via Telegram."
                    }
                else:
                    # Not valid; retry once if under cap
                    if self.iterations < MAX_ITERATIONS:
                        logger.warning(f"[{self.task_id}] Output invalid, retrying...")
                        continue
                    else:
                        # Force completion even if imperfect
                        logger.error(f"[{self.task_id}] Max iterations reached; forcing completion.")
                        output_path = self._save_output(task, apply_result, forced=True)
                        telegram_result = self._send_to_telegram(output_path, task)
                        log_entry = self._log_completion(task, output_path, telegram_result, start_time, forced=True)
                        commit_res = self.git_tool.commit(f"xander-operator: {task[:50]} (forced)", allow_empty=False)
                        return {
                            "status": "completed_with_issues",
                            "task_id": self.task_id,
                            "output_path": str(output_path),
                            "telegram_sent": telegram_result.get("ok", False),
                            "commit": commit_res,
                            "log_entry": log_entry,
                            "iterations": self.iterations,
                            "summary": "Task completed after max iterations; review needed."
                        }

            raise RuntimeError("Execution loop terminated unexpectedly")

        except Exception as e:
            logger.exception(f"[{self.task_id}] Task failed")
            # Send error notification
            self._send_error_notification(task, str(e))
            return {"status": "error", "task_id": self.task_id, "error": str(e)}

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

Respond ONLY with JSON. No explanations.
"""

    def _call_llm(self, prompt: str) -> str:
        """Call LLM (Ollama or OpenAI) to get response."""
        # Use existing LLM integration
        from .llm import LLM
        llm = LLM()
        return llm.generate(prompt)

    def _apply_changes(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply file modifications from plan."""
        applied = []
        for mod in plan.get("modifications", []):
            file_path = self.workdir / mod["file"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(mod["content"])
            applied.append(str(file_path))
        return {"applied_files": applied, "modifications_count": len(applied)}

    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Check if execution result is acceptable."""
        # At minimum, we must have applied some files
        return result.get("modifications_count", 0) > 0

    def _save_output(self, task: str, result: Dict[str, Any], forced: bool = False) -> Path:
        """Save execution result to organized output directory."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_task = "".join(c if c.isalnum() or c in "-_" else "_" for c in task[:30])
        filename = f"{self.task_id}_{safe_task}_{timestamp}.json"
        output_dir = OUTPUTS_DIR / "xander_operator"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        payload = {
            "task_id": self.task_id,
            "task": task,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
            "forced": forced,
            "iterations": self.iterations,
        }
        output_path.write_text(json.dumps(payload, indent=2))
        logger.info(f"[{self.task_id}] Output saved to {output_path}")
        return output_path

    def _send_to_telegram(self, file_path: Path, task: str) -> Dict[str, Any]:
        """Automatically send output file to Telegram."""
        try:
            caption = f"✅ Xander Operator Task Completed\n\nTask: {task[:100]}\nFile: {file_path.name}\nTime: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
            result = send_file_with_config(
                file_path=str(file_path),
                caption=caption
            )
            if result.get("ok"):
                logger.info(f"[{self.task_id}] Telegram delivery confirmed")
            else:
                logger.error(f"[{self.task_id}] Telegram delivery failed: {result.get('error')}")
            return result
        except Exception as e:
            logger.error(f"[{self.task_id}] Telegram send exception: {e}")
            return {"ok": False, "error": str(e)}

    def _send_error_notification(self, task: str, error: str):
        """Send error notification to Telegram."""
        try:
            caption = f"❌ Xander Operator Task Failed\n\nTask: {task[:100]}\nError: {error}\nTime: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
            # Send as a text message via Telegram (we'd need a send_message skill)
            # For now, just log; can extend later
            logger.error(f"[{self.task_id}] Error notification would go here: {error}")
        except Exception as e:
            logger.error(f"[{self.task_id}] Error notification failed: {e}")

    def _log_completion(self, task: str, output_path: Path, telegram_result: Dict[str, Any], start_time: datetime, forced: bool = False) -> Dict[str, Any]:
        """Write task completion log entry."""
        log_dir = Path("/logs") if OUTPUTS_DIR.as_posix().startswith("/") else self.workdir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "tasks.json"
        entry = {
            "task_id": self.task_id,
            "task": task,
            "started_at": start_time.isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "output_file": str(output_path),
            "telegram_sent": telegram_result.get("ok", False),
            "telegram_message_id": telegram_result.get("message_id"),
            "forced": forced,
            "iterations": self.iterations,
        }
        # Append to log file
        entries = []
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text())
                if not isinstance(entries, list):
                    entries = []
            except:
                entries = []
        entries.append(entry)
        log_file.write_text(json.dumps(entries, indent=2))
        logger.info(f"[{self.task_id}] Completion logged to {log_file}")
        return entry
