# Telegram adapter for OpenClaw/xander-operator
# Sends messages and files via Telegram Bot API reliably.

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)

class Telegram:
    """
    Simple, reliable Telegram bot client with retries and fallbacks.
    Usage:
        tg = Telegram(token=os.getenv("TELEGRAM_TOKEN"))
        tg.send_message(chat_id, "Hello")
        tg.send_file(chat_id, "/path/to/file.pdf", caption="Report")
    """
    def __init__(self, token: str, base_url: Optional[str] = None, timeout: int = 30):
        if not token:
            raise ValueError("Telegram bot token required")
        self.token = token
        self.base_url = base_url or f"https://api.telegram.org/bot{token}"
        self.timeout = timeout
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        return session

    def _post(self, endpoint: str, data: Dict[str, Any], files: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        try:
            resp = self.session.post(url, data=data, files=files, timeout=self.timeout)
            resp.raise_for_status()
            payload = resp.json()
            if not payload.get("ok"):
                err = payload.get("description", "Unknown Telegram error")
                raise RuntimeError(f"Telegram API error: {err}")
            return payload
        except requests.RequestException as e:
            log.error(f"Telegram request failed: {e}")
            raise

    def send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = "Markdown") -> Dict:
        log.info(f"Sending message to chat {chat_id}")
        data = {"chat_id": chat_id, "text": text}
        if parse_mode:
            data["parse_mode"] = parse_mode
        return self._post("sendMessage", data)

    def send_file(self, chat_id: int, file_path: str, caption: Optional[str] = None, filename: Optional[str] = None) -> Dict:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if path.stat().st_size > 50 * 1024 * 1024:
            raise ValueError(f"File too large for Telegram (max 50MB): {file_path} ({path.stat().st_size} bytes)")
        log.info(f"Sending file {file_path} to chat {chat_id}")
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        with path.open("rb") as f:
            files = {"document": (filename or path.name, f)}
            return self._post("sendDocument", data, files=files)

    def send_photo(self, chat_id: int, file_path: str, caption: Optional[str] = None) -> Dict:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        log.info(f"Sending photo {file_path} to chat {chat_id}")
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        with path.open("rb") as f:
            files = {"photo": (path.name, f)}
            return self._post("sendPhoto", data, files=files)

    def send_file_safe(self, chat_id: int, file_path: str, caption: Optional[str] = None, fallback_url: Optional[str] = None) -> Dict:
        """
        Try to send file; on failure, optionally send a fallback link.
        """
        try:
            return self.send_file(chat_id, file_path, caption=caption)
        except Exception as e:
            log.warning(f"send_file failed: {e}. Fallback to link.")
            if fallback_url:
                self.send_message(chat_id, f"⚠️ File upload failed. Download here: {fallback_url}")
            raise

# Convenience factory
def get_telegram() -> Telegram:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise EnvironmentError("TELEGRAM_TOKEN environment variable not set")
    return Telegram(token=token)
