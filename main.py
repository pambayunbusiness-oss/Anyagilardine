import logging
import requests
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'
HOST_NBA = "nba-api-free.p.rapidapi.com"
HOST_FOOTBALL = "api-football-v1.p.rapidapi.com"

logging.basicConfig(level=logging.INFO)

async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Menghubungkan ke server NBA...")
    
    # Endpoint utama dari dashboard kamu
    url = f"https://{HOST_NBA}/nba-free-schedule" 
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": HOST_NBA}

    try:
        res = requests.get(url, headers=headers, timeout=15)
        
        # Jika alamat pertama 404, otomatis coba alamat kedua
        if res.status_code == 404:
            res = requests.get(f"https://{HOST_NBA}/schedule", headers=headers, timeout=15)

        if res.status_code != 200:
            await status_msg.edit_text(f"❌ Server sibuk (Error {res.status_code}). Coba lagi nanti.")
            return

        data = res.json()
        # KRUSIAL: API Creativesdev menyimpan data di dalam 'body'
        games = data.get('body', []) if isinstance(data, dict) else data

        if not games:
            await status_msg.edit_text("📅 Belum ada jadwal pertandingan yang dirilis hari ini.")
            return

        msg = "🏀 **NBA Schedule Update**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for g in games[:8]:
            # Mengambil data tim dari dalam objek game
            away = g.get('awayTeam', 'Away')
            home = g.get('homeTeam', 'Home')
            time = g.get('gameDate', 'TBA')
            msg += f"🏟️ **{away} @ {home}**\n⏰ {time}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal memproses data. Pastikan koneksi aman.")

# Fungsi Football tetap sama karena sudah terbukti jalan di botmu
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (Gunakan kode football yang sudah jalan sebelumnya) ...
    pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('nba', get_nba))
    # Tambahkan handler lainnya
    app.run_polling()
        
