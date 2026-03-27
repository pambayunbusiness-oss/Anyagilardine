import os
import requests
import datetime
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging untuk pantau di Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")

# Host untuk masing-masing cabang
NBA_HOST = "api-nba-v1.p.rapidapi.com"
FOOTBALL_HOST = "api-football-v1.p.rapidapi.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽🏀 *Bot NBA & Bola v1.0*\n\n"
        "Gunakan perintah:\n"
        "/jadwal - Cek NBA hari ini\n"
        "/bola - Cek Liga Top Eropa hari ini",
        parse_mode='Markdown'
    )

# --- FUNGSI JADWAL NBA ---
async def get_nba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_date = datetime.datetime.now().strftime('%Y-%m-%d')
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": NBA_HOST}
    params = {"date": target_date, "timezone": "Asia/Jakarta"}
    
    try:
        res = requests.get(f"https://{NBA_HOST}/games", headers=headers, params=params, timeout=10)
        data = res.json()
        games = data.get('response', [])
        
        if not games:
            return await update.message.reply_text(f"ℹ️ Tidak ada jadwal NBA untuk {target_date}.")

        pesan = f"🏀 *NBA {target_date}:*\n\n"
        for g in games[:10]:
            pesan += f"🔥 {g['teams']['visitors']['name']} vs {g['teams']['home']['name']}\n"
        await update.message.reply_text(pesan, parse_mode='Markdown')
    except:
        await update.message.reply_text("⚠️ Gagal mengambil data NBA.")

# --- FUNGSI JADWAL BOLA ---
async def get_bola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_date = datetime.datetime.now().strftime('%Y-%m-%d')
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": FOOTBALL_HOST}
    
    # ID Liga: 39 (EPL), 140 (La Liga), 135 (Serie A), 78 (Bundesliga)
    leagues = [39, 140, 135, 78] 
    
    await update.message.reply_text(f"⏳ Mencari jadwal Bola {target_date}...")
    
    pesan = f"⚽ *Jadwal Bola Top Eropa ({target_date}):*\n\n"
    found = False

    try:
        for league_id in leagues:
            # Musim 2025 sesuai tahun sekarang
            params = {"date": target_date, "league": league_id, "season": "2025"} 
            res = requests.get(f"https://{FOOTBALL_HOST}/fixtures", headers=headers, params=params, timeout=10)
            data = res.json()
            fixtures = data.get('response', [])
            
            if fixtures:
                found = True
                league_name = fixtures[0]['league']['name']
                pesan += f"🏆 *{league_name}*\n"
                for f in fixtures[:5]:
                    home = f['teams']['home']['name']
                    away = f['teams']['away']['name']
                    time = f['fixture']['date'][11:16] # Jam tanding
                    pesan += f"⏰ {time} - {home} vs {away}\n"
                pesan += "────────────────────\n"

        if not found:
            await update.message.reply_text("ℹ️ Tidak ada jadwal Liga Top Eropa hari ini.")
        else:
            await update.message.reply_text(pesan, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("⚠️ Gagal ambil data bola. Pastikan sudah klik SUBSCRIBE di API-Football!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('jadwal', get_nba))
    app.add_handler(CommandHandler('bola', get_bola))
    
    print("🚀 Bot NBA & BOLA Aktif!")
    app.run_polling(drop_pending_updates=True)
        
