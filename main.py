import logging
import asyncio
import pytz
import requests
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
# Gunakan Token Baru dari BotFather & API Key dari Screenshot
TOKEN = '8621903836:AAHpwi9UG3DzmMvRIGOUEINpRv90r2oz-7k'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

WIB = pytz.timezone('Asia/Jakarta')

# Header untuk menghindari blokir
HEADERS_BASE = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

# --- HANDLER BOLA (REVISI SESUAI SCREENSHOT) ---
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("Mencari jadwal bola... 🌍")
    
    # URL sesuai API di screenshot kamu
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-matches-by-date"
    
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
        **HEADERS_BASE
    }
    
    # API ini minta format tanggal YYYYMMDD (contoh: 20260326)
    today_str = datetime.now(WIB).strftime('%Y%m%d')
    
    try:
        res = requests.get(url, headers=headers, params={"date": today_str}, timeout=25)
        res.raise_for_status()
        data = res.json()
        
        # Mengambil list pertandingan dari struktur API ini
        matches = data.get('response', {}).get('matches', [])
        
        if not matches:
            await status_msg.edit_text(f"Tidak ada jadwal bola untuk tanggal {today_str}.")
            return
            
        msg = f"⚽ **Jadwal Bola ({today_str})**\n\n"
        # Ambil 10 pertandingan saja agar tidak terlalu panjang
        for m in matches[:10]:
            league = m.get('league_name', 'Unknown League')
            home = m.get('home_name', 'Home')
            away = m.get('away_name', 'Away')
            time_start = m.get('start_time', '--:--')
            
            msg += f"🏆 {league}\n🥊 **{home}** vs **{away}**\n⏰ `{time_start}`\n---\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error Bola: {e}")
        await status_msg.edit_text("⚠️ Gagal ambil data. Pastikan sudah klik 'Subscribe to Test' di RapidAPI.")

# --- HANDLER ODDS (TETAP LANCAR) ---
async def get_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("Cek Odds NBA... 🎰")
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"
    params = {
        'apiKey': '635af92b5902de211d31a698e1ce2938',
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    try:
        res = requests.get(url, params=params, timeout=25)
        data = res.json()
        if not data:
            await status_msg.edit_text("🎰 Odds belum tersedia.")
            return
        msg = "🎰 **NBA Odds**\n\n"
        for g in data[:8]:
            msg += f"🏀 {g['away_team']} @ {g['home_team']}\n"
            if g['bookmakers']:
                for o in g['bookmakers'][0]['markets'][0]['outcomes']:
                    msg += f"🔹 {o['name']}: `{o['price']}`\n"
            msg += "---\n"
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except Exception as e:
        await status_msg.edit_text("⚠️ Gagal ambil data Odds.")

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', lambda u, c: u.message.reply_text("Bot Aktif!\n/bola - Jadwal Bola\n/odds - Odds NBA")))
    app.add_handler(CommandHandler('bola', get_football))
    app.add_handler(CommandHandler('odds', get_odds))
    
    print("Bot berjalan di Railway...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
