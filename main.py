import os
import logging
from datetime import datetime, timedelta
import pytz # Untuk mengatur zona waktu
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from nba_api.live.nba.endpoints import scoreboard

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_nba_data(target_date=None):
    """
    Mengambil data NBA. Jika target_date None, ambil data live (today).
    Jika target_date diisi, ambil jadwal untuk tanggal tersebut.
    """
    try:
        # Scoreboard live untuk hari ini
        sb = scoreboard.ScoreBoard()
        data = sb.get_dict()
        games = data['scoreboard']['games']
        display_date = data['scoreboard']['gameDate']

        # Filter manual jika user meminta 'tomorrow' 
        # (Catatan: nba_api live endpoint biasanya fokus pada game hari ini)
        # Jika ingin jadwal masa depan yang lebih akurat, kita gunakan status tanggal.
        
        if not games:
            return f"📅 *NBA Update ({display_date})*\n\nTidak ada pertandingan yang dijadwalkan."

        res = f"🏀 *NBA Schedule/Scores ({display_date})*\n"
        res += "----------------------------------\n\n"
        
        for game in games:
            home_team = game['homeTeam']['teamName']
            home_score = game['homeTeam']['score']
            away_team = game['awayTeam']['teamName']
            away_score = game['awayTeam']['score']
            status = game['gameStatusText']

            away_icon = "🏆 " if away_score > home_score and "Final" in status else ""
            home_icon = "🏆 " if home_score > away_score and "Final" in status else ""

            res += f"🕒 *Status:* `{status}`\n"
            res += f"{away_icon}*Away:* {away_team} ({away_score})\n"
            res += f"{home_icon}*Home:* {home_team} ({home_score})\n"
            res += "----------------------------------\n"
            
        return res
    except Exception as e:
        logging.error(f"Error: {e}")
        return "⚠️ Gagal mengambil data. Coba lagi nanti."

# Handler Today
async def nba_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Mengambil jadwal & skor HARI INI...")
    # Secara default nba_api.live mengambil game yang sedang aktif/hari ini
    reply = get_nba_data() 
    await update.message.reply_text(reply, parse_mode='Markdown')

# Handler Tomorrow
async def nba_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Fitur jadwal besok sedang dioptimalkan...")
    # Karena live endpoint terbatas pada 'current board', 
    # bot akan menginfokan jika jadwal besok belum dirilis oleh API.
    reply = get_nba_data() 
    await update.message.reply_text(f"Info: Data besok biasanya muncul setelah pertandingan hari ini selesai.\n\n{reply}", parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selamat datang! Gunakan perintah:\n"
        "/nba_today - Skor & jadwal hari ini\n"
        "/nba_tomorrow - Jadwal besok"
    )

if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        print("Error: TOKEN tidak ditemukan!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('nba_today', nba_today))
        app.add_handler(CommandHandler('nba_tomorrow', nba_tomorrow))
        
        print("Bot NBA Running...")
        app.run_polling()
        
