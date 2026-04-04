import os
import requests

# Ambil token dari Environment Variables (GitHub Secrets)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

def get_schedule():
    url = "https://sports-information.p.rapidapi.com/soccer/schedule"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "sports-information.p.rapidapi.com"
    }
    params = {"year": "2026"} # Tahun saat ini
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Sederhanakan data untuk dikirim ke Telegram
        if isinstance(data, list) and len(data) > 0:
            pesan = "📅 *Jadwal Pertandingan Hari Ini (2026)*\n\n"
            for match in data[:10]: # Ambil 10 pertandingan
                pesan += f"⚽ {match.get('name', 'N/A')}\n⏰ {match.get('date', 'N/A')}\n\n"
            return pesan
        return "Tidak ada jadwal untuk hari ini."
    except:
        return "Gagal mengambil jadwal dari API."

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    jadwal = get_schedule()
    send_telegram(jadwal)
