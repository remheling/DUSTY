from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscribe_keyboard(channels: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"Подписаться {ch}", url=f"https://t.me/{ch[1:]}")]
        for ch in channels
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
