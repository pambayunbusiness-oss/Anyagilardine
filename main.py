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
    await update.message.reply_text("🏀 *Bot Jadwal NBA Aktif!*\nKetik /jadwal untuk cek pertandingan.", parse_mode='Markdown')

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ambil tanggal hari ini (NBA biasanya pakai waktu US, kita coba hari ini dulu)
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
        # Endpoint sesuai screenshot kamu
        url = f"https://{API_HOST}/nba/schedule"
        response = requests.get(url, headers=headers, params=params)
        
        # DEBUG: Cek isi asli API di Logs Railway
        print(f"DEBUG RESPONSE: {response.text[:200]}")
        
        data = response.json()
        
        # Di API NBA ini, datanya biasanya langsung berupa LIST []
        if not data or len(data) == 0:
            await update.message.reply_text(f"ℹ️ Tidak ada pertandingan NBA hari ini ({params['day']}/{params['month']}).")
            return

        pesan = f"🏀 *Jadwal NBA ({params['day']}/{params['month']}):*\n\n"
        
        for game in data[:15]:
            # Sesuaikan dengan nama field di API NBA (biasanya: awayTeam, homeTeam, time)
            away = game.get('awayTeam', 'Unknown')
            home = game.get('homeTeam', 'Unknown')
            waktu = game.get('time', 'TBA')
            location = game.get('location', '')

            pesan += f"🏀 {away} vs {home}\n"
            pesan += f"⏰ Jam: {waktu}\n"
            if location: pesan += f"📍 {location}\n"
            pesan += "────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        # Jika error, kita kirim pesan yang lebih jelas
        await update.message.reply_text(f"⚠️ Terjadi kesalahan saat membaca data NBA.\nDetail: {str(e)[:50]}")

if __name__ == '__main__':
    if not TOKEN or not API_KEY:
        print("❌ ERROR: TOKEN atau API_KEY belum diisi di Railway!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        print("🚀 Bot NBA Berjalan...")
        app.run_polling()
