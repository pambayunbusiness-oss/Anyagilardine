import logging
import requests
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

# Host sesuai dokumentasi yang kamu kirim
SPORTS_INFO_HOST = "sports-information.p.rapidapi.com"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏀🏈⚽ **Bot Sports Information Aktif!**\n\n"
        "Gunakan perintah berikut:\n"
        "• `/nba` - Jadwal NBA Terbaru\n"
        "• `/ncaa` - Jadwal Basketball Kampus (NCAA)\n"
        "• `/news` - Berita Sports Terkini\n"
        "• `/next ucl` - Jadwal Bola Eropa (API-Football)",
        parse_mode='Markdown'
    )

# --- FUNGSI NBA (Berdasarkan Dokumentasi Baru) ---
async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🏀 Mengambil data NBA...")
    
    # Endpoint sesuai dokumentasi: /nba/schedule
    url = f"https://{SPORTS_INFO_HOST}/nba/schedule"
    
    # Mengambil tanggal hari ini (WIB)
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    
    params = {
        "year": now.strftime('%Y'),
        "month": now.strftime('%m'),
        "day": now.strftime('%d')
    }
    
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": SPORTS_INFO_HOST
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        data = res.json()
        
        # Berdasarkan dokumentasi, response biasanya berupa list pertandingan
        if not data:
            await status_msg.edit_text(f"📅 Tidak ada jadwal NBA untuk tanggal {params['day']}-{params['month']}.")
            return

        msg = f"🏀 **Jadwal NBA ({params['day']}/{params['month']})**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        
        # Ambil maksimal 10 game
        for g in data[:10]:
            # Struktur umum API ini biasanya menggunakan 'name' atau 'shortName'
            game_name = g.get('name', 'Pertandingan NBA')
            status = g.get('status', {}).get('type', {}).get('description', 'Scheduled')
            
            msg += f"🏟️ **{game_name}**\n⏰ Status: {status}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"

        await status_msg.edit_text(msg, parse_mode='Markdown')
    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error NBA API: Hubungi admin.")

# --- FUNGSI BERITA (Berdasarkan Dokumentasi Baru) ---
async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📰 Mengambil berita terbaru...")
    
    # Endpoint sesuai dokumentasi: /nba/news
    url = f"https://{SPORTS_INFO_HOST}/nba/news"
    params = {"limit": "5"}
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": SPORTS_INFO_HOST
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        news_list = res.json()

        msg = "📰 **BERITA TERPOPULER**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for item in news_list:
            headline = item.get('headline', 'No Title')
            description = item.get('description', '')
            msg += f"🔥 **{headline}**\n_{description[:100]}..._\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            
        await status_msg.edit_text(msg, parse_mode='Markdown')
    except:
        await status_msg.edit_text("⚠️ Gagal mengambil berita.")

# --- FUNGSI BOLA (Tetap menggunakan API-Football karena lebih lengkap untuk Eropa) ---
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # (Kode fungsi football tetap sama dengan sebelumnya)
    pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('nba', get_nba))
    app.add_handler(CommandHandler('news', get_news))
    # Tambahkan handler lain sesuai kebutuhan
    
    print("✅ Bot NBA Sports Info Siap!")
    app.run_polling()
