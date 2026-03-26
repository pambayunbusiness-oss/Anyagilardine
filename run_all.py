import subprocess
import sys
import time

# Jalankan Bot NBA
proc1 = subprocess.Popen([sys.executable, "main.py"])
print("Bot NBA dimulai...")

# Jalankan Bot Bola
proc2 = subprocess.Popen([sys.executable, "football.py"])
print("Bot Bola dimulai...")

# Jaga agar script tetap hidup
try:
    while True:
        time.sleep(10)
        # Cek jika ada proses yang mati, lalu restart jika perlu
        if proc1.poll() is not None:
            proc1 = subprocess.Popen([sys.executable, "main.py"])
        if proc2.poll() is not None:
            proc2 = subprocess.Popen([sys.executable, "football.py"])
except KeyboardInterrupt:
    proc1.terminate()
    proc2.terminate()
    
