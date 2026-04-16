import os
import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

# Вставь сюда свой Telegram user_id.
# Если хочешь разрешить нескольким людям — добавь их id через запятую.
ALLOWED_USERS = {
    6441961719,389023753
}

app = FastAPI()
telegram_app: Application | None = None


def is_allowed(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id in ALLOWED_USERS)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if not user:
        return

    # Если твой ID ещё не внесён, бот покажет его тебе.
    if user.id not in ALLOWED_USERS:
        await update.message.reply_text(
            "Not Allowed"
        )
        return

    await update.message.reply_text("I'm here")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return

    if update.message and update.message.text:
        await update.message.reply_text(f"Echo: {update.message.text}")


@app.on_event("startup")
async def startup() -> None:
    global telegram_app

    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await telegram_app.initialize()
    await telegram_app.start()
    logger.info("Telegram application initialized and started")


@app.on_event("shutdown")
async def shutdown() -> None:
    global telegram_app

    if telegram_app is not None:
        await telegram_app.stop()
        await telegram_app.shutdown()
        logger.info("Telegram application stopped")


@app.get("/")
async def healthcheck() -> Dict[str, str]:
    return {"status": "alive"}


@app.post("/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    global telegram_app

    if telegram_app is None:
        raise HTTPException(status_code=500, detail="Telegram app is not initialized")

    data: Dict[str, Any] = await request.json()
    update = Update.de_json(data, telegram_app.bot)

    logger.info("Received webhook update")
    await telegram_app.process_update(update)

    return JSONResponse({"ok": True})
