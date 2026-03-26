import logging
import requests
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

FOOTBALL_LEAGUES = {"ucl": 2, "premier": 39, "laliga": 140, "seria": 135}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽🏀 **Bot Sports Super Update**\n\n"
        "• `/next ucl` - Jadwal Bola (WIB)\n"
        "• `/nba` - Jadwal NBA (Creativesdev)\n"
        "• `/news` - Berita Basket Terbaru (ESPN)",
        parse_mode='Markdown'
    )

# --- 1. JADWAL SEPAK BOLA (API-FOOTBALL) ---
async def get_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: `/next ucl`")
        return
    
    query = context.args[0].lower()
    league_id = FOOTBALL_LEAGUES.get(query)
    if not league_id:
        await update.message.reply_text("❌ Liga tidak ada.")
        return

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "api-football-v1.p.rapidapi.com"}
    
    try:
        res = requests.get(url, headers=headers, params={"league": league_id, "next": "8"}, timeout=10)
        fixtures = res.json().get('response', [])
        
        msg = f"📅 **Jadwal {query.upper()}**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for f in fixtures:
            home, away = f['teams']['home']['name'], f['teams']['away']['name']
            utc_time = datetime.strptime(f['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
            wib_time = utc_time.astimezone(pytz.timezone('Asia/Jakarta')).strftime('%d %b, %H:%M WIB')
            msg += f"🏟️ **{home} vs {away}**\n⏰ {wib_time}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except:
        await update.message.reply_text("⚠️ Gagal akses API Bola.")

# --- 2. JADWAL NBA (NBA API FREE - CREATIVESDEV) ---
async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Menggunakan host dari screenshot: nba-api-free.p.rapidapi.com
    url = "https://nba-api-free.p.rapidapi.com/nba-free-schedule"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "nba-api-free.p.rapidapi.com"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        games = data if isinstance(data, list) else data.get('results', [])

        if not games:
            await update.message.reply_text("📅 Jadwal NBA belum diupdate di server.")
            return

        msg = "🏀 **NBA SCHEDULE (CREATIVESDEV)**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for g in games[:10]:
            # Menyesuaikan field dari API Free Data
            date = g.get('gameDate', 'TBA')
            home = g.get('homeTeam', 'Home')
            away = g.get('awayTeam', 'Away')
            msg += f"🏟️ **{away} @ {home}**\n📅 {date}\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except:
        await update.message.reply_text("⚠️ Gagal akses NBA API. Pastikan sudah Subscribe.")

# --- 3. BERITA BASKET (ESPN NEWS - DATA TERBARU) ---
async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ini menggunakan endpoint ESPN News (berdasarkan data JSON yang kamu kirim)
    url = "https://espn-api-data.p.rapidapi.com/news" # Pastikan host ini benar di RapidAPI-mu
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "espn-api-data.p.rapidapi.com"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        news_data = res.json()

        msg = "📰 **LATEST BASKETBALL NEWS**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for item in news_data[:5]:
            headline = item.get('headline', 'No Title')
            link = item.get('link', '')
            msg += f"🔥 **{headline}**\n🔗 [Klik Berita]({link})\n⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)
    except:
        await update.message.reply_text("⚠️ Gagal mengambil berita.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next', get_football))
    app.add_handler(CommandHandler('nba', get_nba))
    app.add_handler(CommandHandler('news', get_news))
    
    print("✅ Bot Berjalan dengan API Berbayar...")
    app.run_polling()
        
