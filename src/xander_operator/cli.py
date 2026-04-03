"""Command-line interface for xander-operator."""
import argparse
import json
import sys
from pathlib import Path
from .agent import CodingAgent
from .config import settings

def main():
    parser = argparse.ArgumentParser(description="Xander Operator — AI developer agent")
    parser.add_argument("--task", required=True, help="Task description for the agent")
    parser.add_argument("--workdir", type=Path, default=settings.workdir, help="Working directory (must be a git repo)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    agent = CodingAgent(workdir=args.workdir)
    result = agent.execute(args.task)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["status"] == "success":
            print(f"✅ Task completed. Files written: {', '.join(result.get('files_written', []))}")
            if result.get("commit"):
                print(f"📝 Committed: {result['commit'].get('sha', '')}")
        else:
            print(f"❌ Error: {result.get('error')}")
            sys.exit(1)

if __name__ == "__main__":
    main()
