from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from typing import List


async def is_subscribed(bot: Bot, user_id: int, channels: List[str]) -> bool:
    for channel in channels:
        try:
            member = await bot.get_chat_member(f"@{channel}", user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest:
            return False
    return True
