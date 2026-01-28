from aiogram.filters import Command
from aiogram.types import Message

@router.message(Command())
async def block_commands_from_users(message: Message):
    if message.chat.type != "private" and message.from_user.id != OWNER_ID:
        await message.delete()
        return

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from config import OWNER_ID
from storage import storage
from checker import is_subscribed
from keyboards import subscribe_kb

router = Router()


def is_owner(message: Message) -> bool:
    return message.from_user and message.from_user.id == OWNER_ID


@router.message(Command())
async def block чужих_commands(message: Message):
    if message.chat.type != "private" and not is_owner(message):
        await message.delete()


@router.message(Command("add_channel"))
async def add_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].startswith("@"):
        await message.answer("Используй: /add_channel @channel")
        return

    storage.add_channel(parts[1])
    await message.answer(f"Канал {parts[1]} добавлен")


@router.message(Command("del_channel"))
async def del_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Используй: /del_channel @channel")
        return

    if storage.remove_channel(parts[1]):
        await message.answer(f"Канал {parts[1]} удалён")
    else:
        await message.answer("Канал не найден")


# 🧹 CLEAR
@router.message(Command("clear_channels"))
async def clear_channels(message: Message):
    if not is_owner(message):
        return

    storage.clear_channels()
    await message.answer("Все каналы удалены")


@router.message(Command("channels"))
async def channels(message: Message):
    if not is_owner(message):
        return

    channels = storage.get_channels()
    if not channels:
        await message.answer("Проверка отключена")
        return

    await message.answer(
        "Каналы на проверке:\n" + "\n".join(channels)
    )


@router.message()
async def guard(message: Message, bot: Bot):
    if message.chat.type == "private":
        return

    if is_owner(message):
        return

    ok, bad_channel = await is_subscribed(bot, message.from_user.id)
    if ok:
        return

    await message.delete()

    await message.answer(
        f"@{message.from_user.username}, подпишитесь на канал",
        reply_markup=subscribe_kb(bad_channel),
        disable_web_page_preview=True
    )





