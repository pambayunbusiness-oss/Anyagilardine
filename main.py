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
    await update.message.reply_text("🏀 *Bot NBA Online!*\nKetik /jadwal untuk cek jadwal terbaru.", parse_mode='Markdown')

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kita coba ambil jadwal bulan ini (Maret 2026)
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        url = f"https://{API_HOST}/nba/schedule"
        # Berdasarkan log kamu, kita minta data bulan Maret 2026
        params = {"year": "2026", "month": "03", "day": "26"}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # LOGIKA PARSING BERDASARKAN SCREENSHOT KAMU
        fixtures = []
        if isinstance(data, list):
            fixtures = data
        elif isinstance(data, dict):
            # API NBA kamu sering membungkus di 'leagueSchedule' atau langsung di root
            fixtures = data.get('leagueSchedule', data.get('games', []))
            if not fixtures and not isinstance(data, list):
                # Jika data adalah dict tunggal (satu pertandingan), jadikan list
                fixtures = [data] if 'homeTeam' in data else []

        if not fixtures or (isinstance(fixtures, list) and len(fixtures) == 0):
            await update.message.reply_text("ℹ️ Tidak ada jadwal NBA ditemukan untuk hari ini di database.")
            return

        pesan = "🏀 *Jadwal NBA Terbaru:* \n\n"
        
        for game in fixtures[:10]:
            # Mengambil data sesuai log: homeTeam, awayTeam, dan status
            home = game.get('homeTeam', 'Team A')
            away = game.get('awayTeam', 'Team B')
            # Ambil status atau waktu
            status = game.get('status', {}).get('description', 'Scheduled')
            waktu = game.get('startTimeUTC', game.get('time', 'TBA'))
            
            # Format tampilan
            pesan += f"🏀 *{away}* @ *{home}*\n"
            pesan += f"🕒 {waktu}\n"
            pesan += f"📝 Status: {status}\n"
            pesan += "────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal memproses data NBA. Coba lagi nanti.")

if __name__ == '__main__':
    if TOKEN and API_KEY:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        print("🚀 Bot NBA Siap Tempur!")
        app.run_polling()
        
