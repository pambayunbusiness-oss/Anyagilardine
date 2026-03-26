import os
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Langsung ambil dari Environment (Tanpa Dotenv)
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-nba-v1.p.rapidapi.com"

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cek tanggal hari ini (WIB)
    target_date = datetime.datetime.now().strftime('%Y-%m-%d')
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
    params = {"date": target_date, "timezone": "Asia/Jakarta"}
    
    try:
        response = requests.get(f"https://{API_HOST}/games", headers=headers, params=params, timeout=10)
        data = response.json()
        fixtures = data.get('response', [])
        
        if not fixtures:
            await update.message.reply_text(f"ℹ️ Tidak ada jadwal untuk {target_date}.")
            return

        pesan = f"🏀 *NBA {target_date}:*\n\n"
        for g in fixtures[:10]:
            away = g['teams']['visitors']['name']
            home = g['teams']['home']['name']
            pesan += f"🔥 {away} vs {home}\n────────────────────\n"
        await update.message.reply_text(pesan, parse_mode='Markdown')
    except:
        await update.message.reply_text("⚠️ Gagal koneksi ke API.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('jadwal', get_jadwal))
    # drop_pending_updates=True WAJIB agar tidak Conflict
    app.run_polling(drop_pending_updates=True)
    
