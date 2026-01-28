from aiogram import Bot
from aiogram.types import ChatMember

async def is_subscribed(bot: Bot, user_id: int, channels: list[str]) -> bool:
    for channel in channels:
        try:
            member: ChatMember = await bot.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except:
            return False
    return True


