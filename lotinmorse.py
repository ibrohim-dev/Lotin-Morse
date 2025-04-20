import telebot
from telebot import types

TOKEN = "7862824775:AAFQGDndsuH_WIcbMgeMw3Kg1XxZ3uH7hgo"
ADMIN_ID = 6939053372
  # O'z ID'ingizni yozing

bot = telebot.TeleBot(TOKEN)

import telebot
from telebot import types

REQUIRED_CHANNEL = "@shaxsiy737"  # <<< shu yerga kanal username'ingni yoz

bot = telebot.TeleBot(TOKEN)

users = set()
blocked_users = set()
user_modes = {}

morse_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    ' ': '/'
}

def to_morse(text):
    return ' '.join(morse_dict.get(ch, '?') for ch in text.upper())

def from_morse(morse_text):
    reverse = {v: k for k, v in morse_dict.items()}
    return ''.join(reverse.get(code, '?') for code in morse_text.strip().split())

# START
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_subscribed(message.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
        )
        bot.send_message(message.chat.id,
            f"⚠️ Botdan foydalanish uchun quyidagi kanalga obuna bo‘ling:\n{REQUIRED_CHANNEL}",
            reply_markup=markup)
        return
        
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!", show_alert=True)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmadingiz!", show_alert=True)

    # Aks holda oddiy boshlanish
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⚡ Lotin → Morse", "◀️ Morse → Lotin", "📊 Admin panel")
    bot.send_message(message.chat.id, "👋 Salom! Men sizga Lotin va Morse o‘rtasida tarjima qilishda yordam beraman.", reply_markup=markup)

# ASOSIY MENYU
def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("⚡ Lotin ➝ Morse", "◀️ Morse ➝ Lotin")
    if chat_id == ADMIN_ID:
        markup.row("🛠 Admin panel")
    bot.send_message(chat_id, "Kerakli xizmatni tanlang:", reply_markup=markup)

# ADMIN PANEL
@bot.message_handler(func=lambda msg: msg.text == "🛠 Admin panel")
def admin_panel(msg):
    if msg.chat.id != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📩 Xabar yuborish", "📊 Statistika")
    markup.row("◀️ Orqaga")
    bot.send_message(msg.chat.id, "Admin paneliga xush kelibsiz:", reply_markup=markup)

# ADMIN: ORQAGA
@bot.message_handler(func=lambda msg: msg.text == "◀️ Orqaga")
def back_to_main(msg):
    user_modes[msg.chat.id] = None
    show_main_menu(msg.chat.id)

# ADMIN: STATISTIKA
@bot.message_handler(func=lambda msg: msg.text == "📊 Statistika")
def stats(msg):
    if msg.chat.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, f"👤 Foydalanuvchilar: {len(users)}\n⛔ Bloklaganlar: {len(blocked_users)}")

# ADMIN: FOYDALANUVCHILARGA XABAR
@bot.message_handler(func=lambda msg: msg.text == "📩 Xabar yuborish")
def ask_broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, "Yubormoqchi bo‘lgan xabaringizni kiriting:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    count = 0
    for uid in users.copy():
        try:
            bot.send_message(uid, message.text)
            count += 1
        except:
            blocked_users.add(uid)
    bot.send_message(message.chat.id, f"✅ Xabar {count} ta foydalanuvchiga yuborildi.")

# LOTIN -> MORSE
@bot.message_handler(func=lambda msg: msg.text == "⚡ Lotin ➝ Morse")
def set_latin_mode(msg):
    user_modes[msg.chat.id] = "latin"
    bot.send_message(msg.chat.id, "✍️ Lotin matn yuboring:")

# MORSE -> LOTIN
@bot.message_handler(func=lambda msg: msg.text == "◀️ Morse ➝ Lotin")
def set_morse_mode(msg):
    user_modes[msg.chat.id] = "morse"
    bot.send_message(msg.chat.id, "✍️ Morse kod yuboring:")

# TARJIMA
# @bot.message_handler(func=lambda msg: True)
# def translate(msg):
#    mode = user_modes.get(msg.chat.id)
#    if mode == "latin":
#        result = to_morse(msg.text)
#        bot.send_message(msg.chat.id, f"📄 Morse:\n`{result}`", parse_mode="Markdown")
#    elif mode == "morse":
#        result = from_morse(msg.text)
#        bot.send_message(msg.chat.id, f"🔁 Lotin:\n`{result}`", parse_mode="Markdown")



import re

@bot.message_handler(func=lambda msg: True)
def translate(msg):
    mode = user_modes.get(msg.chat.id)

    # Matndan barcha Telegram formatlarini olib tashlaymiz
    text = re.sub(r'[*_`~>|]', '', msg.text or '')

    if mode == "latin":
        result = to_morse(text)
        bot.send_message(msg.chat.id, f"📄 Morse:\n`{result}`", parse_mode="Markdown")
    elif mode == "morse":
        result = from_morse(text)
        bot.send_message(msg.chat.id, f"🔁 Lotin:\n`{result}`", parse_mode="Markdown")
        
        
        
        
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        return False




# Botni ishga tushurish
bot.polling(none_stop=True)