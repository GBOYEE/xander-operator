"""
Vector memory module — optional semantic search over tasks and logs.
If dependencies are missing, provides no-op stubs so operator continues.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Use a logger instead of print; fallback to print if logging not configured
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    DEPS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Vector memory dependencies missing: {e}. Vector features disabled.")
    DEPS_AVAILABLE = False

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
VECTOR_DIR = MEMORY_DIR / "vector"
INDEX_FILE = VECTOR_DIR / "index.faiss"
META_FILE = VECTOR_DIR / "metadata.json"

# Global state
_model = None
_index = None
_metadata = {"entries": []}
_initialized = False

def _ensure_dirs():
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

def _load_meta():
    global _metadata
    if META_FILE.exists():
        try:
            _metadata = json.loads(META_FILE.read_text())
        except Exception:
            _metadata = {"entries": []}
    else:
        _metadata = {"entries": []}

def _save_meta():
    META_FILE.write_text(json.dumps(_metadata, indent=2))

def _init():
    """Initialize model and index if deps are available."""
    global _model, _index, _initialized, DEPS_AVAILABLE
    if _initialized:
        return
    if not DEPS_AVAILABLE:
        return
    try:
        _ensure_dirs()
        # Load model (bge-base-en)
        _model = SentenceTransformer("BAAI/bge-base-en")
        dim = _model.get_sentence_embedding_dimension()
        # Load or create FAISS index (inner product, normalized for cosine)
        if INDEX_FILE.exists():
            _index = faiss.read_index(str(INDEX_FILE))
        else:
            _index = faiss.IndexFlatIP(dim)
        _load_meta()
        _initialized = True
    except Exception as e:
        logging.error(f"Vector memory init failed: {e}")
        DEPS_AVAILABLE = False

def _normalize(vec: np.ndarray):
    """Normalize vector for cosine similarity."""
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

def index_text(text: str, metadata: Dict[str, Any], source: str = "generic"):
    """
    Index a text chunk with associated metadata.
    Best-effort: if vector memory unavailable, no-op.
    """
    try:
        _init()
        if not DEPS_AVAILABLE or not _model or not _index:
            return
        # Embed
        embedding = _model.encode([text])[0].astype('float32')
        embedding = _normalize(embedding)
        # Add to index
        _index.add(embedding.reshape(1, -1))
        faiss.write_index(_index, str(INDEX_FILE))
        # Store metadata
        entry_id = hashlib.sha256((text + str(datetime.now())).encode()).hexdigest()[:12]
        entry = {
            "id": entry_id,
            "text": text,
            "source": source,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        _metadata["entries"].append(entry)
        _save_meta()
    except Exception as e:
        logging.warning(f"Vector index failed: {e}")

def index_task(task: Dict[str, Any]):
    """Index a task object (its description and result if present)."""
    # Combine description and result for indexing
    text_parts = [task.get("task") or task.get("description", "")]
    result = task.get("result")
    if result:
        if isinstance(result, dict):
            result_str = json.dumps(result, ensure_ascii=False)
        else:
            result_str = str(result)
        text_parts.append(result_str)
    text = " | ".join(text_parts)[:2000]  # limit length
    meta = {
        "task_id": task.get("id"),
        "type": task.get("type"),
        "status": task.get("status"),
        "created": task.get("created"),
        "source": "task"
    }
    index_text(text, meta, source="task")

def index_log_entry(message: str, metadata: Dict[str, Any]):
    """Index a daily log entry."""
    index_text(message, metadata, source="log")

def search_memory(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Search indexed texts by semantic similarity.
    Returns list of dicts with: score, text, metadata.
    If vector memory unavailable, returns empty list.
    """
    try:
        _init()
        if not DEPS_AVAILABLE or not _model or not _index or _index.ntotal == 0:
            return []
        q_emb = _model.encode([query])[0].astype('float32')
        q_emb = _normalize(q_emb)
        distances, indices = _index.search(q_emb.reshape(1, -1), min(k, _index.ntotal))
        results = []
        entries = _metadata["entries"]
        for dist, idx in zip(distances[0], indices[0]):
            if 0 <= idx < len(entries):
                entry = entries[idx]
                results.append({
                    "score": float(dist),
                    "text": entry["text"],
                    "metadata": entry["metadata"],
                    "source": entry["source"],
                    "timestamp": entry["timestamp"]
                })
        return results
    except Exception as e:
        logging.warning(f"Vector search failed: {e}")
        return []

def clear_index():
    """Wipe all indexed data (use with caution)."""
    global _index, _metadata, _initialized
    try:
        if INDEX_FILE.exists():
            INDEX_FILE.unlink()
        if META_FILE.exists():
            META_FILE.unlink()
        _index = None
        _metadata = {"entries": []}
        _initialized = False
        _ensure_dirs()  # recreate empty
        logging.info("Vector memory cleared.")
    except Exception as e:
        logging.warning(f"Clear index failed: {e}")

# Auto-init on import to ensure directories exist (but not load model yet)
_ensure_dirs()
