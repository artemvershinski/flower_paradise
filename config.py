import os
import json
import logging

logger = logging.getLogger(__name__)

# Токен бота (обязательно)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения")

# ID чата менеджера (обязательно)
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID", 0))
if not MANAGER_CHAT_ID:
    raise ValueError("MANAGER_CHAT_ID не задан в переменных окружения")

# Google Sheets (опционально)
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")

# Google Credentials могут быть переданы как JSON строка
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
# Или как путь к файлу
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "")

# Для вебхука и пинга
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Режим работы (polling или webhook)
MODE = os.getenv("MODE", "polling")  # polling или webhook

logger.info(f"Бот запускается в режиме: {MODE}")
if MODE == "webhook" and not WEBHOOK_URL:
    logger.warning("WEBHOOK_URL не задан, использую polling режим")
    MODE = "polling"
