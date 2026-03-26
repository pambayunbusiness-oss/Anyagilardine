import logging
import requests
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI API ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

# Host API sesuai screenshot dashboard
HOST_NBA = "nba-api-free.p.rapidapi.com"
HOST_FOOTBALL = "api-football-v1.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Mapping Liga Football (Sudah Berjalan Lancar)
FOOTBALL_LEAGUES = {"ucl": 2, "premier": 39, "laliga": 140, "seriea": 135}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏀⚽ **Sports Bot Final Version**\n\n"
        "• `/nba` - Jadwal NBA (Fixed Endpoint)\n"
        "• `/next ucl` - Jadwal Champions League\n"
        "• `/next premier` - Jadwal Liga Inggris",
        parse_mode='Markdown'
    )

# --- 1. JADWAL NBA (REVISI TOTAL ENDPOINT) ---
async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Mengambil data NBA...")
    
    # Menggunakan endpoint 'Schedule' sesuai menu di dashboard RapidAPI
    url = f"https://{HOST_NBA}/nba-free-schedule" 
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": HOST_NBA
    }

    try:
        # Coba ambil data schedule umum
        res = requests.get(url, headers=headers, timeout=15)
        
        # Jika endpoint di atas 404, coba endpoint fallback /schedule
        if res.status_code == 404:
            res = requests.get(f"https://{HOST_NBA}/schedule", headers=headers, timeout=15)

        if res.status_code != 200:
            await status_msg.edit_text(f"❌ API Error {res.status_code}. Silakan cek tab 'Endpoints' di RapidAPI.")
            return

        data = res.json()
        
        # Menangani berbagai struktur JSON (body, results, atau list langsung)
        games = []
        if isinstance(data, list):
            games = data
        elif isinstance(data, dict):
            games = data.get('body', []) or data.get('results', []) or data.get('games', [])

        if not games:
            await status_msg.edit_text("📅 Jadwal NBA belum tersedia di server untuk saat ini.")
            return

        msg = "🏀 **NBA Schedule (Latest)**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        # Ambil 8 pertandingan terbaru
        for g in games[:8]:
            # Penyesuaian nama field dari API Creativesdev
            away = g.get('awayTeam') or g.get('away', 'Away')
            home = g.get('homeTeam') or g.get('home', 'Home')
            time = g.get('gameDate') or g.get('time', 'TBA')
            
            msg += f"🏟️ **{away} @ {home}**\n⏰ {time}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Terjadi kesalahan: {str(e)}")

# --- 2. JADWAL FOOTBALL (VERSI STABIL) ---
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next ucl` atau `/next premier`")
        return

    query = context.args[0].lower()
    league_id = FOOTBALL_LEAGUES.get(query)

    if not league_id:
        await update.message.reply_text("❌ Liga tidak dikenal.")
        return

    status_msg = await update.message.reply_text(f"⚽ Mencari jadwal {query.upper()}...")
    
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": HOST_FOOTBALL}
    params = {"league": league_id, "next": "8"}

    try:
        res = requests.get(f"https://{HOST_FOOTBALL}/v3/fixtures", headers=headers, params=params, timeout=15)
        fixtures = res.json().get('response', [])

        msg = f"⚽ **Jadwal {query.upper()} (WIB)**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for f in fixtures:
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            # Konversi UTC ke WIB
            utc_time = datetime.strptime(f['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
            wib_time = utc_time.astimezone(pytz.timezone('Asia/Jakarta')).strftime('%d %b, %H:%M')
            
            msg += f"🏟️ **{home} vs {away}**\n⏰ {wib_time} WIB\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal mengambil data Football.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('nba', get_nba))
    app.add_handler(CommandHandler('next', get_football))
    
    print("🚀 Bot Sports Terpadu Berjalan...")
    app.run_polling()
                         
