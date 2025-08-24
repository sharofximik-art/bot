import os
from fastapi import FastAPI, Request, Header, HTTPException
from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import CommandStart
from aiogram.types import Update

BOT_TOKEN = os.environ["BOT_TOKEN"]           # BotFather token
BASE_URL = os.environ.get("BASE_URL", "")     # keyin Koyeb URL ni yozasiz
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
r = Router()
dp.include_router(r)

@r.message(CommandStart())
async def start(m: types.Message):
    await m.answer("Salom! Bot ishlayapti ✅")

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    if BASE_URL:
        await bot.set_webhook(f"{BASE_URL}/webhook", secret_token=WEBHOOK_SECRET)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

@app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    data = await request.json()
    await dp.feed_webhook_update(bot, Update.model_validate(data))
    return {"ok": True}

@app.get("/health")
async def health():
    return {"ok": True}
