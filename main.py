import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# KONFIGURASI
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Mapping ID Liga Terupdate untuk API "Free API Live Football Data"
LEAGUE_MAP = {
    "premier": "94",       # Premier League
    "laliga": "87",        # La Liga
    "seria": "55",         # Serie A
    "ucl": "42",           # UEFA Champions League
    "bundesliga": "54",     # Bundesliga
    "ligue1": "53"         # Ligue 1
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Bot Jadwal Pertandingan**\n\n"
        "Gunakan perintah:\n"
        "• `/next premier` (EPL)\n"
        "• `/next laliga` (Spanyol)\n"
        "• `/next seria` (Italia)\n"
        "• `/next ucl` (Champions League)\n\n"
        "Pastikan ketik sesuai daftar di atas ya!",
        parse_mode='Markdown'
    )

async def get_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next premier` atau `/next ucl`", parse_mode='Markdown')
        return

    # Ambil input user dan hilangkan spasi
    user_input = context.args[0].lower().replace(" ", "")
    league_id = LEAGUE_MAP.get(user_input)

    if not league_id:
        await update.message.reply_text(f"❌ Liga '{user_input}' belum terdaftar. Gunakan: premier, laliga, seria, atau ucl.")
        return

    status_msg = await update.message.reply_text(f"⏳ Mengambil jadwal mendatang...")

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }

    try:
        # Langsung tembak ke endpoint Fixtures berdasarkan ID
        fixture_url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-league"
        fixture_res = requests.get(fixture_url, headers=headers, params={"leagueid": league_id}, timeout=15)
        fixture_data = fixture_res.json()
        
        # Ambil list pertandingan
        all_fixtures = fixture_data.get('response', {}).get('all_fixtures', [])
        
        if not all_fixtures:
            await status_msg.edit_text(f"📅 Saat ini tidak ada jadwal mendatang untuk ID {league_id}.")
            return

        msg = f"📅 **Jadwal Mendatang: {user_input.upper()}**\n"
        msg += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        count = 0
        for f in all_fixtures:
            status_type = f.get('status', {}).get('type', '').lower()
            
            # Kita hanya ambil yang BELUM main (notstarted / NS / tba)
            if status_type not in ['finished', 'inprogress', 'canceled']:
                home = f.get('home', {}).get('name')
                away = f.get('away', {}).get('name')
                date = f.get('status', {}).get('reason', 'TBA')
                
                msg += f"🏟️ **{home} vs {away}**\n⏰ {date}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                count += 1
            
            if count >= 10: break

        if count == 0:
            await status_msg.edit_text("Semua pertandingan di matchday ini sudah selesai/sedang berlangsung.")
        else:
            await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("⚠️ Gagal mengambil data. Cek koneksi Railway atau limit API.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_next_match))
    app.run_polling(drop_pending_updates=True)
    
