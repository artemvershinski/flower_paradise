import os
import logging

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required")

MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID", 0))
if not MANAGER_CHAT_ID:
    raise ValueError("MANAGER_CHAT_ID is required")

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "")

PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
MODE = os.getenv("MODE", "polling")

# Язык по умолчанию
DEFAULT_LANGUAGE = "ru"

logger.info(f"Bot mode: {MODE}")
