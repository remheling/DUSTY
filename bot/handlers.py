from aiogram import Router, Bot, F
from aiogram.types import Message

from bot.config import OWNER_ID
from bot.storage import load_data, save_data
from bot.checker import is_subscribed
from bot.keyboards import subscribe_keyboard

router = Router()


def is_owner(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == OWNER_ID)


# =====================
# ADMIN COMMANDS
# =====================

@router.message(F.text.startswith("/set_channels"))
async def set_channels(message: Message):
    if not is_owner(message):
        await message.delete()
        return

    parts = message.text.split()
    channels = [p.replace("@", "") for p in parts[1:4]]

    if not channels:
        await message.reply("❌ Используй:\n/set_channels @ch1 @ch2 @ch3")
        return

    data = load_data()
    data["channels"] = channels
    save_data(data)

    await message.reply(
        "✅ Каналы установлены:\n" +
        "\n".join(f"• @{ch}" for ch in channels)
    )


@router.message(F.text.startswith("/set_interval"))
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

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def check_user_message(message: Message, bot: Bot):
    if not message.from_user:
        return

    # владелец всегда может писать
    if message.from_user.id == OWNER_ID:
        return

    data = load_data()
    channels = data.get("channels", [])

    if not channels:
        return

    subscribed = await is_subscribed(bot, message.from_user.id, channels)

    if subscribed:
        return

    # удаляем сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass

    # формируем текст с упоминанием
    mention = message.from_user.mention_html()
    channels_text = "\n".join(f"• @{ch}" for ch in channels)

    await message.answer(
        f"❌ {mention}, чтобы писать в чате, подпишись на каналы:\n\n"
        f"{channels_text}",
        reply_markup=subscribe_keyboard(channels)
    )
