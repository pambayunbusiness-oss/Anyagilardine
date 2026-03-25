import logging
import requests
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
# Token baru yang baru saja kamu berikan
TOKEN = '8621903836:AAGurbT4Qo-HE-qJmAWMhikdFy3V5m-14A0'
# API Key RapidAPI kamu
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
WIB = pytz.timezone('Asia/Jakarta')

# --- HANDLER BOLA ---
async def get_bola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Sedang mengambil data pemain...")
    
    # URL sesuai API "Free API Live Football Data"
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-search-players"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }
    
    try:
        # Mencari daftar pemain populer (mbappe sebagai contoh search)
        res = requests.get(url, headers=headers, params={"query": "mbappe"}, timeout=15)
        res.raise_for_status()
        data = res.json()
        
        # Mengambil list saran pemain dari struktur JSON yang kamu kirim
        suggestions = data.get('response', {}).get('suggestions', [])
        
        if not suggestions:
            await status_msg.edit_text("📭 Tidak ada data ditemukan.")
            return

        msg = "⚽ **Daftar Pemain Populer**\n"
        msg += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        # Ambil 10 pemain teratas
        for p in suggestions[:10]:
            name = p.get('name', 'Unknown')
            team = p.get('teamName', 'Tanpa Klub')
            msg += f"👤 **{name}**\n🏟️ Klub: {team}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error Bola: {e}")
        await status_msg.edit_text("⚠️ Gagal mengambil data. Pastikan bot di Railway sudah di-restart.")

# --- HANDLER ODDS ---
async def get_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🏀 Mengecek bursa NBA...")
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"
    params = {'apiKey': '635af92b5902de211d31a698e1ce2938', 'regions': 'us', 'markets': 'h2h'}
    try:
        res = requests.get(url, params=params, timeout=15)
        data = res.json()
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

# --- MAIN ---
if __name__ == '__main__':
    # drop_pending_updates=True untuk membersihkan sisa tabrakan koneksi
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', lambda u, c: u.message.reply_text("Bot Aktif!\n\n/bola - Cek Data Pemain\n/odds - Bursa NBA")))
    app.add_handler(CommandHandler('bola', get_bola))
    app.add_handler(CommandHandler('odds', get_odds))
    
    print("✅ Bot is running with NEW REVOKED TOKEN...")
    app.run_polling(drop_pending_updates=True)
