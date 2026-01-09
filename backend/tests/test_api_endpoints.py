"""
API Endpoint Tests for All Modes
Tests backend API endpoints for AICTE, NBA, NAAC, NIRF
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_api_health():
    """Test API is running"""
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


def test_naac_endpoints():
    """Test NAAC API endpoints"""
    print("\n📋 NAAC Endpoints")
    print("-" * 40)
    
    # Test grading scale (no auth required)
    try:
        r = requests.get(f"{BASE_URL}/api/naac/grading-scale")
        if r.status_code == 200:
            data = r.json()
            assert "grades" in data
            print(f"✅ GET /api/naac/grading-scale - {len(data['grades'])} grades")
        else:
            print(f"⚠️ Grading scale: {r.status_code}")
    except Exception as e:
        print(f"❌ NAAC grading: {e}")
    
    # Test dashboard (may need auth)
    try:
        r = requests.get(f"{BASE_URL}/api/naac/test-batch/dashboard")
        if r.status_code in [200, 401, 403]:  # 401/403 expected without auth
            print(f"✅ GET /api/naac/:batch/dashboard - {r.status_code}")
        else:
            print(f"⚠️ Dashboard: {r.status_code}")
    except Exception as e:
        print(f"❌ NAAC dashboard: {e}")


def test_nirf_endpoints():
    """Test NIRF API endpoints"""
    print("\n📋 NIRF Endpoints")
    print("-" * 40)
    
    # Test parameters info
    try:
        r = requests.get(f"{BASE_URL}/api/nirf/parameters-info")
        if r.status_code == 200:
            data = r.json()
            assert "parameters" in data
            print(f"✅ GET /api/nirf/parameters-info - {len(data['parameters'])} params")
        else:
            print(f"⚠️ Parameters info: {r.status_code}")
    except Exception as e:
        print(f"❌ NIRF parameters: {e}")
    
    # Test dashboard
    try:
        r = requests.get(f"{BASE_URL}/api/nirf/test-batch/dashboard")
        if r.status_code in [200, 401, 403]:
            print(f"✅ GET /api/nirf/:batch/dashboard - {r.status_code}")
        else:
            print(f"⚠️ NIRF Dashboard: {r.status_code}")
    except Exception as e:
        print(f"❌ NIRF dashboard: {e}")


def test_nba_endpoints():
    """Test NBA API endpoints"""
    print("\n📋 NBA Endpoints")
    print("-" * 40)
    
    # Test dashboard
    try:
        r = requests.get(f"{BASE_URL}/api/nba/test-batch/dashboard")
        if r.status_code in [200, 401, 403]:
            print(f"✅ GET /api/nba/:batch/dashboard - {r.status_code}")
        else:
            print(f"⚠️ NBA Dashboard: {r.status_code}")
    except Exception as e:
        print(f"❌ NBA dashboard: {e}")


def test_existing_endpoints():
    """Test existing AICTE/general endpoints"""
    print("\n📋 Existing Endpoints")
    print("-" * 40)
    
    endpoints = [
        ("/api/batches", "Batches list"),
        ("/api/kpi/details/overall_score?batch_id=test", "KPI details"),
        ("/api/demo/batches", "Demo batches"),
    ]
    
    for endpoint, name in endpoints:
        try:
            r = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{'✅' if r.status_code in [200, 401, 404] else '⚠️'} {name}: {r.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")


def run_api_tests():
    """Run all API tests"""
    print("=" * 60)
    print("API ENDPOINT TESTS")
    print("=" * 60)
    
    if not test_api_health():
        print("\n❌ API not running. Start backend first.")
        return False
    
    test_naac_endpoints()
    test_nirf_endpoints()
    test_nba_endpoints()
    test_existing_endpoints()
    
    print("\n" + "=" * 60)
    print("API TESTS COMPLETED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    run_api_tests()
