import logging
import requests
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI API ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

# Host API
HOST_SPORTS_INFO = "sports-information.p.rapidapi.com"
HOST_FOOTBALL = "api-football-v1.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Mapping ID Liga untuk Football (API-Football)
FOOTBALL_LEAGUES = {
    "ucl": 2,
    "premier": 39,
    "laliga": 140,
    "seriea": 135,
    "bundesliga": 78
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏀⚽ **Sports Schedule Bot**\n\n"
        "**Perintah NBA:**\n"
        "• `/nba` - Jadwal NBA hari ini\n\n"
        "**Perintah Football:**\n"
        "• `/next ucl` - Jadwal Champions League\n"
        "• `/next premier` - Jadwal Liga Inggris\n"
        "• `/next laliga` - Jadwal Liga Spanyol",
        parse_mode='Markdown'
    )

# --- 1. FUNGSI JADWAL NBA (Sports Information API) ---
async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Mengambil jadwal NBA...")
    
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    
    # Endpoint & Params sesuai snippet berbayarmu
    url = f"https://{HOST_SPORTS_INFO}/nba/schedule"
    params = {
        "year": now.strftime("%Y"),
        "month": now.strftime("%m"),
        "day": now.strftime("%d")
    }
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": HOST_SPORTS_INFO
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        data = res.json()

        if not data or len(data) == 0:
            await status_msg.edit_text(f"📅 Tidak ada pertandingan NBA untuk hari ini ({now.strftime('%d %b')}).")
            return

        msg = f"🏀 **NBA Schedule ({now.strftime('%d %b %Y')})**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for g in data[:10]:
            name = g.get('name', 'NBA Game')
            # Ambil status (Live/Scheduled/Finished)
            status = g.get('status', {}).get('type', {}).get('description', 'Scheduled')
            msg += f"🏟️ **{name}**\n⏰ Status: {status}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal terhubung ke API NBA.")

# --- 2. FUNGSI JADWAL FOOTBALL (API-Football) ---
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: `/next ucl` atau `/next premier`")
        return
    
    league_name = context.args[0].lower()
    league_id = FOOTBALL_LEAGUES.get(league_name)

    if not league_id:
        await update.message.reply_text("❌ Liga tidak dikenal. Gunakan: ucl, premier, laliga, seriea.")
        return

    status_msg = await update.message.reply_text(f"⚽ Mencari jadwal {league_name.upper()}...")
    
    url = f"https://{HOST_FOOTBALL}/v3/fixtures"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": HOST_FOOTBALL
    }
    params = {"league": league_id, "next": "8"}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        fixtures = res.json().get('response', [])

        msg = f"⚽ **Jadwal {league_name.upper()} (WIB)**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for f in fixtures:
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            # Konversi waktu ke WIB
            date_utc = datetime.strptime(f['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
            date_wib = date_utc.astimezone(pytz.timezone('Asia/Jakarta')).strftime('%d %b, %H:%M')
            
            msg += f"🏟️ **{home} vs {away}**\n⏰ {date_wib} WIB\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal terhubung ke API Football.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('nba', get_nba))
    app.add_handler(CommandHandler('next', get_football))
    
    print("✅ Bot NBA & Football Berjalan...")
    app.run_polling()
                
