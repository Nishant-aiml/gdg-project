"""Quick connection test"""
import requests
import sys

API_BASE = "http://127.0.0.1:8000/api"

def test_connection():
    """Test basic API connections"""
    print("=" * 60)
    print("QUICK CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Test health
    try:
        r = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=5)
        if r.status_code == 200:
            print("[PASS] Health check - Backend is running")
        else:
            print(f"[WARN] Health check returned {r.status_code}")
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to backend")
        print("Please start backend: cd backend && python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"[FAIL] Health check error: {e}")
        return False
    
    # Test API health
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        if r.status_code == 200:
            print("[PASS] API health endpoint")
        else:
            print(f"[WARN] API health returned {r.status_code}")
    except Exception as e:
        print(f"[WARN] API health check: {e}")
    
    # Test batch list
    try:
        r = requests.get(f"{API_BASE}/batches/list", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"[PASS] Batch list API - Found {len(data)} batches")
        else:
            print(f"[WARN] Batch list returned {r.status_code}")
    except Exception as e:
        print(f"[WARN] Batch list: {e}")
    
    # Test dashboard evaluations
    try:
        r = requests.get(f"{API_BASE}/dashboard/evaluations", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"[PASS] Dashboard evaluations API - Found {len(data)} evaluations")
        else:
            print(f"[WARN] Dashboard evaluations returned {r.status_code}")
    except Exception as e:
        print(f"[WARN] Dashboard evaluations: {e}")
    
    print()
    print("=" * 60)
    print("Test complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_connection()

