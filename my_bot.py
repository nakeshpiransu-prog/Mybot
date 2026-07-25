import telebot
import sqlite3
import re

# ⚠️ यहाँ अपना Bot Token डालें
TOKEN = '8954535597:AAHxhuzQ4L8cya1tw1g01RjmOOD5Uc2MFa4'
bot = telebot.TeleBot(TOKEN)

# --- DATABASE SETUP ---
conn = sqlite3.connect('bot_settings.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS group_settings (
    chat_id INTEGER PRIMARY KEY,
    nolinks INTEGER DEFAULT 0,
    noevents INTEGER DEFAULT 0,
    nobots INTEGER DEFAULT 0,
    noforwards INTEGER DEFAULT 0,
    nocontacts INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS blacklist (
    chat_id INTEGER,
    word TEXT
)
''')
conn.commit()

# --- HELPER FUNCTIONS ---
def get_setting(chat_id, setting_name):
    cursor.execute(f"SELECT {setting_name} FROM group_settings WHERE chat_id = ?", (chat_id,))
    res = cursor.fetchone()
    if not res:
        cursor.execute("INSERT INTO group_settings (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
        return 0
    return res[0]

def toggle_setting(chat_id, setting_name):
    current = get_setting(chat_id, setting_name)
    new_status = 1 if current == 0 else 0
    cursor.execute(f"UPDATE group_settings SET {setting_name} = ? WHERE chat_id = ?", (new_status, chat_id))
    conn.commit()
    return new_status

def is_admin(chat_id, user_id):
    try:
        status = bot.get_chat_member(chat_id, user_id).status
        return status in ['administrator', 'creator']
    except Exception:
        return False

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "🛡️ Protectron Guard Active!\nग्रुप सेटिंग्स के लिए /status टाइप करें।")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    chat_id = message.chat.id
    nolinks = "✅ ON" if get_setting(chat_id, 'nolinks') else "❌ OFF"
    noevents = "✅ ON" if get_setting(chat_id, 'noevents') else "❌ OFF"
    nobots = "✅ ON" if get_setting(chat_id, 'nobots') else "❌ OFF"
    noforwards = "✅ ON" if get_setting(chat_id, 'noforwards') else "❌ OFF"
    nocontacts = "✅ ON" if get_setting(chat_id, 'nocontacts') else "❌ OFF"
    
    msg = (f"⚙️ **ग्रुप सिक्योरिटी सेटिंग्स:**\n\n"
           f"/nolinks - Anti-Link: {nolinks}\n"
           f"/noevents - Clean Join/Left: {noevents}\n"
           f"/nobots - Anti-Bot Add: {nobots}\n"
           f"/noforwards - Anti-Forward: {noforwards}\n"
           f"/nocontacts - Anti-Contact Share: {nocontacts}\n")
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['nolinks', 'noevents', 'nobots', 'noforwards', 'nocontacts'])
def toggle_commands(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ यह कमांड केवल एडमिन के लिए है!")
        return
    
    cmd = message.text.split()[0].replace('/', '')
    status = toggle_setting(message.chat.id, cmd)
    state_str = "ON" if status else "OFF"
    bot.reply_to(message, f"⚙️ **{cmd}** अब **{state_str}** है।")

# --- BAN / UNBAN COMMANDS ---
@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        bot.ban_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"🚫 {target.first_name} को बैन कर दिया गया है।")

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        bot.unban_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"✅ यूजर को अनबैन कर दिया गया है।")

# --- FILTERS ---
@bot.message_handler(content_types=['new_chat_members', 'left_chat_member'])
def service_cleaner(message):
    chat_id = message.chat.id
    if message.new_chat_members and get_setting(chat_id, 'nobots'):
        for new_user in message.new_chat_members:
            if new_user.is_bot and not is_admin(chat_id, message.from_user.id):
                bot.ban_chat_member(chat_id, new_user.id)
                
    if get_setting(chat_id, 'noevents'):
        try:
            bot.delete_message(chat_id, message.message_id)
        except Exception:
            pass

@bot.message_handler(func=lambda m: True, content_types=['text', 'forward_from', 'forward_from_chat', 'contact', 'animation'])
def main_filter(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if is_admin(chat_id, user_id):
        return

    if get_setting(chat_id, 'noforwards') and (message.forward_from or message.forward_from_chat):
        bot.delete_message(chat_id, message.message_id)
        return

    if get_setting(chat_id, 'nocontacts') and message.contact:
        bot.delete_message(chat_id, message.message_id)
        return

    if get_setting(chat_id, 'nolinks') and message.text:
        urls = re.findall(r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,})', message.text)
        if urls:
            bot.delete_message(chat_id, message.message_id)
            return

print("Protectron Bot is running...")
bot.infinity_polling()
