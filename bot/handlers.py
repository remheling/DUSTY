# handlers.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import OWNER_ID
from storage import storage

router = Router()


def is_owner(message: Message) -> bool:
    return message.from_user is not None and message.from_user.id == OWNER_ID


# ➕ Добавить канал в проверку
@router.message(Command("add_channel"))
async def add_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        await message.answer("❌ Используй:\n/add_channel @channel")
        return

    channel = parts[1]
    storage.add_channel(channel)
    await message.answer(f"✅ Канал {channel} добавлен в проверку")


# ➖ Удалить ОДИН канал
@router.message(Command("del_channel"))
async def del_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        await message.answer("❌ Используй:\n/del_channel @channel")
        return

    channel = parts[1]
    removed = storage.remove_channel(channel)

    if removed:
        await message.answer(f"🗑 Канал {channel} удалён из проверки")
    else:
        await message.answer(f"⚠️ Канал {channel} не найден в списке")


# 🧹 Удалить ВСЕ каналы
@router.message(Command("clear_channels"))
async def clear_channels(message: Message):
    if not is_owner(message):
        return

    storage.clear_channels()
    await message.answer("🧹 Все каналы удалены из проверки")


# 📋 Показать статус проверки
@router.message(Command("channels"))
async def show_channels(message: Message):
    if not is_owner(message):
        return

    channels = storage.get_channels()
    if not channels:
        await message.answer("ℹ️ Проверка отключена — каналы не заданы")
        return

    text = "📢 Каналы на проверке:\n" + "\n".join(channels)
    await message.answer(text)



