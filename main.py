import os
import telebot
import yt_dlp
from flask import Flask, request
from dotenv import load_dotenv
import threading
import time

load_dotenv()

# Bot tokenini oling
TOKEN = "8366478184:AAGP8zLve0yfm3ABggvKjHvZmcSDkQt4ehQ"
bot = telebot.TeleBot(TOKEN)

# Flask serverni sozlash (Koyeb uchun)
app = Flask(__name__)

# Vaqtinchalik fayllar uchun papka
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.route('/')
def home():
    return "Bot is running 24/7!", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga Instagram yoki YouTube linkini yuboring, men uni yuklab beraman.\n\nAgar faqat musiqasini xohlasangiz, linkdan keyin 'audio' so'zini yozing.")

def download_media(url, is_audio=False):
    ydl_opts = {
        'format': 'best' if not is_audio else 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4' if not is_audio else None,
    }
    
    if is_audio:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if is_audio:
            filename = os.path.splitext(filename)[0] + '.mp3'
        return filename

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    is_audio = 'audio' in url.lower()
    if is_audio:
        url = url.lower().replace('audio', '').strip()

    if not (url.startswith('http://') or url.startswith('https://')):
        bot.reply_to(message, "Iltimos, to'g'ri link yuboring.")
        return

    msg = bot.reply_to(message, "Yuklanmoqda... Iltimos kuting.")
    
    try:
        file_path = download_media(url, is_audio)
        
        with open(file_path, 'rb') as f:
            if is_audio:
                bot.send_audio(message.chat.id, f)
            else:
                bot.send_video(message.chat.id, f)
        
        # Faylni o'chirish
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"Xatolik yuz berdi: {str(e)}", message.chat.id, msg.message_id)

def run_flask():
    # Koyeb PORT muhit o'zgaruvchisini beradi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Webhookni sozlash (Keyinchalik Koyeb URL'ini qo'yish kerak bo'ladi)
    # Hozircha polling bilan ishga tushiramiz, lekin hostingda webhook afzal
    # Koyeb uchun: bot.remove_webhook()
    # bot.set_webhook(url=f"https://your-app-name.koyeb.app/{TOKEN}")
    
    # Flaskni alohida thread'da ishga tushirish (24/7 saqlash uchun)
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Pollingni ishga tushirish
    bot.infinity_polling()
