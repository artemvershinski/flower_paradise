import os
import logging

logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required")

# ID чата менеджера
MANAGER_CHAT_ID = int(os.environ.get("MANAGER_CHAT_ID", 0))
if not MANAGER_CHAT_ID:
    raise ValueError("MANAGER_CHAT_ID is required")

# Google Sheets (опционально)
GOOGLE_SHEETS_ID = os.environ.get("GOOGLE_SHEETS_ID", "")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "")

# Настройки сервера
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
MODE = os.environ.get("MODE", "polling")

# Язык по умолчанию
DEFAULT_LANGUAGE = "ru"

logger.info(f"Bot mode: {MODE}")
logger.info(f"BOT_TOKEN: {'configured' if BOT_TOKEN else 'MISSING'}")
logger.info(f"MANAGER_CHAT_ID: {MANAGER_CHAT_ID}")
