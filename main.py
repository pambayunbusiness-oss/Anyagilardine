import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# ID LIGA TETAP (Agar tidak perlu mencari lagi)
LEAGUE_IDS = {
    "premier": "94",
    "laliga": "87",
    "seria": "55",
    "ucl": "42",
    "bundesliga": "54"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Bot Jadwal Pertandingan**\n\n"
        "Ketik perintah berikut:\n"
        "• `/next premier`\n"
        "• `/next laliga`\n"
        "• `/next seria`\n"
        "• `/next ucl`",
        parse_mode='Markdown'
    )

async def get_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next premier` atau `/next ucl`")
        return

    # Ambil kata pertama yang diketik user
    user_query = context.args[0].lower()
    league_id = LEAGUE_IDS.get(user_query)

    if not league_id:
        await update.message.reply_text(f"❌ Liga '{user_query}' tidak terdaftar. Gunakan: premier, laliga, seria, atau ucl.")
        return

    status_msg = await update.message.reply_text(f"⏳ Mengambil jadwal {user_query}...")

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }

    try:
        # Langsung ambil jadwal pakai ID yang sudah kita simpan
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-league"
        res = requests.get(url, headers=headers, params={"leagueid": league_id}, timeout=15)
        data = res.json()
        
        fixtures = data.get('response', {}).get('all_fixtures', [])
        
        if not fixtures:
            await status_msg.edit_text(f"📅 Belum ada jadwal mendatang untuk {user_query.upper()}.")
            return

        msg = f"📅 **Jadwal Mendatang: {user_query.upper()}**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        count = 0
        for f in fixtures:
            # Filter yang belum mulai
            st_type = f.get('status', {}).get('type', '').lower()
            if st_type not in ['finished', 'inprogress', 'canceled']:
                home = f.get('home', {}).get('name')
                away = f.get('away', {}).get('name')
                time = f.get('status', {}).get('reason') or f.get('status', {}).get('utcTime', 'TBA')
                
                msg += f"🏟️ **{home} vs {away}**\n⏰ {time}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                count += 1
            if count >= 8: break

        if count == 0:
            await status_msg.edit_text(f"Semua pertandingan {user_query.upper()} sudah selesai.")
        else:
            await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        await status_msg.edit_text("⚠️ Gagal mengambil data. Cek kuota API kamu.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_next_match))
    app.run_polling(drop_pending_updates=True)
    
