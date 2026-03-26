import os
import logging
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi sesuai screenshot RapidAPI kamu
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "sports-information.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 Bot Jadwal NBA Aktif! Ketik /jadwal")

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ambil tanggal hari ini
    now = datetime.datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        # Endpoint sesuai screenshot: /nba/schedule
        url = f"https://{API_HOST}/nba/schedule"
        params = {"year": year, "month": month, "day": day}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Log untuk cek di Railway
        print(f"DEBUG NBA: {response.status_code} - {response.text[:100]}")
        
        # Struktur data NBA biasanya berbeda, kita sesuaikan:
        games = data # API ini biasanya langsung mengembalikan list atau objek games
        
        if not games:
            await update.message.reply_text(f"ℹ️ Tidak ada jadwal NBA untuk hari ini ({day}-{month}-{year}).")
            return

        pesan = f"🏀 *Jadwal NBA Hari Ini ({day}/{month}):*\n\n"
        
        # Loop data (sesuaikan dengan struktur respon API kamu)
        # Jika responnya berbentuk list:
        for game in games[:10]:
            # Sesuaikan nama field (home/away/time) dengan hasil 'Test Endpoint' kamu
            home = game.get('homeTeam', 'Team A')
            away = game.get('awayTeam', 'Team B')
            time = game.get('gameTime', '--:--')
            
            pesan += f"⏰ {time} | {home} vs {away}\n"
            pesan += "────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal mengambil jadwal NBA. Cek log.")

if __name__ == '__main__':
    if TOKEN and API_KEY:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        print("🏀 Bot NBA Siap!")
        app.run_polling()
        
