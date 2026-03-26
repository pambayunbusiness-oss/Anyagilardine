import os
import time
import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# Logging untuk memantau error di Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Konfigurasi Header NBA
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
]

def get_nba_stats(player_name):
    try:
        nba_players = players.find_players_by_full_name(player_name)
        if not nba_players:
            return f"❌ Pemain '{player_name}' tidak ditemukan."
        
        player_id = nba_players[0]['id']
        headers = {'Host': 'stats.nba.com', 'User-Agent': random.choice(USER_AGENTS), 'Referer': 'https://stats.nba.com/'}
        
        career = playercareerstats.PlayerCareerStats(player_id=player_id, headers=headers, timeout=30)
        df = career.get_data_frames()[0].tail(5) # Ambil 5 musim terakhir
        
        # Format pesan untuk Telegram
        res = f"🏀 *Statistik: {nba_players[0]['full_name']}*\n\n"
        res += "`Season | Team | PTS | REB | AST`\n"
        for _, row in df.iterrows():
            res += f"`{row['SEASON_ID']} | {row['TEAM_ABBREVIATION']}  | {row['PTS']} | {row['REB']} | {row['AST']}`\n"
        return res
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Handler perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Masukkan nama pemain NBA untuk melihat statistiknya (Contoh: Giannis Antetokounmpo)")

# Handler pesan teks
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text(f"🔍 Mencari data untuk: {user_input}...")
    reply = get_nba_stats(user_input)
    await update.message.reply_text(reply, parse_mode='Markdown')

if __name__ == '__main__':
    # AMBIL TOKEN DARI ENVIRONMENT VARIABLE (Sangat disarankan untuk Railway)
    # Jika ingin testing lokal cepat, ganti os.getenv dengan "NOMOR_TOKEN_MU"
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot sedang berjalan...")
    application.run_polling()
    
