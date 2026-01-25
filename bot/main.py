import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import router
from checker import checker_router  # если есть

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()

    # ⬇️ ПОДКЛЮЧАЕМ РОУТЕРЫ ОДИН РАЗ
    dp.include_router(router)
    dp.include_router(checker_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())






