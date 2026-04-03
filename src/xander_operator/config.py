"""Configuration for xander-operator."""
import os
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Settings:
    workdir: Path = field(default_factory=lambda: Path(os.getenv("XANDER_OPERATOR_WORKDIR", "/workspace")))
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("XANDER_OPERATOR_MODEL", "phi3")
    max_retries: int = int(os.getenv("XANDER_MAX_RETRIES", "3"))
    dry_run: bool = os.getenv("XANDER_DRY_RUN", "false").lower() == "true"
    allow_shell: bool = os.getenv("XANDER_ALLOW_SHELL", "false").lower() == "true"

settings = Settings()
