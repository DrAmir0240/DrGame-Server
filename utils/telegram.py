import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class TelegramError(Exception):
    """خطای اختصاصی برای ارسال پیام تلگرام."""
    pass


def send_telegram_message(
    text: str,
    chat_id: str | int | None = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
    disable_notification: bool = False,
    protect_content: bool = False,
) -> dict:
    """
    ارسال پیام به تلگرام با Bot API.
    - text: متن پیام (می‌تونه HTML یا Markdown باشه)
    - chat_id: اگر None بود از settings استفاده می‌کنه
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        raise TelegramError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

    chat_id = chat_id or settings.TELEGRAM_CHANNEL_ID
    if not chat_id:
        raise TelegramError("TELEGRAM_CHANNEL_ID یا chat_id خالی است.")

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
        "disable_notification": disable_notification,
        "protect_content": protect_content,
    }

    try:
        resp = requests.post(url, json=payload, timeout=settings.TELEGRAM_TIMEOUT)
    except requests.RequestException as e:
        logger.exception("ارسال پیام به تلگرام شکست خورد.")
        raise TelegramError(f"خطا در اتصال به تلگرام: {e}") from e

    if resp.status_code != 200:
        logger.error("Telegram non-200: %s - %s", resp.status_code, resp.text)
        raise TelegramError(f"کد وضعیت نامعتبر از تلگرام: {resp.status_code}")

    data = resp.json()
    if not data.get("ok"):
        logger.error("Telegram error: %s", data)
        # مثال خطا: {"ok": false, "error_code": 400, "description": "Bad Request: CHAT_ADMIN_REQUIRED"}
        raise TelegramError(f"ارسال پیام ناموفق: {data}")

    return data
