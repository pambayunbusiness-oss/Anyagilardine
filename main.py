import os
import logging
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi API dari Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-football-v1.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bot Jadwal Bola Aktif!\n\n"
        "Gunakan perintah:\n"
        "⚽ /jadwal - Cek pertandingan LIVE & Jadwal hari ini"
    )

async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ambil tanggal hari ini (Waktu Indonesia)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        # STEP 1: Cek yang sedang LIVE
        res_live = requests.get(f"https://{API_HOST}/v3/fixtures", headers=headers, params={"live": "all"})
        data_live = res_live.json().get("response", [])

        # STEP 2: Ambil semua jadwal HARI INI
        res_today = requests.get(f"https://{API_HOST}/v3/fixtures", headers=headers, params={"date": today, "timezone": "Asia/Jakarta"})
        data_today = res_today.json().get("response", [])

        pesan = ""

        # Tampilkan yang LIVE dulu jika ada
        if data_live:
            pesan += "🔴 *SEDANG BERLANGSUNG (LIVE):*\n"
            for m in data_live[:5]:
                h, a = m['teams']['home']['name'], m['teams']['away']['name']
                gh, ga = m['goals']['home'], m['goals']['away']
                pesan += f"• {h} ({gh}) vs ({ga}) {a}\n"
            pesan += "\n"

        # Tampilkan jadwal hari ini
        if data_today:
            pesan += f"📅 *JADWAL HARI INI ({today}):*\n"
            # Filter yang belum mulai (NS = Not Started)
            upcoming = [m for m in data_today if m['fixture']['status']['short'] == "NS"]
            
            if not upcoming and not data_live:
                pesan = "ℹ️ Semua pertandingan hari ini sudah selesai."
            else:
                for m in upcoming[:10]:
                    jam = m['fixture']['date'][11:16] # Ambil jam HH:mm
                    h, a = m['teams']['home']['name'], m['teams']['away']['name']
                    pesan += f"⏰ {jam} WIB: {h} vs {a}\n"
        else:
            if not pesan: pesan = "ℹ️ Tidak ada jadwal pertandingan untuk hari ini."

        await update.message.reply_text(pesan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal mengambil data. Coba lagi nanti.")

if __name__ == '__main__':
    if not TOKEN:
        print("❌ Error: TOKEN Kosong!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', get_jadwal))
        print("✅ Bot Final Revision is Running...")
        app.run_polling()
                     
