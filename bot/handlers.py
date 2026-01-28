from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

from config import OWNER_ID
from checker import is_subscribed, channels_text
from storage import storage

router = Router()


def is_owner(message: Message) -> bool:
    return message.from_user and message.from_user.id == OWNER_ID


# 🔒 ГЛОБАЛЬНАЯ ПРОВЕРКА — ПЕРВАЯ
@router.message()
async def subscription_guard(message: Message, bot: Bot):
    if message.chat.type not in ("group", "supergroup"):
        return

    if not message.from_user:
        return

    if is_owner(message):
        return

    if await is_subscribed(bot, message.from_user.id):
        return

    # ❌ не подписан
    try:
        await message.delete()
    except:
        pass

    await message.answer(
        f"@{message.from_user.username or message.from_user.id}, "
        f"подпишитесь на канал:\n{channels_text()}",
        disable_notification=True
    )


# ===== КОМАНДЫ ВЛАДЕЛЬЦА =====

@router.message(Command("add_channel"))
async def add_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        await message.answer("Использование: /add_channel @channel")
        return

    storage.add_channel(parts[1])
    await message.answer(f"Канал {parts[1]} добавлен")


@router.message(Command("del_channel"))
async def del_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /del_channel @channel")
        return

    storage.remove_channel(parts[1])
    await message.answer("Канал удалён")


@router.message(Command("channels"))
async def show_channels(message: Message):
    if not is_owner(message):
        return

    channels = storage.get_all()
    if not channels:
        await message.answer("Каналы не заданы")
        return

    await message.answer("Активные каналы:\n" + channels_text())



