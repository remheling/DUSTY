from aiogram import Bot
from storage import storage

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    for channel in storage.get_channels():
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except:
            return False
    return True



