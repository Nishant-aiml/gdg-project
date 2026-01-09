"""Wait for backend to be ready"""
import requests
import time
import sys

max_attempts = 15
url = "http://127.0.0.1:8000/health"

for i in range(max_attempts):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            print("✓ Backend is running!")
            sys.exit(0)
    except:
        pass
    print(f"Waiting for backend... ({i+1}/{max_attempts})")
    time.sleep(1)

print("[FAIL] Backend did not start in time")
sys.exit(1)

