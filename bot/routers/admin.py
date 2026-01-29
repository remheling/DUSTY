from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import OWNER_ID
from storage import storage
from utils import parse_time

router = Router()

def is_owner(message: Message):
    return message.from_user.id == OWNER_ID


@router.message(Command("add_channel"))
async def add_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()[1:]
    for ch in parts:
        if ch.startswith("@"):
            storage.add_channel(ch)

    await message.answer("Каналы добавлены.")


@router.message(Command("del_channel"))
async def del_channel(message: Message):
    if not is_owner(message):
        return

    ch = message.text.split(maxsplit=1)[1]
    storage.remove_channel(ch)
    await message.answer(f"Канал {ch} удалён.")


@router.message(Command("set_channel_timer"))
async def set_channel_timer(message: Message):
    if not is_owner(message):
        return

    _, ch, t = message.text.split()
    seconds = parse_time(t)
    if not seconds:
        await message.answer("Неверный формат времени.")
        return

    if storage.set_channel_timer(ch, seconds):
        await message.answer(f"Таймер для {ch} установлен.")
    else:
        await message.answer("Канал не найден.")


@router.message(Command("channels"))
async def channels(message: Message):
    if not is_owner(message):
        return

    channels = storage.get_active_channels()
    await message.answer(
        "Каналы на проверке:\n" + "\n".join(channels)
        if channels else "Проверка отключена."
    )


@router.message(Command("set_bot_timer"))
async def set_bot_timer(message: Message):
    if not is_owner(message):
        return

    t = message.text.split()[1]
    seconds = parse_time(t)
    if not seconds or seconds < 15 or seconds > 300:
        await message.answer("Допустимо: 15s–5m")
        return

    storage.bot_msg_ttl = seconds
    await message.answer("Таймер сообщений бота обновлён.")

