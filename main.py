import os
import logging
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi (GANTI HOST-NYA)
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-nba-v1.p.rapidapi.com" # Host standar NBA

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 *Bot NBA Online!*\nKetik /jadwal untuk cek jadwal hari ini.")

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        # Endpoint standar API-NBA v1
        url = f"https://{API_HOST}/games"
        params = {"date": today}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Ambil list dari 'response'
        fixtures = data.get('response', [])

        if not fixtures:
            await update.message.reply_text(f"ℹ️ Tidak ada jadwal NBA untuk hari ini ({today}).\n\nTips: NBA biasanya baru rilis jadwal saat jam tanding Amerika dimulai.")
            return

        pesan = f"🏀 *Jadwal NBA Hari Ini ({today}):*\n\n"
        
        for g in fixtures[:15]:
            away = g['teams']['visitors']['name']
            home = g['teams']['home']['name']
            status = g['status']['long']
            
            # Ambil skor jika sudah/sedang main
            s_away = g['scores']['visitors']['points']
            s_home = g['scores']['home']['points']
            
            if status == "Scheduled":
                pesan += f"⏰ {away} vs {home}\n"
            else:
                pesan += f"🏀 {away} ({s_away}) - ({s_home}) {home}\n"
                pesan += f"💬 Status: {status}\n"
            
            pesan += "────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal mengambil data. Pastikan kamu sudah 'Subscribe' ke API-NBA v1 di RapidAPI.")

if __name__ == '__main__':
    if TOKEN and API_KEY:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        app.run_polling()
            
