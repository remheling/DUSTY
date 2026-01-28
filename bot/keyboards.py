from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from storage import storage

def subscribe_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=ch, url=f"https://t.me/{ch.lstrip('@')}")]
            for ch in storage.get_channels()
        ]
    )


