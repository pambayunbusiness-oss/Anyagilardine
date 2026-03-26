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

# ID LIGA (API-Football & API-NBA)
FOOTBALL_LEAGUES = {
    "ucl": 2,
    "premier": 39,
    "laliga": 140,
    "seria": 135
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽🏀 **Bot Jadwal Sports Aktif!**\n\n"
        "**Sepak Bola:**\n"
        "• `/next ucl` - Jadwal Champions League (8 Apr dll)\n"
        "• `/next premier` - Jadwal Liga Inggris\n\n"
        "**Basket NBA:**\n"
        "• `/nba` - Jadwal NBA Hari Ini (WIB)\n"
        "• `/nba_besok` - Jadwal NBA Besok",
        parse_mode='Markdown'
    )

# --- FUNGSI SEPAK BOLA (API-FOOTBALL) ---
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next ucl` atau `/next premier`")
        return

    query = context.args[0].lower()
    league_id = FOOTBALL_LEAGUES.get(query)

    if not league_id:
        await update.message.reply_text("❌ Liga tidak terdaftar. Gunakan: ucl, premier, laliga, seria.")
        return

    status_msg = await update.message.reply_text(f"⏳ Mengambil jadwal resmi {query.upper()}...")
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "api-football-v1.p.rapidapi.com"}
    params = {"league": league_id, "next": "10"}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        fixtures = res.json().get('response', [])

        if not fixtures:
            await status_msg.edit_text("📅 Tidak ada jadwal mendatang di database.")
            return

        msg = f"📅 **Jadwal Mendatang: {query.upper()}**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for f in fixtures:
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            # Konversi ke WIB
            utc_time = datetime.strptime(f['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
            wib_time = utc_time.astimezone(pytz.timezone('Asia/Jakarta')).strftime('%d %b, %H:%M WIB')
            
            msg += f"🏟️ **{home} vs {away}**\n⏰ {wib_time}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal mengambil data bola. Cek koneksi/API Key.")

# --- FUNGSI NBA (API-NBA) ---
async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tentukan tanggal (Hari ini atau Besok)
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    
    if 'besok' in update.message.text:
        target_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        target_date = now.strftime('%Y-%m-%d')

    status_msg = await update.message.reply_text(f"🏀 Mencari jadwal NBA ({target_date})...")
    url = "https://api-nba-v1.p.rapidapi.com/games"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"}
    params = {"date": target_date}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        games = res.json().get('response', [])

        if not games:
            await status_msg.edit_text(f"📅 Tidak ada game NBA untuk tanggal {target_date}.")
            return

        msg = f"🏀 **Jadwal NBA: {target_date}**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for g in games:
            home = g['teams']['home']['name']
            away = g['teams']['visitors']['name']
            arena = g['arena']['name']
            # Status pertandingan (Scheduled / Live / Finished)
            st = g['status']['long']
            
            msg += f"🏟️ **{away} @ {home}**\n📍 {arena}\n⏰ Status: {st}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal mengambil data NBA. Pastikan sudah Subscribe API-NBA.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_football))
    app.add_handler(CommandHandler('nba', get_nba))
    app.add_handler(CommandHandler('nba_besok', get_nba))
    
    print("✅ Bot Aktif (Bola + NBA)...")
    app.run_polling(drop_pending_updates=True)
            
