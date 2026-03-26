import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "sports-information.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Bot Jadwal Bola Aktif! Ketik /jadwal")

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        # KITA PAKAI ENDPOINT PALING AMAN: 50 Pertandingan Terdekat (Live/Mendatang)
        url = f"https://{API_HOST}/v3/fixtures"
        # Kita ambil 15 pertandingan terdekat secara umum tanpa filter tanggal kaku
        params = {"next": "15", "timezone": "Asia/Jakarta"}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        fixtures = data.get("response", [])
        
        if not fixtures:
            await update.message.reply_text("ℹ️ Sedang tidak ada jadwal pertandingan di database.")
            return

        pesan = "🏆 *Jadwal Pertandingan Terdekat:* \n\n"
        
        for m in fixtures:
            home = m['teams']['home']['name']
            away = m['teams']['away']['name']
            liga = m['league']['name']
            waktu = m['fixture']['date'][11:16] # Jam:Menit
            status = m['fixture']['status']['short']
            
            # Jika sedang LIVE
            if status in ["1H", "2H", "HT"]:
                score_h = m['goals']['home']
                score_a = m['goals']['away']
                pesan += f"🔴 *LIVE* | {home} ({score_h}) vs ({score_a}) {away}\n"
            # Jika belum mulai
            else:
                pesan += f"⏰ {waktu} WIB | {home} vs {away}\n"
            
            pesan += f"   _{liga}_\n---\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Terjadi gangguan koneksi ke server API.")

if __name__ == '__main__':
    if not TOKEN:
        print("❌ Error: TOKEN Kosong!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        print("✅ Bot Terkoneksi!")
        app.run_polling()
        
