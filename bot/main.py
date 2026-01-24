import asyncio
from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.handlers import router


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не найден. Проверь .env")

    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



