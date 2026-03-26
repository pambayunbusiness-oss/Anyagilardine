import subprocess
import sys
import time

# Menjalankan bot NBA (main.py)
p1 = subprocess.Popen([sys.executable, "main.py"])
print("Memulai Bot NBA...")

# Menjalankan bot Bola (football.py)
p2 = subprocess.Popen([sys.executable, "football.py"])
print("Memulai Bot Bola...")

# Menjaga agar script utama tetap hidup selama bot berjalan
try:
    p1.wait()
    p2.wait()
except KeyboardInterrupt:
    p1.terminate()
    p2.terminate()
  
