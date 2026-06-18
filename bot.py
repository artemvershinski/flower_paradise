import logging
import os
import asyncio
import threading
from fastapi import FastAPI
import uvicorn
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

from config import BOT_TOKEN
from handlers import start, handle_callback, handle_text
from states import States

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# FastAPI приложение для health check
app = FastAPI()

@app.get("/")
@app.get("/health")
async def health():
    return {"status": "ok", "service": "flower-paradise-bot"}

def run_bot():
    """Запуск бота в polling-режиме"""
    try:
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN is empty!")
            return
        
        logger.info("Initializing bot...")
        application = Application.builder().token(BOT_TOKEN).build()
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                States.MAIN_MENU: [CallbackQueryHandler(handle_callback)],
                States.LANGUAGE_SELECT: [CallbackQueryHandler(handle_callback)],
                States.SELECT_CATEGORY: [CallbackQueryHandler(handle_callback)],
                States.SELECT_FLOWER: [CallbackQueryHandler(handle_callback)],
                States.VIEW_FLOWER: [CallbackQueryHandler(handle_callback)],
                States.ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
                States.ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
                States.ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
                States.ASK_DELIVERY_DATE: [CallbackQueryHandler(handle_callback)],
                States.ASK_DELIVERY_TIME: [CallbackQueryHandler(handle_callback)],
                States.ASK_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
                States.CONFIRM_ORDER: [CallbackQueryHandler(handle_callback)],
                States.ORDER_HISTORY: [CallbackQueryHandler(handle_callback)],
                States.ORDER_STATUS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
                States.MANAGER_MENU: [CallbackQueryHandler(handle_callback)],
                States.MANAGER_VIEW_ORDERS: [CallbackQueryHandler(handle_callback)],
                States.MANAGER_VIEW_ORDER: [CallbackQueryHandler(handle_callback)],
                States.MANAGER_CHANGE_STATUS: [CallbackQueryHandler(handle_callback)],
            },
            fallbacks=[CommandHandler('start', start)]
        )
        
        application.add_handler(conv_handler)
        
        logger.info("Starting bot in polling mode...")
        application.run_polling(allowed_updates=["message", "callback_query"])
        
    except Exception as e:
        logger.error(f"Bot error: {e}")

def run_web():
    """Запуск веб-сервера для health check"""
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting web server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Запускаем бота в основном потоке
    run_bot()
