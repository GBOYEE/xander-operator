# Telegram Integration for OpenClaw

Send notifications and files to Telegram from your agents.

## Setup

1. Create a bot via BotFather and get your `TELEGRAM_TOKEN`.
2. Get your chat ID (send a message to your bot, then visit:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`).
3. Export environment variables:

```bash
export TELEGRAM_TOKEN="123:ABC"
export TELEGRAM_CHAT_ID="987654321"
```

## Task Types

### send_telegram
Send a text message.

```json
{
  "type": "send_telegram",
  "text": "Task completed successfully."
}
```

### send_telegram_file
Send a file (PDF, image, etc.). The file must exist locally and be <50MB.

```json
{
  "type": "send_telegram_file",
  "file_path": "/path/to/report.pdf",
  "caption": "Your weekly report"
}
```

You can also omit `chat_id` if `TELEGRAM_CHAT_ID` is set.

## Example

```python
from xander_operator import add_task

add_task(
    "Send CV PDF",
    task_type="send_telegram_file",
    file_path="/var/www/html/cv/oyebanji_adegboyega.html",
    caption="Here is my CV"
)
```

## Notes

- Uses `sendDocument` endpoint for files (supports most MIME types).
- Auto-retries on transient errors.
- Raises on permanent failures; task status set to `failed`.
