from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import OWNER_ID
from storage import storage

router = Router()


def is_owner(message: Message) -> bool:
    return message.from_user and message.from_user.id == OWNER_ID


@router.message(Command("add_channel"))
async def add_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        await message.answer("❌ Используй:\n/add_channel @channel")
        return

    storage.add_channel(parts[1])
    await message.answer(f"✅ Канал {parts[1]} добавлен в проверку")


@router.message(Command("del_channel"))
async def del_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        await message.answer("❌ Используй:\n/del_channel @channel")
        return

    removed = storage.remove_channel(parts[1])
    if removed:
        await message.answer(f"🗑 Канал {parts[1]} удалён из проверки")
    else:
        await message.answer("⚠️ Канал не найден")


@router.message(Command("clear_channels"))
async def clear_channels(message: Message):
    if not is_owner(message):
        return

    storage.clear_channels()
    await message.answer("🧹 Все каналы удалены из проверки")


@router.message(Command("channels"))
async def show_channels(message: Message):
    if not is_owner(message):
        return

    channels = storage.get_channels()
    if not channels:
        await message.answer("ℹ️ Проверка отключена — каналы не заданы")
        return

    text = "📢 Каналы на проверке:\n"
    text += "\n".join(f"@{c}" for c in channels)
    await message.answer(text)




