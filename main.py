import os
import time
import random
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from nba_api.live.nba.endpoints import scoreboard

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_nba_schedule():
    try:
        # Mengambil data papan skor live (termasuk jadwal hari ini)
        sb = scoreboard.ScoreBoard()
        data = sb.get_dict()
        games = data['scoreboard']['games']
        game_date = data['scoreboard']['gameDate']

        if not games:
            return f"📅 *Jadwal NBA ({game_date})*\n\nTidak ada pertandingan yang dijadwalkan hari ini."

        res = f"🏀 *Jadwal NBA Hari Ini ({game_date})*\n\n"
        res += "`Waktu (ET) | Matchup`\n"
        res += "---------------------------\n"
        
        for game in games:
            home_team = game['homeTeam']['teamName']
            away_team = game['awayTeam']['teamName']
            # Waktu di API biasanya dalam format string ET
            start_time = game['gameStatusText'] 
            
            res += f"🕒 `{start_time}`\n"
            res += f"🏟️ *{away_team}* vs *{home_team}*\n\n"
            
        return res
    except Exception as e:
        return f"⚠️ Gagal mengambil jadwal: {str(e)}"

# Handler perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Gunakan perintah /schedule untuk melihat jadwal pertandingan NBA hari ini."
    )

# Handler perintah /schedule
async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Sedang mengambil jadwal terbaru...")
    reply = get_nba_schedule()
    await update.message.reply_text(reply, parse_mode='Markdown')

if __name__ == '__main__':
    # Pastikan TOKEN sudah diisi di Environment Variables Railway
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN tidak ditemukan di Environment Variables!")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('schedule', schedule_handler))
        
        print("Bot Jadwal NBA sedang berjalan...")
        application.run_polling()
        
