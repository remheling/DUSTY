from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import OWNER_ID, MAX_CHANNELS
import time
import threading

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def get_selected():
    with db.cur() as c:
        c.execute('SELECT group_id FROM selected WHERE owner_id = ?', (OWNER_ID,))
        res = c.fetchone()
        return res[0] if res else None

def is_admin_or_owner(bot, user_id, chat_id):
    if user_id == OWNER_ID:
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def is_vip(user_id):
    with db.cur() as c:
        c.execute('SELECT * FROM vip WHERE user_id = ? AND type = "глобальный"', (user_id,))
        if c.fetchone():
            return True
        c.execute('SELECT * FROM vip WHERE user_id = ? AND type = "обычный"', (user_id,))
        return c.fetchone() is not None

def is_subscribed(bot, user_id, channels):
    for ch in channels:
        try:
            chat = bot.get_chat(ch)
            member = bot.get_chat_member(chat.id, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

def sub_keyboard(channels):
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        clean = ch.replace('@', '')
        kb.add(InlineKeyboardButton(f"📢 Подписаться на {ch}", url=f"https://t.me/{clean}"))
    kb.add(InlineKeyboardButton("💎 VIP информация", callback_data="vip"))
    return kb

# ========== РЕГИСТРАЦИЯ ВСЕХ КОМАНД ==========

def register(bot: TeleBot):
    
    # ---------- КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦА (УПРАВЛЕНИЕ ГРУППАМИ) ----------
    
    @bot.message_handler(commands=['groups'])
    def groups(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        with db.cur() as c:
            c.execute('SELECT id, title FROM groups')
            groups = c.fetchall()
        if not groups:
            bot.reply_to(m, "❌ Нет групп")
            return
        text = "📋 **Группы:**\n"
        for i, g in enumerate(groups, 1):
            text += f"{i}. {g[1]}\n"
        text += "\n👉 Выбери: /go НОМЕР"
        bot.reply_to(m, text, parse_mode="Markdown")
    
    @bot.message_handler(commands=['go'])
    def go(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2 or not args[1].isdigit():
            bot.reply_to(m, "❌ Используй: /go 1")
            return
        with db.cur() as c:
            c.execute('SELECT id, title FROM groups')
            groups = c.fetchall()
        num = int(args[1]) - 1
        if num < 0 or num >= len(groups):
            bot.reply_to(m, "❌ Неверный номер")
            return
        gid = groups[num][0]
        with db.cur() as c:
            c.execute('UPDATE selected SET group_id = ? WHERE owner_id = ?', (gid, OWNER_ID))
        bot.reply_to(m, f"✅ Выбрана: {groups[num][1]}")
    
    @bot.message_handler(commands=['add'])
    def add(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /add @канал")
            return
        ch = args[1] if args[1].startswith('@') else '@' + args[1]
        gid = get_selected()
        if not gid:
            bot.reply_to(m, "❌ Сначала выбери группу: /groups")
            return
        with db.cur() as c:
            c.execute('SELECT COUNT(*) FROM channels WHERE group_id = ?', (gid,))
            count = c.fetchone()[0]
            if count >= MAX_CHANNELS:
                bot.reply_to(m, f"❌ Максимум {MAX_CHANNELS} канала")
                return
            c.execute('INSERT INTO channels (name, group_id) VALUES (?, ?)', (ch, gid))
        bot.reply_to(m, f"✅ Канал {ch} добавлен")
    
    @bot.message_handler(commands=['del'])
    def delete(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /del @канал")
            return
        ch = args[1] if args[1].startswith('@') else '@' + args[1]
        gid = get_selected()
        if not gid:
            bot.reply_to(m, "❌ Сначала выбери группу")
            return
        with db.cur() as c:
            c.execute('DELETE FROM channels WHERE name = ? AND group_id = ?', (ch, gid))
            if c.rowcount > 0:
                bot.reply_to(m, f"✅ Канал {ch} удален")
            else:
                bot.reply_to(m, f"❌ Канал {ch} не найден")
    
    @bot.message_handler(commands=['list'])
    def channels(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        gid = get_selected()
        if not gid:
            bot.reply_to(m, "❌ Сначала выбери группу")
            return
        with db.cur() as c:
            c.execute('SELECT name FROM channels WHERE group_id = ?', (gid,))
            ch = c.fetchall()
        if not ch:
            bot.reply_to(m, "📢 Нет каналов")
            return
        text = "📢 **Каналы:**\n"
        for c in ch:
            text += f"   • {c[0]}\n"
        bot.reply_to(m, text, parse_mode="Markdown")
    
    # ---------- КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦА (УПРАВЛЕНИЕ VIP) ----------
    
    @bot.message_handler(commands=['vip'])
    def add_vip(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /vip @user")
            return
        username = args[1].replace('@', '')
        try:
            user = bot.get_chat(f"@{username}")
            uid = user.id
        except:
            bot.reply_to(m, "❌ Пользователь не найден")
            return
        
        with db.cur() as c:
            c.execute('INSERT OR REPLACE INTO vip (user_id, username, type) VALUES (?, ?, "обычный")', 
                     (uid, username))
        bot.reply_to(m, f"✅ Обычный VIP для @{username}")
        try:
            bot.send_message(uid, "🎉 Вам выдан обычный VIP!")
        except:
            pass
    
    @bot.message_handler(commands=['vipglobal'])
    def add_vip_global(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /vipglobal @user")
            return
        username = args[1].replace('@', '')
        try:
            user = bot.get_chat(f"@{username}")
            uid = user.id
        except:
            bot.reply_to(m, "❌ Пользователь не найден")
            return
        
        with db.cur() as c:
            c.execute('INSERT OR REPLACE INTO vip (user_id, username, type) VALUES (?, ?, "глобальный")', 
                     (uid, username))
        bot.reply_to(m, f"✅ Глобальный VIP для @{username}")
        try:
            bot.send_message(uid, "👑 Вам выдан глобальный VIP!")
        except:
            pass
    
    @bot.message_handler(commands=['unvip'])
    def remove_vip(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /unvip @user")
            return
        username = args[1].replace('@', '')
        with db.cur() as c:
            c.execute('DELETE FROM vip WHERE username = ?', (username,))
            if c.rowcount > 0:
                bot.reply_to(m, f"✅ VIP удален у @{username}")
            else:
                bot.reply_to(m, f"❌ VIP не найден для @{username}")
    
    @bot.message_handler(commands=['vip_list'])
    def vip_list(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        with db.cur() as c:
            c.execute('SELECT username, type FROM vip')
            vips = c.fetchall()
        if not vips:
            bot.reply_to(m, "📋 Нет VIP пользователей")
            return
        text = "👑 **VIP пользователи:**\n\n"
        for v in vips:
            text += f"• @{v[0]} - {v[1]}\n"
        bot.reply_to(m, text, parse_mode="Markdown")
    
    # ---------- КОМАНДЫ ДЛЯ ВСЕХ ----------
    
    @bot.message_handler(commands=['start', 'help'])
    def start(m: Message):
        if m.chat.type == 'private':
            bot.reply_to(m, "🔒 Бот для проверки подписки\n\nДобавь в группу и сделай админом")
        else:
            if is_admin_or_owner(bot, m.from_user.id, m.chat.id):
                bot.reply_to(m, "✅ Бот работает")
    
    @bot.message_handler(commands=['vip_info'])
    def vip_info(m: Message):
        text = """💎 **VIP ПОДПИСКА**

🔹 **Обычный VIP**
   • Освобождение от проверки в 1 группе
   • Доступ к конкурсам

🔸 **Глобальный VIP**
   • Освобождение от проверки ВО ВСЕХ группах
   • Иммунитет к мутам
   • Безлимит на медиа

👑 **Получить:** @AerenRem"""
        
        if m.chat.type in ['group', 'supergroup']:
            sent = bot.reply_to(m, text, parse_mode="Markdown")
            def delete():
                time.sleep(30)
                try:
                    bot.delete_message(m.chat.id, sent.message_id)
                    bot.delete_message(m.chat.id, m.message_id)
                except:
                    pass
            threading.Thread(target=delete, daemon=True).start()
        else:
            bot.reply_to(m, text, parse_mode="Markdown")
    
    # ---------- ОБРАБОТКА СООБЩЕНИЙ В ГРУППАХ ----------
    
    @bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
    def handle_group(m: Message):
        if is_admin_or_owner(bot, m.from_user.id, m.chat.id):
            return
        
        if is_vip(m.from_user.id):
            return
        
        with db.cur() as c:
            c.execute('SELECT name FROM channels WHERE group_id = ?', (m.chat.id,))
            channels = [r[0] for r in c.fetchall()]
        
        if not channels:
            return
        
        if not is_subscribed(bot, m.from_user.id, channels):
            try:
                bot.delete_message(m.chat.id, m.message_id)
            except:
                pass
            
            name = m.from_user.username or m.from_user.first_name
            text = f"@{name}, ты не подписан на каналы: {', '.join(channels)}\nПодпишись, чтобы писать!"
            kb = sub_keyboard(channels)
            
            sent = bot.send_message(m.chat.id, text, reply_markup=kb)
            
            def delete():
                time.sleep(30)
                try:
                    bot.delete_message(m.chat.id, sent.message_id)
                except:
                    pass
            
            threading.Thread(target=delete, daemon=True).start()
    
    # ---------- ОБРАБОТКА НАЖАТИЙ НА КНОПКИ ----------
    
    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        if call.data == "vip":
            text = """💎 **VIP ПОДПИСКА**

🔹 **Обычный VIP**
   • Освобождение от проверки в 1 группе
   • Доступ к конкурсам

🔸 **Глобальный VIP**
   • Освобождение от проверки ВО ВСЕХ группах
   • Иммунитет к мутам
   • Безлимит на медиа

👑 **Получить:** @AerenRem"""
            
            bot.answer_callback_query(call.id, "💎 Информация о VIP")
            bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    
    # ---------- ОБРАБОТКА ДОБАВЛЕНИЯ В ГРУППУ ----------
    
    @bot.message_handler(content_types=['new_chat_members'])
    def on_new(m: Message):
        for member in m.new_chat_members:
            if member.id == bot.get_me().id:
                with db.cur() as c:
                    c.execute('INSERT OR REPLACE INTO groups (id, title) VALUES (?, ?)', 
                            (m.chat.id, m.chat.title))
                bot.send_message(OWNER_ID, f"✅ Бот добавлен в {m.chat.title}")