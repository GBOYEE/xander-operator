# Vector Memory Module (Phase 6 Early)

Optional semantic search over task history and daily logs.
Uses sentence-transformers (bge-base-en) and FAISS.

**Status:** Experimental, not required for basic operation.
If dependencies missing, operator continues without vector features.

## Setup (if you want vector recall)

```bash
pip install sentence-transformers faiss-cpu
# or faiss-gpu if CUDA available
```

## Usage

In operator.py:
- After logging, `index_log_entry(message, metadata)` is called (best-effort).
- After task updates with result, `index_task(task)` is called.
- Search available via: `search_memory(query, k=5)`

CLI:
```
python3 operator.py --search "competitor price March"
```

Returns JSON results with score, snippet, metadata.

## Design

- Index stored in `memory/vector/` (index.faiss + metadata.json)
- Model: `BAAI/bge-base-en` (~400MB) for best recall
- Embeddings normalized for cosine similarity
- Metadata tracks source (task/log), timestamp, IDs

## Dependencies

- `sentence-transformers>=2.2.0`
- `faiss-cpu` or `faiss-gpu`
- `numpy`

If import fails, module loads stubs and all indexing/search calls become no-ops.
