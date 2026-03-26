import os
import requests
import logging
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging untuk Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Konfigurasi API dari Variables Railway
API_KEY = os.getenv("FOOTBALL_API_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"

# Pemetaan Perintah ke ID Liga API-Football
LIGA_IDS = {
    'pl': 39,      # Premier League
    'laliga': 140, # La Liga
    'ucl': 2,       # UEFA Champions League
    'seria': 135,  # Serie A
    'wc': 1        # World Cup
}

def get_league_schedule(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    tz_jkt = pytz.timezone('Asia/Jakarta')
    today = datetime.now(tz_jkt).strftime('%Y-%m-%d')
    
    # Filter berdasarkan Liga dan Tanggal Hari Ini
    querystring = {"date": today, "league": league_id, "timezone": "Asia/Jakarta"}
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        
        if not data.get('response'):
            return f"📅 Tidak ada pertandingan dijadwalkan untuk liga ini hari ini ({today})."

        res = f"⚽ *Update Pertandingan ({today})*\n"
        res += "------------------------------------------\n\n"
        
        for match in data['response']:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            h_score = match['goals']['home']
            a_score = match['goals']['away']
            status = match['fixture']['status']['long']
            
            score_display = f"{h_score} - {a_score}" if h_score is not None else "vs"
            
            res += f"🏟️ *{home}* {score_display} *{away}*\n"
            res += f"🕒 Status: `{status}`\n"
            res += "------------------------------------------\n"
            
        return res
    except Exception as e:
        logging.error(f"Error API: {e}")
        return "⚠️ Gagal mengambil data. Cek koneksi API."

# Handler Dinamis untuk Liga
async def league_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mengambil perintah yang diketik (misal: /pl menjadi pl)
    command = update.message.text.split('@')[0].replace('/', '').lower()
    league_id = LIGA_IDS.get(command)
    
    if league_id:
        await update.message.reply_text(f"🔍 Mencari jadwal {command.upper()}...")
        reply = get_league_schedule(league_id)
        await update.message.reply_text(reply, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ *Bot Jadwal Bola Aktif!*\n\n"
        "Gunakan perintah berikut:\n"
        "/pl - Premier League\n"
        "/laliga - La Liga\n"
        "/ucl - Champions League\n"
        "/seria - Serie A\n"
        "/wc - World Cup",
        parse_mode='Markdown'
    )

if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_TOKEN_BOLA")
    
    if not TOKEN:
        logging.error("Variabel TELEGRAM_TOKEN_BOLA tidak ditemukan!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler('start', start))
        
        # Mendaftarkan semua perintah liga secara otomatis
        for cmd in LIGA_IDS.keys():
            app.add_handler(CommandHandler(cmd, league_handler))
            
        logging.info("Bot Sepak Bola Multi-Liga Berjalan...")
        app.run_polling()
            
