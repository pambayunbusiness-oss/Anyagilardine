import pandas as pd
import time
import random
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
from requests.exceptions import ReadTimeout, ConnectionError

# Daftar User-Agent agar tidak mudah terdeteksi sebagai satu bot yang sama
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
]

def get_nba_stats_with_retry(player_name, retries=3, backoff_factor=2):
    """
    Mengambil data statistik pemain dengan sistem auto-retry.
    """
    # Cari ID Pemain
    nba_players = players.find_players_by_full_name(player_name)
    if not nba_players:
        return f"Pemain '{player_name}' tidak ditemukan."
    
    player_id = nba_players[0]['id']
    
    for i in range(retries):
        try:
            # Setup header acak setiap kali mencoba
            headers = {
                'Host': 'stats.nba.com',
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://stats.nba.com/',
                'Connection': 'keep-alive',
            }

            print(f"Percobaan {i+1}: Mengambil data untuk {player_name}...")
            
            # Request ke NBA API
            career = playercareerstats.PlayerCareerStats(
                player_id=player_id, 
                headers=headers, 
                timeout=30
            )
            
            df = career.get_data_frames()[0]
            # Menampilkan 5 musim terakhir
            return df[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'REB', 'AST']].tail(5)

        except (ReadTimeout, ConnectionError) as e:
            wait_time = backoff_factor * (i + 1)
            print(f"Gagal koneksi. Mencoba lagi dalam {wait_time} detik... ({e})")
            time.sleep(wait_time)
            
    return "Gagal mengambil data setelah beberapa kali percobaan. Server NBA mungkin sedang sibuk."

if __name__ == "__main__":
    # Contoh penggunaan untuk Giannis Antetokounmpo
    # Kamu bisa menggantinya dengan nama pemain lain seperti Kyle Kuzma
    data_stats = get_nba_stats_with_retry("Giannis Antetokounmpo")
    
    print("\n--- Hasil Statistik ---")
    print(data_stats)
            
