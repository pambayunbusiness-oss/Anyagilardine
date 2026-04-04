import os
import requests

# Ambil data dari GitHub Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

def get_schedule():
    url = "https://sports-information.p.rapidapi.com/soccer/schedule"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "sports-information.p.rapidapi.com"
    }
    params = {"year": "2026"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            pesan = "📅 *Jadwal Pertandingan Hari Ini*\n\n"
            for match in data[:10]:
                pesan += f"⚽ {match.get('name', 'N/A')}\n⏰ {match.get('date', 'N/A')}\n\n"
            return pesan
        return "Tidak ada jadwal pertandingan untuk hari ini."
    except Exception as e:
        return f"Gagal mengambil data API: {str(e)}"

def send_telegram(text):
    # Pastikan Token dan ID tidak kosong
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("ERROR: TELEGRAM_TOKEN atau CHAT_ID belum diisi di Secrets!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    
    # BAGIAN PENTING: Untuk melihat hasil di Log GitHub
    print(f"--- LAPORAN PENGIRIMAN ---")
    print(f"Status Code: {response.status_code}")
    print(f"Respon Telegram: {response.text}")
    print(f"--------------------------")

if __name__ == "__main__":
    print("Memulai bot...")
    jadwal_match = get_schedule()
    send_telegram(jadwal_match)
    
