#!/usr/bin/env python3
"""
LLM Client with Caching

Supports OpenAI API or Ollama (OpenAI-compatible).
Caches responses in SQLite to avoid重复 calls.
"""

import os
import sqlite3
import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from openai import OpenAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

log = logging.getLogger(__name__)

def _get_workspace() -> Path:
    return Path(os.getenv("XANDER_WORKSPACE", Path.home() / ".openclaw" / "workspace")).expanduser()

WORKSPACE = _get_workspace()
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DB = MEMORY_DIR / "llm_cache.db"

# ==================== CACHE LAYER ====================
class LLMCache:
    def __init__(self, db_path: Path = CACHE_DB, ttl_days: int = 7):
        self.db_path = Path(db_path)
        self.ttl = timedelta(days=ttl_days)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    prompt_hash TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    model TEXT,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON cache(created)")
            conn.commit()

    def get(self, prompt: str, model: str) -> Optional[str]:
        prompt_hash = self._hash(prompt)
        cutoff = datetime.now() - self.ttl
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT response FROM cache WHERE prompt_hash = ? AND model = ? AND created > ?",
                (prompt_hash, model, cutoff.isoformat())
            )
            row = cur.fetchone()
            if row:
                log.debug(f"LLM cache HIT for prompt hash {prompt_hash[:8]}")
                return row[0]
        return None

    def set(self, prompt: str, response: str, model: str):
        prompt_hash = self._hash(prompt)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (prompt_hash, prompt, response, model, created) VALUES (?, ?, ?, ?, ?)",
                (prompt_hash, prompt, response, model, datetime.now().isoformat())
            )
            conn.commit()
        log.debug(f"LLM cache SET for prompt hash {prompt_hash[:8]}")

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

# Global cache instance
_cache = LLMCache()

# ==================== CLIENT ====================
def get_llm_client() -> Optional['OpenAI']:
    if not LLM_AVAILABLE:
        log.error("OpenAI library not installed. Install openai>=1.0.0")
        return None

    # Prefer Ollama if OLLAMA_BASE_URL is set
    base_url = os.getenv("OLLAMA_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY", "ollama")  # dummy key for Ollama

    if base_url:
        log.info(f"Using Ollama LLM at {base_url}")
        return OpenAI(api_key=api_key, base_url=base_url)
    elif os.getenv("OPENAI_API_KEY"):
        log.info("Using OpenAI API")
        return OpenAI(api_key=api_key)
    else:
        log.error("No LLM configuration: set OPENAI_API_KEY or OLLAMA_BASE_URL")
        return None

def generate_response(
    prompt: str,
    *,
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    use_cache: bool = True
) -> Optional[str]:
    """
    Generate LLM response. If model not provided, reads OPENAI_MODEL from env,
    else defaults to stepfun/step-1-flash (OpenRouter free tier).
    """
    if model is None:
        model = os.getenv("OPENAI_MODEL", "stepfun/step-1-flash")
    """
    Generate a response from the LLM with optional caching.
    Returns the text content or None on failure.
    """
    if not LLM_AVAILABLE:
        log.error("OpenAI library not installed")
        return None

    # Check cache first (model is part of cache key)
    if use_cache:
        cached = _cache.get(prompt, model)
        if cached:
            return cached

    client = get_llm_client()
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful research assistant that synthesizes information clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        content = response.choices[0].message.content.strip() if response.choices else None
        if content and use_cache:
            _cache.set(prompt, content, model)
        return content
    except Exception as e:
        log.exception("LLM generation failed")
        return None

def clear_cache():
    """Clear the LLM response cache."""
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute("DELETE FROM cache")
        conn.commit()
    log.info("LLM cache cleared")

# Example usage:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_prompt = "Say hello and introduce yourself in one sentence."
    resp = generate_response(test_prompt, model="gpt-4o-mini")
    print(resp)
