import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ganti dengan API Key milikmu
RAPID_API_KEY = "YOUR_RAPIDAPI_KEY"
URL = "https://sports-information.p.rapidapi.com/schedule" # Sesuaikan dengan endpoint API-mu

async def get_football_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "sports-information.p.rapidapi.com"
    }
    
    today = datetime.now()
    schedule_message = "<b>Jadwal Pertandingan 1 Minggu Kedepan:</b>\n\n"
    
    # Loop untuk 7 hari ke depan
    for i in range(7):
        current_date = today + timedelta(days=i)
        formatted_date = current_date.strftime('%Y-%m-%d')
        
        # Contoh param (sesuaikan dengan dokumentasi API 'Sports Information' yang kamu pakai)
        params = {
            "year": current_date.year,
            "month": current_date.month,
            "day": current_date.day
        }
        
        try:
            response = requests.get(URL, headers=headers, params=params)
            data = response.json()
            
            # Logika parsing data (disesuaikan dengan struktur JSON API-mu)
            if data and "matches" in data: # Ini hanya contoh, cek struktur JSON asli
                schedule_message += f"📅 <b>{formatted_date}</b>\n"
                for match in data["matches"]:
                    schedule_message += f"⚽ {match['homeTeam']} vs {match['awayTeam']}\n"
                schedule_message += "\n"
        except Exception as e:
            print(f"Error pada tanggal {formatted_date}: {e}")

    if schedule_message == "<b>Jadwal Pertandingan 1 Minggu Kedepan:</b>\n\n":
        schedule_message = "Maaf, tidak ditemukan jadwal pertandingan untuk minggu ini."

    await update.message.reply_text(schedule_message, parse_mode='HTML')

if __name__ == '__main__':
    application = ApplicationBuilder().token('YOUR_TELEGRAM_BOT_TOKEN').build()
    
    # Perintah diganti dari /start menjadi /football
    football_handler = CommandHandler('football', get_football_schedule)
    application.add_handler(football_handler)
    
    application.run_polling()
    
