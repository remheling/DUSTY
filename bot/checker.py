from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from storage import storage


async def get_not_subscribed(bot: Bot, user_id: int) -> list[str]:
    not_subscribed = []

    for channel in storage.get_channels():
        try:
            member = await bot.get_chat_member(f"@{channel}", user_id)
            if member.status not in ("member", "administrator", "creator"):
                not_subscribed.append(channel)
        except TelegramBadRequest:
            not_subscribed.append(channel)

    return not_subscribed


