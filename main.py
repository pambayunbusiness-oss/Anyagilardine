import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# KONFIGURASI
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Bot Jadwal Pertandingan**\n\n"
        "Ketik: `/next nama liga`\n"
        "Contoh: `/next premier league` atau `/next la liga`",
        parse_mode='Markdown'
    )

async def get_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Silakan masukkan nama liga. Contoh: `/next premier league`")
        return

    status_msg = await update.message.reply_text(f"🔍 Mencari data untuk {query}...")

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }

    try:
        # STEP 1: Cari ID Liga berdasarkan nama yang kamu ketik
        search_url = "https://free-api-live-football-data.p.rapidapi.com/football-get-search-all"
        search_res = requests.get(search_url, headers=headers, params={"search": query}, timeout=15)
        search_data = search_res.json()
        
        # Ambil ID liga pertama yang ditemukan
        leagues = search_data.get('response', {}).get('leagues', [])
        if not leagues:
            await status_msg.edit_text(f"❌ Liga '{query}' tidak ditemukan. Coba nama lain.")
            return
        
        league_id = leagues[0].get('id')
        league_name = leagues[0].get('name')

        # STEP 2: Ambil Jadwal berdasarkan ID Liga tersebut
        fixture_url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-league"
        fixture_res = requests.get(fixture_url, headers=headers, params={"leagueid": league_id}, timeout=15)
        fixture_data = fixture_res.json()
        
        # Ambil list pertandingan
        all_fixtures = fixture_data.get('response', {}).get('all_fixtures', [])
        
        if not all_fixtures:
            await status_msg.edit_text(f"📅 Tidak ada jadwal mendatang untuk {league_name}.")
            return

        msg = f"📅 **Jadwal Mendatang: {league_name}**\n"
        msg += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        # Filter pertandingan yang belum mulai (NS atau notstarted)
        count = 0
        for f in all_fixtures:
            # Kita ambil pertandingan yang statusnya bukan 'finished'
            status_type = f.get('status', {}).get('type', '').lower()
            if status_type != 'finished':
                home = f.get('home', {}).get('name')
                away = f.get('away', {}).get('name')
                date = f.get('status', {}).get('reason', 'TBA')
                
                msg += f"🏟️ **{home} vs {away}**\n⏰ {date}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                count += 1
            if count >= 8: break # Batasi 8 pertandingan agar tidak kena limit karakter Telegram

        await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("⚠️ Gagal mengambil data. Pastikan kuota RapidAPI masih ada.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_next_match))
    app.run_polling(drop_pending_updates=True)
    
