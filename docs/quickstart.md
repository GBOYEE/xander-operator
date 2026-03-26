# Quickstart Guide

## 1. Environment Setup

```bash
# Clone or download this repository
cd /path/to/xander-operator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## 2. First Task

Edit `memory/tasks.json` and add a simple browse task:

```json
{
  "id": "demo-1",
  "task": "Fetch example.com",
  "type": "browse",
  "url": "https://example.com",
  "status": "pending",
  "created": "2025-03-26T12:00:00Z",
  "attempts": 0,
  "last_error": "",
  "result": null
}
```

## 3. Run

```bash
python3 xander_operator.py
```

You should see:

```
🔧 Operator booting...
▶️  Starting task demo-1: Fetch example.com
✅ browse https://example.com → 129 chars
🛑 Operator run complete
```

Check `memory/2025-03-26.md` for the log and `memory/tasks.json` for updated status.

## 4. Optional: Semantic Search

After a few tasks, try:

```bash
python3 xander_operator.py --search "example domain" --top 3
```

First run will download the embedding model (~400MB); subsequent runs are fast.

---

That’s it. You’re ready to automate.
