import os
import logging
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-nba-v1.p.rapidapi.com" 

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏀 *Bot NBA Online!*\n\n"
        "Gunakan perintah berikut:\n"
        "/jadwal - Cek jadwal hari ini\n"
        "/besok - Cek jadwal besok\n"
        "/kemarin - Cek skor kemarin", 
        parse_mode='Markdown'
    )

async def fetch_nba_data(target_date):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    url = f"https://{API_HOST}/games"
    params = {"date": target_date}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        return response.json()
    except Exception as e:
        logging.error(f"API Error: {e}")
        return None

async def process_jadwal(update: Update, days_delta=0):
    # Menghitung tanggal berdasarkan delta (0=hari ini, 1=besok, -1=kemarin)
    date_obj = datetime.datetime.now() + datetime.timedelta(days=days_delta)
    str_date = date_obj.strftime('%Y-%m-%d')
    
    await update.message.reply_text(f"⏳ Mengambil data NBA untuk {str_date}...")
    
    data = await fetch_nba_data(str_date)
    
    if not data or not data.get('response'):
        await update.message.reply_text(
            f"ℹ️ Tidak ada jadwal ditemukan untuk {str_date}.\n\n"
            "Tips: NBA biasanya baru merilis jadwal fix beberapa jam sebelum pertandingan dimulai (Waktu US)."
        )
        return

    fixtures = data.get('response', [])
    pesan = f"🏀 *Jadwal/Skor NBA ({str_date}):*\n\n"
    
    for g in fixtures[:15]:
        try:
            away = g['teams']['visitors']['name']
            home = g['teams']['home']['name']
            status = g['status']['long']
            s_away = g['scores']['visitors']['points']
            s_home = g['scores']['home']['points']
            
            if "Scheduled" in status or "Not Started" in status:
                pesan += f"⏰ {away} vs {home}\n"
            else:
                pesan += f"🏀 {away} ({s_away}) - ({s_home}) {home}\n"
                pesan += f"💬 Status: {status}\n"
            
            pesan += "────────────────────\n"
        except:
            continue
            
    await update.message.reply_text(pesan, parse_mode='Markdown')

# Handler Perintah
async def jadwal_hari_ini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_jadwal(update, days_delta=0)

async def jadwal_besok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_jadwal(update, days_delta=1)

async def jadwal_kemarin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_jadwal(update, days_delta=-1)

if __name__ == '__main__':
    if not TOKEN or not API_KEY:
        print("❌ API_KEY atau TOKEN belum diisi di Railway!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # Tambahkan Handler
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('jadwal', jadwal_hari_ini))
        app.add_handler(CommandHandler('besok', jadwal_besok))
        app.add_handler(CommandHandler('kemarin', jadwal_kemarin))
        
        print("🚀 Bot NBA Final Version Aktif!")
        # drop_pending_updates=True untuk mencegah tabrakan bot (Conflict)
        app.run_polling(drop_pending_updates=True)
        
