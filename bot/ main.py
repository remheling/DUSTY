import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from routers import admin, checker, start

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(checker.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())







