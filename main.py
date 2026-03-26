import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# ID LIGA & SEASON (Biasanya season ID 2025/2026 atau terbaru)
# Jika ID ini salah, API akan mengembalikan data kosong.
LEAGUE_CONFIG = {
    "ucl": {"id": "42", "season": "2025"},
    "premier": {"id": "94", "season": "2025"},
    "laliga": {"id": "87", "season": "2025"},
    "seria": {"id": "55", "season": "2025"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Bot Jadwal Aktif. Ketik `/next ucl` atau `/next premier`.")

async def get_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next ucl`")
        return

    user_query = context.args[0].lower()
    config = LEAGUE_CONFIG.get(user_query)

    if not config:
        await update.message.reply_text(f"❌ Liga '{user_query}' tidak terdaftar.")
        return

    status_msg = await update.message.reply_text(f"⏳ Menarik seluruh kalender {user_query}...")

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }

    try:
        # Kita tembak All Fixtures dengan League ID
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-league"
        res = requests.get(url, headers=headers, params={"leagueid": config["id"]}, timeout=15)
        data = res.json()
        
        # Ambil list besar dari 'all_fixtures'
        fixtures = data.get('response', {}).get('all_fixtures', [])
        
        if not fixtures:
            await status_msg.edit_text(f"📅 Data API kosong untuk {user_query.upper()}.")
            return

        msg = f"📅 **Jadwal Mendatang: {user_query.upper()}**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        count = 0
        # Urutkan berdasarkan yang paling dekat dengan hari ini
        for f in fixtures:
            st_type = str(f.get('status', {}).get('type', '')).lower()
            
            # Ambil yang belum main
            if st_type not in ['finished', 'inprogress', 'canceled']:
                home = f.get('home', {}).get('name')
                away = f.get('away', {}).get('name')
                time_info = f.get('status', {}).get('reason') or f.get('status', {}).get('utcTime', 'TBA')
                
                # Kita filter manual, jika ada 'Apr 08' atau '08/04' di string waktu
                msg += f"🏟️ **{home} vs {away}**\n⏰ {time_info}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                count += 1
            
            if count >= 10: break

        if count == 0:
            await status_msg.edit_text(f"Semua pertandingan {user_query.upper()} sudah selesai di database.")
        else:
            await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception:
        await status_msg.edit_text("⚠️ Gagal mengambil data.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_next_match))
    app.run_polling(drop_pending_updates=True)
