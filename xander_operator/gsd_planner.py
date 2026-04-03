#!/usr/bin/env python3
"""
GSD Planner — generates step-by-step execution plans for tasks.
Uses local Ollama model (phi3:mini) for planning.
"""

import json
import os
import requests
from typing import Dict, List, Any

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "phi3:mini")

def plan_task(task_desc: str, task_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate a GSD plan for the given task.

    Returns a dict with:
      - objective: clear statement of goal
      - steps: list of {description, tool, validation, expected_output}
      - success_criteria: how to verify completion
    """
    # Build prompt
    prompt = f"""You are a disciplined project manager. Create a step-by-step execution plan for this task.

Task: {task_desc}
Type: {task_type}
Params: {json.dumps(params or {}, ensure_ascii=False)}

Provide a JSON plan with:
{{
  "objective": "string",
  "steps": [
    {{
      "step": 1,
      "description": "what to do",
      "tool": "tool_name or None",
      "validation": "how to check this step succeeded",
      "expected_output": "what we expect to have after this step"
    }}
  ],
  "success_criteria": "list of conditions that mean the whole task is done"
}}

Make steps concrete, sequential, and verifiable. Use tools: browse, fill, research, write_file, shell, etc. Keep the number of steps between 3 and 8.
Respond ONLY with pure JSON, no extra text."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": PLANNER_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 1024}
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        text = data.get("response", "").strip()
        # Extract JSON from response (might have extra text before/after)
        try:
            # Find first { and last }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_text = text[start:end]
                plan = json.loads(json_text)
                return plan
            else:
                raise ValueError("No JSON object found in response")
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse plan JSON: {e}", "raw": text}
    except Exception as e:
        return {"error": f"Planning failed: {e}"}

# For manual testing
if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "Create a Python script that reverses a list"
    plan = plan_task(task, "code")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
