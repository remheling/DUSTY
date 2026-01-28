from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def subscribe_kb(channel: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подписаться",
                    url=f"https://t.me/{channel.lstrip('@')}"
                )
            ]
        ]
    )

