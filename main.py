import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Bot Jadwal Pertandingan**\n\n"
        "Cara pakai: `/next [nama liga]`\n"
        "Contoh:\n"
        "• `/next premier league`\n"
        "• `/next laliga`\n"
        "• `/next serie a`\n"
        "• `/next champions league`",
        parse_mode='Markdown'
    )

async def get_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Silakan masukkan nama liga. Contoh: `/next premier league`", parse_mode='Markdown')
        return

    status_msg = await update.message.reply_text(f"⏳ Mencari jadwal terbaru untuk {query}...")

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }

    try:
        # STEP 1: Cari ID Liga secara otomatis berdasarkan ketikan kamu
        search_res = requests.get(
            "https://free-api-live-football-data.p.rapidapi.com/football-get-search-all",
            headers=headers,
            params={"search": query},
            timeout=15
        )
        search_data = search_res.json()
        leagues = search_data.get('response', {}).get('leagues', [])

        if not leagues:
            await status_msg.edit_text(f"❌ Liga '{query}' tidak ditemukan. Coba ketik nama lengkapnya.")
            return

        league_id = leagues[0].get('id')
        league_name = leagues[0].get('name')

        # STEP 2: Ambil semua jadwal berdasarkan ID yang baru saja ditemukan
        fixture_res = requests.get(
            "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-league",
            headers=headers,
            params={"leagueid": league_id},
            timeout=15
        )
        fixture_data = fixture_res.json()
        
        # Coba ambil dari all_fixtures atau fixtures
        all_fixtures = fixture_data.get('response', {}).get('all_fixtures') or fixture_data.get('response', {}).get('fixtures') or []
        
        if not all_fixtures:
            await status_msg.edit_text(f"📅 Saat ini belum ada jadwal pertandingan mendatang untuk {league_name}.")
            return

        msg = f"📅 **Jadwal Mendatang: {league_name}**\n"
        msg += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        count = 0
        for f in all_fixtures:
            status_type = f.get('status', {}).get('type', '').lower()
            
            # Tampilkan yang belum mulai (notstarted / NS / tba)
            if status_type not in ['finished', 'inprogress', 'canceled']:
                home = f.get('home', {}).get('name', 'TBA')
                away = f.get('away', {}).get('name', 'TBA')
                # Ambil jam/tanggal dari reason atau utcTime
                date = f.get('status', {}).get('reason') or f.get('status', {}).get('utcTime', 'TBA')
                
                msg += f"🏟️ **{home} vs {away}**\n⏰ {date}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                count += 1
            
            if count >= 8: break # Batasi 8 biar pas di layar HP

        if count == 0:
            await status_msg.edit_text(f"Semua pertandingan di matchday {league_name} sudah selesai.")
        else:
            await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("⚠️ Gagal mengambil data. Pastikan kuota RapidAPI masih ada.")

if __name__ == '__main__':
    # drop_pending_updates=True untuk membersihkan sisa error "Conflict"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_next_match))
    
    print("✅ Bot Aktif...")
    app.run_polling(drop_pending_updates=True)
    
