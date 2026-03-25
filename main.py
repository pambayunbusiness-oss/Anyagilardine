import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# KONFIGURASI
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Mapping ID Liga (Berdasarkan database Free API Live Football Data)
# Jika ID berubah, kamu bisa mencarinya via endpoint 'football-get-all-leagues'
LEAGUE_IDS = {
    "premier": "94",      # Premier League
    "laliga": "87",       # La Liga
    "seria": "55",        # Serie A
    "ucl": "42",          # UEFA Champions League
    "bundesliga": "54"    # tambahan
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Bot Jadwal Liga**\n\n"
        "Gunakan perintah:\n"
        "/next premier - Jadwal EPL\n"
        "/next laliga - Jadwal La Liga\n"
        "/next seria - Jadwal Serie A\n"
        "/next ucl - Jadwal Champions League",
        parse_mode='Markdown'
    )

async def get_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Silakan masukkan nama liga. Contoh: `/next premier`", parse_mode='Markdown')
        return

    league_input = context.args[0].lower()
    league_id = LEAGUE_IDS.get(league_input)

    if not league_id:
        await update.message.reply_text("Liga tidak terdaftar. Gunakan: premier, laliga, seria, atau ucl.")
        return

    status_msg = await update.message.reply_text(f"⏳ Mengambil jadwal mendatang {league_input}...")

    # Endpoint untuk mengambil jadwal liga spesifik
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-league"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }
    params = {"leagueid": league_id}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        data = res.json()
        
        # Mengambil list pertandingan mendatang (all_fixtures)
        fixtures = data.get('response', {}).get('all_fixtures', [])
        
        if not fixtures:
            await status_msg.edit_text("Tidak ada jadwal mendatang yang ditemukan untuk liga ini.")
            return

        msg = f"📅 **Jadwal Mendatang: {league_input.upper()}**\n"
        msg += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        # Ambil 10 pertandingan mendatang (yang statusnya belum dimulai/NS)
        count = 0
        for f in fixtures:
            status_type = f.get('status', {}).get('type', '')
            if status_type == 'notstarted' or status_type == 'NS':
                home = f.get('home', {}).get('name', 'Home')
                away = f.get('away', {}).get('name', 'Away')
                date_str = f.get('status', {}).get('reason', 'TBA') # Jam/Tanggal
                
                msg += f"🏟️ **{home} vs {away}**\n⏰ {date_str}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                count += 1
            
            if count >= 10: break # Batasi 10 jadwal saja agar tidak kepanjangan

        if count == 0:
            await status_msg.edit_text("Semua pertandingan di matchday ini sudah selesai.")
        else:
            await status_msg.edit_text(msg, parse_mode='Markdown')
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("⚠️ Gagal mengambil data. Cek limit API kamu.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_next_match)) # Menggunakan /next
    app.run_polling(drop_pending_updates=True)
    
