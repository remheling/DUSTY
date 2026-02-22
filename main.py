import logging
from telebot import TeleBot
from config import BOT_TOKEN, OWNER_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(BOT_TOKEN)
logger.info("✅ Бот запущен")

from handlers.bot import register
register(bot)

try:
    bot.send_message(OWNER_ID, "✅ Бот работает!\n/groups - список групп")
except:
    pass

logger.info("✅ Бот работает...")
bot.polling(none_stop=True)