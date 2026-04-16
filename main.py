import os
import asyncio
import threading
import logging

from fastapi import FastAPI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logger.info(f"BOT TOKEN EXISTS: {bool(BOT_TOKEN)}")
if BOT_TOKEN:
    logger.info(f"BOT TOKEN PREFIX: {BOT_TOKEN[:10]}")

app = FastAPI()


@app.get("/")
def ping():
    return {"status": "alive"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот жив.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Echo: {text}")


def run_bot():
    async def bot_main():
        logger.info("Starting Telegram bot...")
        tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
        tg_app.add_handler(CommandHandler("start", start))
        tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        await tg_app.initialize()
        logger.info("Telegram app initialized")

        await tg_app.start()
        logger.info("Telegram app started")

        await tg_app.updater.start_polling()
        logger.info("Polling started")

        while True:
            await asyncio.sleep(3600)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_main())
    except Exception as e:
        logger.exception(f"Bot crashed: {e}")


@app.on_event("startup")
def startup_event():
    logger.info("FastAPI startup event triggered")
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    logger.info("Bot thread started")
