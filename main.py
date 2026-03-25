import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
TOKEN = '8621903836:AAHePdX4K1KGTD9LENa_9pwxxlrOohRotWw'
RAPID_API_KEY = '129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Aktif.\n/bola\n/odds")

async def get_bola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-search-players"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }
    try:
        res = requests.get(url, headers=headers, params={"search": "mbappe"}, timeout=15)
        data = res.json()
        suggestions = data.get('response', {}).get('suggestions', [])
        
        if not suggestions:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        msg = ""
        for p in suggestions[:10]:
            msg += f"👤 {p.get('name')}\n🏟️ {p.get('teamName')}\n\n"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("Error API.")

async def get_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"
    params = {'apiKey': '635af92b5902de211d31a698e1ce2938', 'regions': 'us', 'markets': 'h2h'}
    try:
        res = requests.get(url, params=params, timeout=15)
        data = res.json()
        msg = ""
        for g in data[:5]:
            msg += f"🔥 {g['away_team']} @ {g['home_team']}\n"
            if g['bookmakers']:
                for o in g['bookmakers'][0]['markets'][0]['outcomes']:
                    msg += f"{o['name']}: {o['price']}\n"
            msg += "---\n"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("Error Odds.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('bola', get_bola))
    app.add_handler(CommandHandler('odds', get_odds))
    app.run_polling(drop_pending_updates=True)
    
