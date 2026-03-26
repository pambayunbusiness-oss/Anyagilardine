import os
import logging
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi Environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-nba-v1.p.rapidapi.com" 

# Setup Logging agar muncul di Railway Deploy Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 *Bot NBA Online!*\nKetik /jadwal untuk cek pertandingan 2 hari ke depan.")

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Logika mengambil tanggal 2 hari ke depan (48 jam)
    target_date = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        url = f"https://{API_HOST}/games"
        params = {"date": target_date}
        
        # Tambahkan timeout agar bot tidak gantung jika API lambat
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        fixtures = data.get('response', [])

        if not fixtures:
            await update.message.reply_text(f"ℹ️ Tidak ada jadwal NBA untuk tanggal {target_date}.\n\nMusim mungkin sedang libur atau jadwal belum dirilis.")
            return

        pesan = f"🏀 *Jadwal NBA ({target_date}):*\n\n"
        
        for g in fixtures[:15]:
            try:
                away = g['teams']['visitors']['name']
                home = g['teams']['home']['name']
                status = g['status']['long']
                
                s_away = g['scores']['visitors']['points']
                s_home = g['scores']['home']['points']
                
                if "Scheduled" in status or "Not Started" in status:
                    pesan += f"⏰ {away} vs {home}\n"
                else:
                    pesan += f"🏀 {away} ({s_away}) - ({s_home}) {home}\n"
                    pesan += f"💬 Status: {status}\n"
                
                pesan += "────────────────────\n"
            except KeyError:
                continue
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal mengambil data. Pastikan API Key benar dan sudah Subscribe ke API-NBA v1.")

if __name__ == '__main__':
    if not TOKEN or not API_KEY:
        print("❌ ERROR: Variabel TELEGRAM_TOKEN atau RAPIDAPI_KEY belum diisi di Railway!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        
        print("🚀 Bot NBA Berjalan di Railway...")
        # drop_pending_updates=True penting agar bot tidak crash saat restart
        app.run_polling(drop_pending_updates=True)
    
