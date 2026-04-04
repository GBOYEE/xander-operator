"""Xander Operator Agent — Contract-Compliant Wrapper"""

from pathlib import Path
from datetime import datetime
import json
import logging

from .agent import CodingAgent
from .config import settings

logger = logging.getLogger(__name__)

class OperatorAgent:
    """
    Wrapper around CodingAgent that guarantees the completion contract.
    """
    def __init__(self):
        self.agent = CodingAgent(workdir=settings.workdir)

    def run_task(self, task: str) -> dict:
        """
        Execute task and return strict contract.
        """
        try:
            # Execute using underlying agent
            result = self.agent.execute(task)

            # Normalize result into contract format
            contract = {
                "status": "completed" if result.get("status") == "success" else "failed",
                "task": task,
                "output_path": self._find_output_path(result),
                "summary": result.get("summary", "Task executed"),
                "task_id": result.get("task_id", "unknown")
            }
            return contract

        except Exception as e:
            logger.exception("Operator task failed")
            return {
                "status": "failed",
                "task": task,
                "output_path": None,
                "summary": str(e),
                "task_id": None
            }

    def _find_output_path(self, result: dict) -> str:
        """Determine the main output file path from agent result."""
        # If agent provides explicit output_path, use it
        if "output_path" in result:
            return result["output_path"]
        # Otherwise, look for files in workspace/outputs/
        outputs_dir = Path(settings.workdir) / "outputs"
        if outputs_dir.exists():
            # Get most recent file
            files = list(outputs_dir.rglob("*"))
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                return str(latest)
        # Fallback: return a placeholder
        return str(Path(settings.workdir) / "outputs" / "last_result.json")
