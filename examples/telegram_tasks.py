#!/usr/bin/env python3
"""
Example: create Telegram notification tasks for XANDER Operator.
Usage:
    python examples/telegram_tasks.py send_message "Deploy complete"
    python examples/telegram_tasks.py send_file /path/to/file.pdf "Here is the report"
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from xander_operator import add_task

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("Set TELEGRAM_CHAT_ID environment variable")
        sys.exit(1)

    if action == "send_message":
        text = sys.argv[2] if len(sys.argv) > 2 else "Hello from XANDER"
        add_task(
            description=f"Telegram message: {text[:30]}...",
            task_type="send_telegram",
            chat_id=int(chat_id),
            text=text
        )
        print("Queued Telegram message task")

    elif action == "send_file":
        if len(sys.argv) < 3:
            print("Usage: send_file <file_path> [caption]")
            sys.exit(1)
        file_path = sys.argv[2]
        caption = sys.argv[3] if len(sys.argv) > 3 else None
        add_task(
            description=f"Telegram file: {Path(file_path).name}",
            task_type="send_telegram_file",
            chat_id=int(chat_id),
            file_path=file_path,
            caption=caption
        )
        print("Queued Telegram file task")
    else:
        print(f"Unknown action: {action}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
