import os
import logging
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "sports-information.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 *Bot Jadwal NBA Aktif!* Ketik /jadwal")

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    params = {
        "year": now.strftime('%Y'),
        "month": now.strftime('%m'),
        "day": now.strftime('%d')
    }
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        url = f"https://{API_HOST}/nba/schedule"
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # DEBUG: Muncul di Logs Railway untuk kita cek struktur aslinya
        print(f"DEBUG DATA TYPE: {type(data)}")
        print(f"DEBUG FULL DATA: {data}")

        # LOGIKA PERBAIKAN:
        # Jika data berupa list, pakai langsung. Jika dictionary, cari kunci 'games' atau 'data'
        fixtures = []
        if isinstance(data, list):
            fixtures = data
        elif isinstance(data, dict):
            fixtures = data.get('games', data.get('data', []))

        if not fixtures:
            await update.message.reply_text(f"ℹ️ Tidak ada jadwal NBA untuk hari ini ({params['day']}/{params['month']}).")
            return

        pesan = f"🏀 *Jadwal NBA ({params['day']}/{params['month']}):*\n\n"
        
        for game in fixtures[:15]:
            # Ambil data dengan aman menggunakan .get()
            away = game.get('awayTeam', 'Unknown')
            home = game.get('homeTeam', 'Unknown')
            waktu = game.get('time', game.get('gameTime', 'TBA'))

            pesan += f"🏀 {away} vs {home}\n"
            pesan += f"⏰ Jam: {waktu}\n"
            pesan += "────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"⚠️ Gagal memproses data.\nSaran: Cek Logs Railway bagian 'DEBUG FULL DATA'.")

if __name__ == '__main__':
    if TOKEN and API_KEY:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        print("🚀 Bot NBA Berjalan...")
        app.run_polling()
    
