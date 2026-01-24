from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def subscribe_keyboard(channels: List[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{ch}")]
        for ch in channels
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
