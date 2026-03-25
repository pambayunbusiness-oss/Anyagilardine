import logging
import requests
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
# Token baru dari BotFather (Sudah di-Revoke)
TOKEN = '8621903836:AAHpwi9UG3DzmMvRIGOUEINpRv90r2oz-7k'
# API Key RapidAPI dari Screenshot kamu
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

# Setup Logging agar muncul di Deploy Logs Railway
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

WIB = pytz.timezone('Asia/Jakarta')

# --- HANDLER BOLA ---
async def get_bola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Sedang mengambil jadwal bola...")
    
    # URL sesuai API "Free API Live Football Data" di screenshot kamu
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-matches-by-date"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    # Format tanggal YYYYMMDD (Contoh: 20260326)
    tgl_sekarang = datetime.now(WIB).strftime('%Y%m%d')
    
    try:
        response = requests.get(url, headers=headers, params={"date": tgl_sekarang}, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Mengambil list pertandingan dari struktur API ini
        matches = data.get('response', {}).get('matches', [])
        
        if not matches:
            await status_msg.edit_text(f"📭 Tidak ada jadwal bola untuk hari ini ({tgl_sekarang}).")
            return

        msg = f"⚽ **Jadwal Bola ({tgl_sekarang})**\n\n"
        for m in matches[:10]: # Batasi 10 pertandingan saja
            league = m.get('league_name', 'Liga')
            home = m.get('home_name', 'Tim A')
            away = m.get('away_name', 'Tim B')
            time = m.get('start_time', '--:--')
            msg += f"🏆 {league}\n🥊 **{home}** vs **{away}**\n⏰ `{time}`\n---\n"
            
        await status_msg.edit_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error Bola: {e}")
        await status_msg.edit_text("⚠️ Gagal mengambil data bola. Cek status 'Subscribe' di RapidAPI.")

# --- HANDLER ODDS NBA ---
async def get_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🏀 Mengecek bursa NBA...")
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"
    params = {
        'apiKey': '635af92b5902de211d31a698e1ce2938',
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    try:
        res = requests.get(url, params=params, timeout=15)
        data = res.json()
        if not data:
            await status_msg.edit_text("🎰 Odds NBA belum tersedia.")
            return

        msg = "🎰 **NBA Odds (H2H)**\n\n"
        for g in data[:5]:
            msg += f"🔥 {g['away_team']} @ {g['home_team']}\n"
            if g['bookmakers']:
                for o in g['bookmakers'][0]['markets'][0]['outcomes']:
                    msg += f"🔹 {o['name']}: `{o['price']}`\n"
            msg += "---\n"
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal mengambil data Odds.")

# --- MENJALANKAN BOT ---
if __name__ == '__main__':
    # drop_pending_updates=True penting agar bot tidak tabrakan (Conflict)
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Perintah Bot
    app.add_handler(CommandHandler('start', lambda u, c: u.message.reply_text("Bot Aktif!\n\n/bola - Jadwal Bola\n/odds - Bursa NBA")))
    app.add_handler(CommandHandler('bola', get_bola))
    app.add_handler(CommandHandler('odds', get_odds))
    
    print("✅ Bot is running with the NEW TOKEN...")
    app.run_polling(drop_pending_updates=True)
    
