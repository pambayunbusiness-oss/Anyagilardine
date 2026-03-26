import os
import requests
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Setup Logging agar muncul di Log Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

API_KEY = "129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89"
API_HOST = "api-football-v1.p.rapidapi.com"

def get_football_schedule():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Ambil Liga Inggris (39), Spanyol (140), Italia (135), Jerman (78), Perancis (61)
    # Jika ingin semua liga, hapus parameter 'league'
    querystring = {"date": today, "timezone": "Asia/Jakarta"}
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        data = response.json()
        
        if not data.get('response'):
            return f"📅 *Jadwal Bola ({today})*\n\nBelum ada jadwal tersedia saat ini."

        res = f"⚽ *Jadwal & Skor Bola ({today})*\n"
        res += "----------------------------------\n\n"
        
        for match in data['response'][:10]: # Limit 10 pertandingan saja
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            h_score = match['goals']['home']
            a_score = match['goals']['away']
            status = match['fixture']['status']['short']
            
            score = f"{h_score} - {a_score}" if h_score is not None else "vs"
            res += f"🏟️ *{home}* {score} *{away}*\n🕒 Status: `{status}`\n\n"
            
        return res
    except Exception as e:
        return f"⚠️ Error API: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Bola Aktif! Gunakan /bola untuk jadwal hari ini.")

async def bola_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User meminta jadwal bola")
    await update.message.reply_text("🔍 Menghubungi server skor...")
    reply = get_football_schedule()
    await update.message.reply_text(reply, parse_mode='Markdown')

if __name__ == '__main__':
    # AMBIL TOKEN DARI RAILWAY
    TOKEN = os.getenv("TELEGRAM_TOKEN_BOLA")
    
    if not TOKEN:
        logging.error("Variabel TELEGRAM_TOKEN_BOLA tidak ditemukan!")
    else:
        logging.info("Memulai Bot Sepak Bola...")
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('bola', bola_handler))
        
        app.run_polling()
        
