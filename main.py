import logging
import requests
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# KONFIGURASI
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Jadwal Bola Aktif.\nKetik /bola untuk lihat jadwal hari ini.")

async def get_bola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Mengambil jadwal pertandingan...")
    
    # Ambil tanggal hari ini format YYYYMMDD
    tz = pytz.timezone('Asia/Jakarta')
    today = datetime.now(tz).strftime('%Y%m%d')
    
    # Endpoint untuk JADWAL (Fixtures)
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-fixtures-by-date"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }
    params = {"date": today}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        data = res.json()
        
        # Mengambil list pertandingan
        fixtures = data.get('response', {}).get('fixtures', [])
        
        if not fixtures:
            await status_msg.edit_text(f"Tidak ada jadwal pertandingan untuk tanggal {today}.")
            return

        msg = f"📅 **Jadwal Bola Hari Ini ({today})**\n"
        msg += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        for f in fixtures[:15]:
            home = f.get('home', {}).get('name', 'Home')
            away = f.get('away', {}).get('name', 'Away')
            status = f.get('status', {}).get('type', 'TBA')
            time = f.get('status', {}).get('reason', '') # Biasanya berisi jam
            
            msg += f"🏟️ {home} vs {away}\n⏰ Status/Jam: {status} {time}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            
        await status_msg.edit_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("⚠️ Gagal mengambil jadwal. Cek koneksi API.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('bola', get_bola))
    app.run_polling(drop_pending_updates=True)
        
