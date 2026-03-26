import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging untuk pantau di Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "sports-information.p.rapidapi.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏀 Bot NBA Aktif! Ketik /jadwal")

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    
    # Kita pakai parameter dari screenshot kamu yang sukses (200 OK)
    params = {"year": "2024", "month": "02", "day": "06"}

    try:
        url = f"https://{API_HOST}/nba/schedule"
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Sesuai screenshot JSON kamu yang berhasil
        games = data.get('games', [])

        if not games:
            await update.message.reply_text("ℹ️ Data ditemukan tapi daftar pertandingan kosong.")
            return

        pesan = "🏀 *Jadwal NBA (Test):*\n\n"
        for g in games[:5]:
            name = g.get('name', 'NBA Game')
            pesan += f"🔥 {name}\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal mengambil data.")

if __name__ == '__main__':
    if not TOKEN:
        print("❌ TOKEN TIDAK DITEMUKAN!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        
        print("🚀 Bot sedang dinyalakan...")
        # drop_pending_updates=True untuk mencegah Conflict/Tabrakan
        app.run_polling(drop_pending_updates=True)
        
