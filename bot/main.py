import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import router


async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(router)  # ✅ ТОЛЬКО ОДИН РАЗ

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())





