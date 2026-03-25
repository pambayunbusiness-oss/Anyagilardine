import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- KONFIGURASI ---
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Daftar ID Liga yang sudah pasti benar (Database 2026)
FIXED_LEAGUES = {
    "premier": "94",
    "epl": "94",
    "laliga": "87",
    "seria": "55",
    "ucl": "42",
    "champions": "42",
    "bundesliga": "54"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Bot Jadwal Pertandingan Final**\n\n"
        "Gunakan perintah:\n"
        "• `/next premier` (EPL)\n"
        "• `/next laliga` (Spanyol)\n"
        "• `/next seria` (Italia)\n"
        "• `/next ucl` (Liga Champions)\n\n"
        "Atau liga
        
