"""Xander Operator CLI — contract-compliant task execution."""

import argparse
import json
import logging
from pathlib import Path

from .operator_agent import OperatorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Xander Operator — autonomous agent executor")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--output", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()

    agent = OperatorAgent()
    contract = agent.run_task(args.task)

    if args.output == "json":
        print(json.dumps(contract, indent=2))
    else:
        # Text summary
        if contract["status"] == "completed":
            print(f"✅ Task completed\nOutput: {contract['output_path']}\nSummary: {contract['summary']}")
        else:
            print(f"❌ Task failed\nError: {contract.get('error', 'unknown')}")

if __name__ == "__main__":
    main()
