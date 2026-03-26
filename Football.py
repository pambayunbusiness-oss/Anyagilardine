import os
import requests
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Konfigurasi API Football (RapidAPI)
API_KEY = "129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89"
API_HOST = "api-football-v1.p.rapidapi.com"

def get_football_schedule():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    # Mengambil jadwal hari ini berdasarkan tanggal sistem
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Parameter: Kita ambil liga populer (misal: Premier League ID = 39) 
    # Kamu bisa hapus 'league': '39' jika ingin semua liga (tapi datanya akan sangat banyak)
    querystring = {"date": today, "timezone": "Asia/Jakarta"}
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        
        if not data['response']:
            return f"📅 *Jadwal Bola ({today})*\n\nBelum ada jadwal pertandingan besar hari ini."

        res = f"⚽ *Jadwal & Skor Bola ({today})*\n"
        res += "----------------------------------\n\n"
        
        # Ambil maksimal 15 pertandingan agar tidak kepanjangan di chat
        for match in data['response'][:15]:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            home_score = match['goals']['home']
            away_score = match['goals']['away']
            status = match['fixture']['status']['short'] # FT, NS (Not Started), 1H, 2H
            league = match['league']['name']
            
            # Format skor jika sudah mulai/selesai
            score_text = f"{home_score} - {away_score}" if home_score is not None else "vs"
            
            res += f"🏆 *{league}*\n"
            res += f"🏟️ {home} {score_text} {away}\n"
            res += f"🕒 Status: `{status}`\n"
            res += "----------------------------------\n"
            
        return res
    except Exception as e:
        logging.error(f"Error Football API: {e}")
        return "⚠️ Gagal mengambil data sepak bola. Cek koneksi API."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Gunakan /bola untuk melihat jadwal pertandingan sepak bola hari ini.")

async def bola_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Sedang menarik data dari server...")
    reply = get_football_schedule()
    await update.message.reply_text(reply, parse_mode='Markdown')

if __name__ == '__main__':
    # Gunakan Token Bot Telegram khusus untuk Bola
    TOKEN = os.getenv("TELEGRAM_TOKEN_BOLA")
    
    if not TOKEN:
        print("Gagal: TELEGRAM_TOKEN_BOLA tidak diset di Railway!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('bola', bola_handler))
        
        print("Bot Sepak Bola (API-Football) aktif...")
        app.run_polling()
          
