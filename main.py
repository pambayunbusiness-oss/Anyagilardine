import logging
import requests
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

FOOTBALL_LEAGUES = {"ucl": 2, "premier": 39, "laliga": 140, "seria": 135}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽🏀 **Bot Jadwal Sports Gabungan**\n\n"
        "• `/next ucl` - Jadwal Bola (UCL, EPL, dll)\n"
        "• `/nba` - Jadwal NBA (Hari Ini & Besok)",
        parse_mode='Markdown'
    )

# --- FUNGSI BOLA ---
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next ucl`")
        return
    query = context.args[0].lower()
    league_id = FOOTBALL_LEAGUES.get(query)
    if not league_id:
        await update.message.reply_text("❌ Liga tidak terdaftar.")
        return

    status_msg = await update.message.reply_text(f"⏳ Menarik data {query.upper()}...")
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "api-football-v1.p.rapidapi.com"}
    params = {"league": league_id, "next": "10"}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        fixtures = res.json().get('response', [])
        if not fixtures:
            await status_msg.edit_text("📅 Jadwal belum tersedia.")
            return

        msg = f"📅 **Jadwal {query.upper()}**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for f in fixtures:
            home, away = f['teams']['home']['name'], f['teams']['away']['name']
            utc_time = datetime.strptime(f['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
            wib_time = utc_time.astimezone(pytz.timezone('Asia/Jakarta')).strftime('%d %b, %H:%M WIB')
            msg += f"🏟️ **{home} vs {away}**\n⏰ {wib_time}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal koneksi API Bola.")

# --- FUNGSI NBA (AUTO-SEARCH 2 HARI) ---
async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🏀 Mencari jadwal NBA (2 Hari Terakhir/Mendatang)...")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"}
    
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    
    # Kita cek tanggal hari ini dan kemarin (karena NBA main malam di USA, pagi di Indo)
    dates_to_check = [
        (now - timedelta(days=1)).strftime('%Y-%m-%d'), # Kemarin (Game yang sedang/baru selesai)
        now.strftime('%Y-%m-%d')                       # Hari ini (Game yang akan datang)
    ]

    all_games_msg = ""
    
    try:
        for date in dates_to_check:
            res = requests.get(url, headers=headers, params={"date": date}, timeout=15)
            games = res.json().get('response', [])
            
            if games:
                all_games_msg += f"📅 **Tanggal: {date}**\n"
                for g in games:
                    home, away = g['teams']['home']['name'], g['teams']['visitors']['name']
                    status = g['status']['long']
                    all_games_msg += f"🏟️ **{away} @ {home}**\n⏰ Status: {status}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                all_games_msg += "\n"

        if not all_games_msg:
            await status_msg.edit_text("📅 Tidak ada jadwal NBA ditemukan untuk 48 jam terakhir.")
        else:
            final_msg = "🏀 **JADWAL NBA TERBARU**\n\n" + all_games_msg
            await status_msg.edit_text(final_msg, parse_mode='Markdown')
            
    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error API NBA: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_football))
    app.add_handler(CommandHandler('nba', get_nba))
    
    print("✅ Bot NBA + Bola Siap!")
    app.run_polling(drop_pending_updates=True)
            
