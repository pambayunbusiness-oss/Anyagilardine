import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# ID LIGA TETAP
LEAGUE_IDS = {
    "premier": "94",
    "laliga": "87",
    "seria": "55",
    "ucl": "42",
    "bundesliga": "54"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Bot Aktif. Ketik `/next ucl` atau `/next premier`.")

async def get_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next ucl`")
        return

    user_query = context.args[0].lower()
    league_id = LEAGUE_IDS.get(user_query)

    if not league_id:
        await update.message.reply_text(f"❌ Liga '{user_query}' tidak terdaftar.")
        return

    status_msg = await update.message.reply_text(f"⏳ Mencari jadwal lengkap {user_query}...")

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }

    try:
        # Gunakan endpoint all-fixtures
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-league"
        res = requests.get(url, headers=headers, params={"leagueid": league_id}, timeout=15)
        data = res.json()
        
        # API ini sering menaruh data di 'all_fixtures'
        fixtures = data.get('response', {}).get('all_fixtures', [])
        
        if not fixtures:
            await status_msg.edit_text(f"📅 API belum merilis jadwal mendatang untuk {user_query.upper()}.")
            return

        msg = f"📅 **Jadwal Mendatang: {user_query.upper()}**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        count = 0
        for f in fixtures:
            # Kita ambil yang statusnya belum mulai (NS / notstarted / scheduled)
            st_type = str(f.get('status', {}).get('type', '')).lower()
            
            if st_type not in ['finished', 'inprogress', 'canceled']:
                home = f.get('home', {}).get('name', 'TBA')
                away = f.get('away', {}).get('name', 'TBA')
                # Ambil keterangan waktu/tanggal
                time_info = f.get('status', {}).get('reason') or f.get('status', {}).get('utcTime', 'TBA')
                
                msg += f"🏟️ **{home} vs {away}**\n⏰ {time_info}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                count += 1
            
            # Ambil maksimal 10 jadwal agar tidak kepanjangan
            if count >= 10: break

        if count == 0:
            await status_msg.edit_text(f"Belum ada jadwal pertandingan baru yang masuk di database API.")
        else:
            await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        await status_msg.edit_text("⚠️ Gagal mengambil data. Cek kuota RapidAPI.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_next_match))
    app.run_polling(drop_pending_updates=True)
    
