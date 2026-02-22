from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import OWNER_ID, MAX_CHANNELS
from datetime import datetime, timedelta
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
        c.execute('SELECT * FROM vip WHERE user_id = ? AND (until IS NULL OR until > ?)', 
                 (user_id, datetime.now()))
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
    
    @bot.message_handler(commands=['time'])
    def set_time(m: Message):
        """Установить время проверки: /time 6, /time 12, /time 24"""
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /time 6, /time 12, /time 24")
            return
        
        gid = get_selected()
        if not gid:
            bot.reply_to(m, "❌ Сначала выбери группу: /groups")
            return
        
        with db.cur() as c:
            c.execute('SELECT id, name FROM channels WHERE group_id = ?', (gid,))
            channels = c.fetchall()
        
        if not channels:
            bot.reply_to(m, "❌ В этой группе нет каналов")
            return
        
        try:
            hours = int(args[1])
            if hours not in [6, 12, 24]:
                bot.reply_to(m, "❌ Только 6, 12 или 24 часа")
                return
        except:
            bot.reply_to(m, "❌ Используй: /time 6, /time 12, /time 24")
            return
        
        until = datetime.now() + timedelta(hours=hours)
        until_str = until.strftime("%d.%m.%Y %H:%M")
        
        with db.cur() as c:
            for ch in channels:
                c.execute('UPDATE channels SET until = ? WHERE id = ?', (until, ch[0]))
        
        bot.reply_to(m, f"✅ Время проверки для {len(channels)} каналов установлено на {hours} часов (до {until_str})")
    
    @bot.message_handler(commands=['status'])
    def status(m: Message):
        """Показать общий статус"""
        if m.from_user.id != OWNER_ID:
            return
        gid = get_selected()
        if not gid:
            bot.reply_to(m, "❌ Сначала выбери группу: /groups")
            return
        
        now = datetime.now()
        text = f"📊 **ОБЩИЙ СТАТУС**\n\n"
        
        # Статус группы
        with db.cur() as c:
            c.execute('SELECT title FROM groups WHERE id = ?', (gid,))
            group = c.fetchone()
            
            c.execute('SELECT name, until FROM channels WHERE group_id = ?', (gid,))
            channels = c.fetchall()
        
        if group:
            text += f"👥 **Группа:** {group[0]}\n"
            text += f"📢 **Каналы ({len(channels)}/{MAX_CHANNELS}):**\n"
            
            for ch in channels:
                name = ch[0]
                until = ch[1]
                
                if until:
                    until_time = datetime.fromisoformat(until) if isinstance(until, str) else until
                    if until_time > now:
                        hours_left = int((until_time - now).total_seconds() / 3600)
                        minutes_left = int(((until_time - now).total_seconds() % 3600) / 60)
                        text += f"   • {name} (осталось {hours_left}ч {minutes_left}м)\n"
                    else:
                        text += f"   • {name} (⚠️ истекло)\n"
                else:
                    text += f"   • {name} (∞ без срока)\n"
        
        # Статус VIP
        with db.cur() as c:
            c.execute('SELECT username, type, until FROM vip WHERE until IS NULL OR until > ? ORDER BY until', (now,))
            active_vips = c.fetchall()
            c.execute('SELECT username, type, until FROM vip WHERE until IS NOT NULL AND until <= ?', (now,))
            expired_vips = c.fetchall()
        
        text += f"\n👑 **Активные VIP ({len(active_vips)}):**\n"
        
        if active_vips:
            for v in active_vips:
                username = v[0]
                vip_type = v[1]
                until = v[2]
                
                if until:
                    until_time = datetime.fromisoformat(until) if isinstance(until, str) else until
                    days_left = (until_time - now).days
                    text += f"   • @{username} - {vip_type} (осталось {days_left} дн)\n"
                else:
                    text += f"   • @{username} - {vip_type} (∞)\n"
        else:
            text += "   • Нет активных VIP\n"
        
        if expired_vips:
            text += f"\n⚠️ **Истекшие VIP ({len(expired_vips)}):**\n"
            for v in expired_vips:
                username = v[0]
                vip_type = v[1]
                text += f"   • @{username} - {vip_type}\n"
        
        bot.reply_to(m, text, parse_mode="Markdown")
    
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
            c.execute('SELECT name, until FROM channels WHERE group_id = ?', (gid,))
            ch = c.fetchall()
        if not ch:
            bot.reply_to(m, "📢 Нет каналов")
            return
        
        now = datetime.now()
        text = "📢 **Каналы:**\n"
        for c in ch:
            name = c[0]
            until = c[1]
            
            if until:
                until_time = datetime.fromisoformat(until) if isinstance(until, str) else until
                if until_time > now:
                    hours_left = int((until_time - now).total_seconds() / 3600)
                    minutes_left = int(((until_time - now).total_seconds() % 3600) / 60)
                    text += f"   • {name} (осталось {hours_left}ч {minutes_left}м)\n"
                else:
                    text += f"   • {name} (⚠️ истек)\n"
            else:
                text += f"   • {name}\n"
        
        bot.reply_to(m, text, parse_mode="Markdown")
    
    # ---------- КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦА (УПРАВЛЕНИЕ VIP) ----------
    
    @bot.message_handler(commands=['vip'])
    def add_vip(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /vip @user 7d / 30d")
            return
        
        username = args[1].replace('@', '')
        try:
            user = bot.get_chat(f"@{username}")
            uid = user.id
        except:
            bot.reply_to(m, "❌ Пользователь не найден")
            return
        
        until = None
        if len(args) >= 3:
            time_str = args[2].lower()
            if time_str == '7d':
                until = datetime.now() + timedelta(days=7)
            elif time_str == '30d':
                until = datetime.now() + timedelta(days=30)
            else:
                bot.reply_to(m, "❌ Только 7d или 30d")
                return
        
        with db.cur() as c:
            c.execute('INSERT OR REPLACE INTO vip (user_id, username, type, until) VALUES (?, ?, "обычный", ?)', 
                     (uid, username, until))
        
        if until:
            until_str = until.strftime("%d.%m.%Y")
            bot.reply_to(m, f"✅ Обычный VIP для @{username} до {until_str}")
        else:
            bot.reply_to(m, f"✅ Обычный VIP для @{username} (бессрочно)")
    
    @bot.message_handler(commands=['vipglobal'])
    def add_vip_global(m: Message):
        if m.from_user.id != OWNER_ID:
            return
        args = m.text.split()
        if len(args) < 2:
            bot.reply_to(m, "❌ Используй: /vipglobal @user 7d / 30d")
            return
        
        username = args[1].replace('@', '')
        try:
            user = bot.get_chat(f"@{username}")
            uid = user.id
        except:
            bot.reply_to(m, "❌ Пользователь не найден")
            return
        
        until = None
        if len(args) >= 3:
            time_str = args[2].lower()
            if time_str == '7d':
                until = datetime.now() + timedelta(days=7)
            elif time_str == '30d':
                until = datetime.now() + timedelta(days=30)
            else:
                bot.reply_to(m, "❌ Только 7d или 30d")
                return
        
        with db.cur() as c:
            c.execute('INSERT OR REPLACE INTO vip (user_id, username, type, until) VALUES (?, ?, "глобальный", ?)', 
                     (uid, username, until))
        
        if until:
            until_str = until.strftime("%d.%m.%Y")
            bot.reply_to(m, f"✅ Глобальный VIP для @{username} до {until_str}")
        else:
            bot.reply_to(m, f"✅ Глобальный VIP для @{username} (бессрочно)")
    
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
            c.execute('SELECT username, type, until FROM vip ORDER BY until')
            vips = c.fetchall()
        if not vips:
            bot.reply_to(m, "📋 Нет VIP пользователей")
            return
        
        now = datetime.now()
        text = "👑 **VIP пользователи:**\n\n"
        for v in vips:
            username = v[0]
            vip_type = v[1]
            until = v[2]
            
            if until:
                until_time = datetime.fromisoformat(until) if isinstance(until, str) else until
                if until_time > now:
                    days_left = (until_time - now).days
                    text += f"• @{username} - {vip_type} (осталось {days_left} дн)\n"
                else:
                    text += f"• @{username} - {vip_type} (⚠️ истек)\n"
            else:
                text += f"• @{username} - {vip_type} (∞)\n"
        
        bot.reply_to(m, text, parse_mode="Markdown")
    
    # ---------- КОМАНДЫ ДЛЯ ВСЕХ ----------
    
    @bot.message_handler(commands=['start', 'help'])
    def start(m: Message):
        """Простое приветствие без списка команд"""
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
   • Сроки: 7 или 30 дней

🔸 **Глобальный VIP**
   • Освобождение от проверки ВО ВСЕХ группах
   • Иммунитет к мутам
   • Безлимит на медиа
   • Сроки: 7 или 30 дней

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
            c.execute('SELECT name, until FROM channels WHERE group_id = ?', (m.chat.id,))
            channels_data = c.fetchall()
        
        if not channels_data:
            return
        
        now = datetime.now()
        active_channels = []
        for ch in channels_data:
            name = ch[0]
            until = ch[1]
            if until:
                until_time = datetime.fromisoformat(until) if isinstance(until, str) else until
                if until_time <= now:
                    continue
            active_channels.append(name)
        
        if not active_channels:
            return
        
        if not is_subscribed(bot, m.from_user.id, active_channels):
            try:
                bot.delete_message(m.chat.id, m.message_id)
            except:
                pass
            
            name = m.from_user.username or m.from_user.first_name
            text = f"@{name}, ты не подписан на каналы: {', '.join(active_channels)}\nПодпишись, чтобы писать!"
            kb = sub_keyboard(active_channels)
            
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
   • Сроки: 7 или 30 дней

🔸 **Глобальный VIP**
   • Освобождение от проверки ВО ВСЕХ группах
   • Иммунитет к мутам
   • Безлимит на медиа
   • Сроки: 7 или 30 дней

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
