import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "sports-information.p.rapidapi.com"

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
    
    # Kita pakai parameter dari screenshot kamu yang sukses (200 OK)
    params = {"year": "2024", "month": "02", "day": "06"}

    try:
        url = f"https://{API_HOST}/nba/schedule"
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Di screenshot kamu, datanya ada di dalam 'games'
        games = data.get('games', [])

        if not games:
            await update.message.reply_text("ℹ️ Data ditemukan tapi daftar pertandingan kosong.")
            return

        pesan = "🏀 *Jadwal NBA (Data Terdeteksi):*\n\n"
        for g in games[:5]:
            name = g.get('name', 'NBA Game')
            pesan += f"🔥 {name}\n────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text("⚠️ Bot masih mengalami kendala sinkronisasi API.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('jadwal', get_jadwal))
    app.run_polling()
            
