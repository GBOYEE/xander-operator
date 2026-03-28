"""Skills registry for XANDER operator.

A skill is a reusable procedure that can be invoked by name.
Stored in memory/skills.json and loaded at runtime.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

def _get_workspace() -> Path:
    return Path(os.getenv("XANDER_WORKSPACE", Path.home() / ".openclaw" / "workspace")).expanduser()

WORKSPACE = _get_workspace()
MEMORY_DIR = WORKSPACE / "memory"
SKILLS_FILE = MEMORY_DIR / "skills.json"

class Skills:
    def __init__(self):
        self.skills: Dict[str, Dict] = {}
        self.load()

    def load(self):
        if SKILLS_FILE.exists():
            try:
                data = json.loads(SKILLS_FILE.read_text())
                if isinstance(data, dict):
                    self.skills = data
            except Exception:
                self.skills = {}
        else:
            self.skills = {}
            # Seed with built-in skill
            self.register("integrate_telegram_module", {
                "steps": [
                    "Ensure TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set",
                    "Use xander_operator.telegram.Telegram to send messages/files",
                    "Handle send_message and send_file; wrap with retries",
                    "Validate file existence and size (<50MB) before send"
                ],
                "notes": "Telegram integration for outbound notifications. Uses Bot API sendDocument for files.",
                "when": "task type is send_telegram or send_telegram_file"
            })

    def register(self, name: str, skill: Dict):
        self.skills[name] = skill
        self.save()

    def save(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        SKILLS_FILE.write_text(json.dumps(self.skills, indent=2))

    def match(self, task: Dict) -> Optional[str]:
        """Return skill name if current task matches a known pattern."""
        ttype = task.get("type", "")
        desc = task.get("task", "").lower()
        for name, skill in self.skills.items():
            if skill.get("when"):
                # Simple string match for now; can expand
                if ttype in skill["when"] or any(keyword in desc for keyword in skill.get("keywords", [])):
                    return name
        return None

    def get(self, name: str) -> Optional[Dict]:
        return self.skills.get(name)

# Global instance
_skills = None
def get_skills() -> Skills:
    global _skills
    if _skills is None:
        _skills = Skills()
    return _skills
