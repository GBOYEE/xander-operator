#!/usr/bin/env python3
import sys
from pathlib import Path

# Insert src into path to get the src layout package
sys.path.insert(0, str(Path(__file__).parent / "src"))

from xander_operator.api.server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
