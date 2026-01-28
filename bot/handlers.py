from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config import OWNER_ID
from storage import storage
from checker import is_subscribed
from keyboards import subscribe_kb
from utils import parse_time

router = Router()

def is_owner(m: Message):
    return m.from_user and m.from_user.id == OWNER_ID


@router.message(Command("start"))
async def start_cmd(message: Message):
    if message.chat.type == "private":
        await message.answer(
            "Бот удаляет сообщения пользователей без подписки на обязательные каналы."
        )


@router.message(Command("add_channel"))
async def add_channels(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()[1:]
    for ch in parts:
        if ch.startswith("@"):
            storage.add_channel(ch)

    await message.answer("Каналы добавлены.")


@router.message(Command("add_one"))
async def add_one(message: Message):
    if not is_owner(message):
        return

    ch = message.text.split()[1]
    storage.add_channel(ch)
    await message.answer("Канал добавлен.")


@router.message(Command("del_channel"))
async def del_channel(message: Message):
    if not is_owner(message):
        return

    parts = message.text.split()
    ttl = parse_time(parts[2])
    storage.add_channel(parts[1], ttl)
    await message.answer("Канал будет удалён автоматически.")


@router.message(Command("status"))
async def status(message: Message):
    if not is_owner(message):
        return

    ch = storage.get_channels()
    await message.answer("\n".join(ch) if ch else "Проверка выключена.")


@router.message()
async def guard(message: Message, bot):
    if message.chat.type not in ("group", "supergroup"):
        return

    if is_owner(message):
        return

    if await is_subscribed(bot, message.from_user.id):
        return

    await message.delete()

    mention = message.from_user.mention_html()
    text = (
        f"{mention}, подпишитесь на обязательные каналы:\n"
        + "\n".join(storage.get_channels())
    )

    warn = await message.answer(text, reply_markup=subscribe_kb())
    await warn.delete(delay=storage.bot_msg_ttl)






