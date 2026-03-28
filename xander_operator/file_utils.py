"""File utility helpers for OpenClaw/xander-operator."""

import os
from pathlib import Path
from typing import Optional

def ensure_file(file_path: str) -> None:
    """Raise FileNotFoundError if file does not exist."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

def get_file_size_mb(file_path: str) -> float:
    """Return file size in megabytes."""
    p = Path(file_path)
    return p.stat().st_size / (1024 * 1024)

def enforce_telegram_limit(file_path: str, limit_mb: int = 50) -> None:
    """Raise ValueError if file exceeds Telegram's size limit for bots."""
    size = get_file_size_mb(file_path)
    if size > limit_mb:
        raise ValueError(f"File too large for Telegram (limit {limit_mb}MB): {size:.2f} MB")

def resolve_path(path: str, base_dir: Optional[str] = None) -> Path:
    """Resolve a path relative to base_dir if provided, else to cwd or XANDER_WORKSPACE."""
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    if base_dir:
        return (Path(base_dir) / p).resolve()
    # Try XANDER_WORKSPACE first, then cwd
    workspace = Path(os.getenv("XANDER_WORKSPACE", Path.cwd()))
    candidate = (workspace / p).resolve()
    if candidate.exists():
        return candidate
    return Path.cwd() / p
