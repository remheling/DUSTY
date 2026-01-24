from aiogram import Router, Bot, F
from aiogram.types import Message

from .config import OWNER_ID
from .storage import load_data, save_data
from .checker import is_subscribed
from .keyboards import subscribe_keyboard

router = Router()


def is_owner(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == OWNER_ID)


# =====================
# ADMIN COMMANDS
# =====================

@router.message(F.text & F.text.startswith("/set_channels"))
async def set_channels(message: Message):
    if not is_owner(message):
        await message.delete()
        return

    parts = message.text.split()
    channels = [p.replace("@", "") for p in parts[1:4]]

    if not channels:
        await message.reply("❌ Используй: /set_channels @ch1 @ch2 @ch3")
        return

    data = load_data()
    data["channels"] = channels
    save_data(data)

    await message.reply(
        "✅ Каналы установлены:\n" +
        "\n".join(f"@{ch}" for ch in channels)
    )


@router.message(F.text & F.text.startswith("/set_interval"))
async def set_interval(message: Message):
    if not is_owner(message):
        await message.delete()
        return

    parts = message.text.split()

    if len(parts) < 2 or not parts[1].isdigit():
        await message.reply("❌ Используй: /set_interval 6 | 12 | 24")
        return

    hours = int(parts[1])
    if hours not in (6, 12, 24):
        await message.reply("❌ Доступно: 6 / 12 / 24")
        return

    data = load_data()
    data["check_interval"] = hours
    save_data(data)

    await message.reply(f"⏱ Интервал установлен: {hours} часов")


# =====================
# USER MESSAGE CHECK
# =====================

@router.message()
async def check_user_message(message: Message, bot: Bot):
    if not message.from_user:
        return

    if message.from_user.id == OWNER_ID:
        return

    data = load_data()
    channels = data.get("channels", [])

    if not channels:
        return

    subscribed = await is_subscribed(bot, message.from_user.id, channels)

    if not subscribed:
        try:
            await message.delete()
        except Exception:
            pass

        await message.answer(
            "❌ Чтобы писать в чате, подпишись на каналы:",
            reply_markup=subscribe_keyboard(channels)
        )
