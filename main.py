import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-nba-v1.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 *Bot NBA Ready!*\nKetik /jadwal untuk lihat pertandingan terdekat.")

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        # KITA UBAH DISINI: Mengambil 10 pertandingan mendatang (Next)
        # Jika endpoint /schedule tidak mendukung 'next', kita pakai /list
        url = f"https://{API_HOST}/nba/schedule"
        
        # Kita coba ambil data tanpa filter tanggal yang ketat agar tidak zonk
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Log untuk kita cek di Railway
        print(f"DEBUG DATA: {str(data)[:500]}")

        fixtures = []
        if isinstance(data, list):
            fixtures = data
        elif isinstance(data, dict):
            # Coba bongkar berbagai kemungkinan nama field
            fixtures = data.get('games', data.get('leagueSchedule', data.get('data', [])))

        if not fixtures:
            await update.message.reply_text("ℹ️ Database API sedang tidak memberikan jadwal. Coba lagi nanti malam saat jam tanding US.")
            return

        pesan = "🏀 *15 Pertandingan NBA Terdekat:* \n\n"
        
        # Ambil 10 saja agar tidak kepanjangan
        for game in fixtures[:15]:
            home = game.get('homeTeam', 'Unknown')
            away = game.get('awayTeam', 'Unknown')
            waktu = game.get('startTimeUTC', game.get('time', 'TBA'))
            status = game.get('status', {}).get('description', 'Scheduled')

            pesan += f"🏀 *{away}* vs *{home}*\n"
            pesan += f"⏰ {waktu}\n"
            pesan += f"🏁 Status: {status}\n"
            pesan += "────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal menarik data dari server NBA.")

if __name__ == '__main__':
    if TOKEN and API_KEY:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        print("🚀 Bot NBA Aktif!")
        app.run_polling()
        
