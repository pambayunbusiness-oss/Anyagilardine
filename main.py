import os
import logging
import requests
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Konfigurasi Dasar
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "api-nba-v1.p.rapidapi.com" 

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏀 *Bot NBA Final Version*\n\n"
        "Gunakan perintah:\n"
        "/jadwal - Cek pertandingan hari ini\n"
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
    
    # Menambahkan timezone Asia/Jakarta agar tanggal sinkron dengan WIB
    params = {
        "date": target_date,
        "timezone": "Asia/Jakarta"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        return response.json()
    except Exception as e:
        logging.error(f"API Error: {e}")
        return None

async def process_jadwal(update: Update, days_delta=0):
    # Menghitung tanggal (WIB)
    date_obj = datetime.datetime.now() + datetime.timedelta(days=days_delta)
    str_date = date_obj.strftime('%Y-%m-%d')
    
    await update.message.reply_text(f"⏳ Mencari data NBA untuk
    
