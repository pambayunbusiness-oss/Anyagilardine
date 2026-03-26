import requests

# Masukkan API Key kamu di sini untuk tes
API_KEY = "129f979654msh783082d7f6eab02p197906jsn7e1a5e01ed89"
API_HOST = "api-football-v1.p.rapidapi.com"

url = "https://api-football-v1.p.rapidapi.com/v3/status"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

try:
    print("⏳ Sedang mengecek status API Key kamu...")
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    
    if response.status_code == 200:
        remaining = data['response']['requests']['remaining']
        limit = data['response']['requests']['limit_day']
        print("✅ API KEY AKTIF!")
        print(f"📊 Sisa Kuota Hari Ini: {remaining} dari {limit} request.")
    else:
        print(f"❌ API Error: {data.get('message', 'Terjadi kesalahan')}")
        
except Exception as e:
    print(f"⚠️ Gagal terhubung ke server: {e}")
