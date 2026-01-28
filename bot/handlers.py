import asyncio
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from config import OWNER_ID
from storage import storage
from checker import is_subscribed
from keyboards import subscribe_keyboard

router = Router()


def is_owner(message: Message) -> bool:
    return message.from_user and message.from_user.id == OWNER_ID


@router.message(Command("start"))
async def start(message: Message):
    if message.chat.type != "private":
        return

    await message.answer(
        "Этот бот автоматически удаляет сообщения пользователей,\n"
        "которые не подписаны на обязательные каналы."
    )


@router.message(Command("set_channel"))
async def set_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    channels = [p for p in parts if p.startswith("@")]

    if not channels:
        await message.answer("Укажи хотя бы один канал.")
        return

    storage.set_channels(channels)
    await message.answer("Каналы обновлены.")


@router.message(Command("del_channel"))
async def del_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        await message.answer("Используй: /del_channel @channel")
        return

    if storage.remove_channel(parts[1]):
        await message.answer("Канал удалён из проверки.")
    else:
        await message.answer("Канал не найден.")


@router.message(Command("clear_channels"))
async def clear_channels(message: Message):
    if not is_owner(message):
        return

    storage.clear_channels()
    await message.answer("Все каналы удалены из проверки.")


@router.message(Command("set_timer"))
async def set_timer(message: Message):
    if not is_owner(message):
        return

    try:
        value = message.text.split()[1].lower()
        if value.endswith("s"):
            seconds = int(value[:-1])
        elif value.endswith("m"):
            seconds = int(value[:-1]) * 60
        else:
            raise ValueError

        if not 15 <= seconds <= 600:
            raise ValueError

        storage.set_timer(seconds)
        await message.answer("Таймер обновлён.")
    except:
        await message.answer("Формат: /set_timer 15s–10m")


@router.message()
async def check_message(message: Message, bot: Bot):
    if message.chat.type not in ("group", "supergroup"):
        return

    if not storage.get_channels():
        return

    if await is_subscribed(bot, message.from_user.id, storage.get_channels()):
        return

    try:
        await message.delete()
    except:
        return

    warn = await message.answer(
        f"{message.from_user.mention_html()}\n\n"
        "Сообщение удалено.\n"
        "Подпишитесь на обязательные каналы.",
        reply_markup=subscribe_keyboard(storage.get_channels()),
        parse_mode="HTML"
    )

    await asyncio.sleep(storage.get_timer())
    try:
        await warn.delete()
    except:
        pass



