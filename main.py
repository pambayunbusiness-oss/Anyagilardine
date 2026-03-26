import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Mengambil API Key dari Railway (Environment Variables)
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
# Host API (Contoh: API-Football dari RapidAPI)
API_HOST = "api-football-v1.p.rapidapi.com"

# 2. Setup Logging agar kita bisa cek error di tab "Logs" Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 3. Fungsi Perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Bot Jadwal Olahraga sudah online.\n\n"
        "Gunakan perintah berikut:\n"
        "⚽ /jadwal - Untuk melihat pertandingan live hari ini"
    )

# 4. Fungsi Perintah /jadwal
async def get_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://{API_HOST}/v3/fixtures"
    querystring = {"live": "all"} # Menampilkan pertandingan yang sedang berlangsung
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        fixtures = data.get("response", [])
        
        if not fixtures:
            await update.message.reply_text("ℹ️ Saat ini tidak ada pertandingan yang sedang berlangsung.")
            return

        pesan = "🏆 *Pertandingan Sedang Berlangsung:* \n\n"
        # Ambil maksimal 10 pertandingan agar tidak kepanjangan
        for match in fixtures[:10]:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            score_h = match['goals']['home']
            score_a = match['goals']['away']
            liga = match['league']['name']
            
            pesan += f"📌 *{liga}*\n"
            pesan += f"🏠 {home} ({score_h}) vs ({score_a}) {away} 🚩\n"
            pesan += "────────────────────\n"
            
        await update.message.reply_text(pesan, parse_mode='Markdown')
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Gagal mengambil data. Pastikan API Key Anda benar.")

# 5. Menjalankan Bot
if __name__ == '__main__':
    if not TOKEN:
        print("❌ ERROR: TELEGRAM_TOKEN tidak ditemukan di Variables Railway!")
    else:
        # Membangun aplikasi bot
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Menambahkan handler perintah
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('jadwal', get_jadwal))
        
        print("✅ Bot sedang berjalan di Railway...")
        application.run_polling()
            
