import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
if OWNER_ID == 0:
    raise RuntimeError("OWNER_ID не задан или неверный")


