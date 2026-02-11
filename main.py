import os
import telebot
import random
from flask import Flask, request
from dotenv import load_dotenv
import threading

load_dotenv()

# Bot tokeni (Siz bergan token)
TOKEN = os.environ.get("BOT_TOKEN", "8366478184:AAGP8zLve0yfm3ABggvKjHvZmcSDkQt4ehQ")
bot = telebot.TeleBot(TOKEN)

# Flask server (Koyeb 24/7 uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "KAI Bot is running 24/7!", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# 1. Yangi a'zolarni kutib olish
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        first_name = new_member.first_name
        group_name = message.chat.title
        
        # Ramazon tabrigi bilan kutib olish
        welcome_text = (f"Salom {first_name}! 👋\n"
                        f"'{group_name}' guruhiga xush kelibsiz!\n"
                        f"Yaqinlashib kelayotgan Ramazon oyingiz muborak bo'lsin! ✨")
        bot.reply_to(message, welcome_text)

# 2. "кай инфа" buyrug'i (tasodifiy foizlar)
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith("кай инфа"))
def kai_info(message):
    # Savolni ajratib olish
    question = message.text.lower().replace("кай инфа", "").strip()
    if not question:
        bot.reply_to(message, "Iltimos, savol bering. Masalan: 'кай инфа do'stim ahmoq'")
        return
        
    percentage = random.randint(0, 100)
    
    # Turli xil javob variantlari
    responses = [
        f"Menimcha, bu {percentage}% haqiqat.",
        f"Aniq ayta olaman: {percentage}%!",
        f"Mening hisob-kitoblarim bo'yicha: {percentage}%",
        f"Bunga ishonish qiyin, lekin: {percentage}%",
        f"Siz so'radingiz, men javob beraman: {percentage}%"
    ]
    
    bot.reply_to(message, random.choice(responses))

# 3. Aqlli suhbatdosh (Oddiy savol-javoblar)
@bot.message_handler(func=lambda message: message.text and not message.text.startswith("/"))
def chat_logic(message):
    text = message.text.lower()
    
    # Oddiy suhbat mantiqi
    if any(word in text for word in ["salom", "qalaysan", "nima gap"]):
        responses = ["Salom! Men KAI botman. Guruhda zerikmaysiz degan umiddaman!", "Vaalaykum salom! Kayfiyatlar qalay?", "Salom! Men suhbatga tayyorman."]
        bot.reply_to(message, random.choice(responses))
        
    elif any(word in text for word in ["kim", "botsan", "nima bu"]):
        bot.reply_to(message, "Men KAI — guruhlar uchun aqlli va ko'ngilochar botman. Menga 'кай инфа [savol]' deb yozishingiz mumkin.")

    elif "ramazon" in text:
        bot.reply_to(message, "Ramazon — baraka va rahmat oyi. Barchamizga muborak bo'lsin! 🌙")

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Flaskni alohida thread'da ishga tushirish
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Botni ishga tushirish
    print("KAI bot ishga tushdi...")
    bot.infinity_polling()
