from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from storage import storage


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    channels = storage.get_all()
    if not channels:
        return True  # если каналов нет — проверка выключена

    for channel in channels:
        try:
            member = await bot.get_chat_member(f"@{channel}", user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest:
            return False

    return True


def channels_text() -> str:
    return "\n".join(f"@{c}" for c in storage.get_all())



