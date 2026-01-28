from aiogram import Bot
from aiogram.types import ChatMemberStatus
from storage import storage

async def is_subscribed(bot: Bot, user_id: int) -> tuple[bool, str | None]:
    if not storage.has_channels():
        return True, None

    for channel in storage.get_channels():
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ):
                return False, channel
        except:
            return False, channel

    return True, None



