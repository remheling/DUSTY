from aiogram import Router
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
import asyncio

from storage import storage

router = Router()


@router.message()
async def check(message: Message):
    if message.text and message.text.startswith("/"):
        return

    channels = storage.get_active_channels()
    if not channels:
        return

    for ch in channels:
        try:
            member = await message.bot.get_chat_member(ch, message.from_user.id)
            if member.status in ("left", "kicked"):
                raise Exception
        except:
            try:
                await message.delete()
            except TelegramBadRequest:
                pass

            text = (
                f"{message.from_user.mention_html()} сообщение удалено.\n"
                f"Подпишитесь на обязательные каналы:\n"
                + "\n".join(channels)
            )

            msg = await message.answer(text, parse_mode="HTML")
            await asyncio.sleep(storage.bot_msg_ttl)
            await msg.delete()
            return



