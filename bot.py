import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from fastapi import FastAPI
import uvicorn

from config import BOT_TOKEN, MODE, WEBHOOK_URL, PORT
from handlers import start, handle_callback, handle_text
from states import States

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI()

async def setup_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    
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
    
    if MODE == "webhook" and WEBHOOK_URL:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.info("Starting in polling mode")
    
    return application

@app.on_event("startup")
async def startup_event():
    logger.info("Starting bot...")
    app.bot_app = await setup_bot()
    if MODE == "polling":
        asyncio.create_task(app.bot_app.run_polling())

@app.get("/")
async def root():
    return {"status": "ok", "service": "flower_paradise_bot"}

@app.post("/webhook")
async def webhook(request):
    try:
        update_data = await request.json()
        await app.bot_app.process_update(update_data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    if MODE == "webhook":
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    else:
        asyncio.run(run_polling())

async def run_polling():
    application = await setup_bot()
    await application.run_polling(allowed_updates=["message", "callback_query"])
