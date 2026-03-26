import os
import requests
import logging
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Setup Logging agar muncul di Dashboard Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Configuration (RapidAPI)
API_KEY = "129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89"
API_HOST = "api-football-v1.p.rapidapi.com"

def get_football_data():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    # Mengambil tanggal hari ini dalam format YYYY-MM-DD
    tz_jkt = pytz.timezone('Asia/Jakarta')
    today = datetime.now(tz_jkt).strftime('%Y-%m-%d')
    
    # Query: Mengambil jadwal hari ini untuk zona waktu Jakarta
    querystring = {"date": today, "timezone": "Asia/Jakarta"}
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    try:
        logging.info(f"Meminta data sepak bola untuk tanggal: {today}")
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        
        if not data.get('response'):
            return f"📅 *Jadwal Bola ({today})*\n\nBelum ada jadwal pertandingan besar yang tersedia jam sekarang."

        res = f"⚽ *Jadwal & Skor Bola ({today})*\n"
        res += "------------------------------------------\n\n"
        
        # Ambil 15 pertandingan teratas
        for match in data['response'][:15]:
            league = match['league']['name']
            home = match['teams']['home']['name']
            
