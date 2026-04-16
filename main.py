import os
import threading
import logging

from fastapi import FastAPI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# --- базовый лог ---
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- FastAPI для пинга ---
app = FastAPI()

@app.get("/")
def ping():
    return {"status": "alive"}

# --- Telegram бот ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот жив.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Echo: {text}")

def run_bot():
    app_tg = ApplicationBuilder().token(BOT_TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ВАЖНО: polling блокирует поток → запускаем в отдельном thread
    app_tg.run_polling()

# --- запуск ---
threading.Thread(target=run_bot, daemon=True).start()
