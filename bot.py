import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

from config import BOT_TOKEN
from handlers import start, handle_callback, handle_text
from states import States

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота в polling-режиме"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.MAIN_MENU: [CallbackQueryHandler(handle_callback)],
            States.SELECT_CATEGORY: [CallbackQueryHandler(handle_callback)],
            States.SELECT_FLOWER: [CallbackQueryHandler(handle_callback)],
            States.VIEW_FLOWER: [CallbackQueryHandler(handle_callback)],
            States.ORDER_FLOWER: [CallbackQueryHandler(handle_callback)],
            States.ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            States.ASK_DELIVERY_DATE: [CallbackQueryHandler(handle_callback)],
            States.ASK_DELIVERY_TIME: [CallbackQueryHandler(handle_callback)],
            States.ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            States.ASK_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            States.CONFIRM_ORDER: [CallbackQueryHandler(handle_callback)],
            States.ORDER_HISTORY: [CallbackQueryHandler(handle_callback)],
            States.ORDER_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            States.MANAGER_MENU: [CallbackQueryHandler(handle_callback)],
            States.MANAGER_VIEW_ORDERS: [CallbackQueryHandler(handle_callback)],
            States.MANAGER_VIEW_ORDER: [CallbackQueryHandler(handle_callback)],
            States.MANAGER_CHANGE_STATUS: [CallbackQueryHandler(handle_callback)],
            States.MANAGER_SELECT_STATUS: [CallbackQueryHandler(handle_callback)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    application.add_handler(conv_handler)
    
    # Запуск polling
    logger.info("Starting bot in polling mode...")
    await application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
