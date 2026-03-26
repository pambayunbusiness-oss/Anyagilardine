import os
import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from nba_api.live.nba.endpoints import scoreboard

# Logging untuk Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_nba_update():
    try:
        # Mengambil data scoreboard live
        sb = scoreboard.ScoreBoard()
        data = sb.get_dict()
        games = data['scoreboard']['games']
        game_date = data['scoreboard']['gameDate']

        if not games:
            return f"📅 *NBA Update ({game_date})*\n\nTidak ada pertandingan yang dijadwalkan hari ini."

        res = f"🏀 *NBA Update ({game_date})*\n"
        res += "----------------------------------\n\n"
        
        for game in games:
            home_team = game['homeTeam']['teamName']
            home_score = game['homeTeam']['score']
            away_team = game['awayTeam']['teamName']
            away_score = game['awayTeam']['score']
            status = game['gameStatusText'] # Contoh: "Final", "Q3 05:20", atau "10:00 PM ET"

            # Logika menentukan pemenang/unggul
            away_icon = ""
            home_icon = ""
            
            if home_score > away_score:
                home_icon = "🏆 "
            elif away_score > home_score:
                away_icon = "🏆 "

            res += f"🕒 *Status:* `{status}`\n"
            res += f"{away_icon}*Away:* {away_team} ({away_score})\n"
            res += f"{home_icon}*Home:* {home_team} ({home_score})\n"
            res += "----------------------------------\n"
            
        return res
    except Exception as e:
        logging.error(f"Error fetching NBA data: {e}")
        return f"⚠️ Gagal mengambil data NBA: Server sedang sibuk."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Gunakan perintah /nba untuk melihat jadwal, skor, dan pemenang pertandingan hari ini.")

async def nba_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Sedang mengambil data NBA terbaru...")
    reply = get_nba_update()
    await update.message.reply_text(reply, parse_mode='Markdown')

if __name__ == '__main__':
    # Pastikan variabel TELEGRAM_TOKEN sudah ada di Railway Variables
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        print("Gagal: TELEGRAM_TOKEN tidak ditemukan!")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Perintah baru: /nba
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('nba', nba_handler))
        
        print("Bot NBA Live sedang berjalan...")
        application.run_polling()
            
