"""
Comprehensive Frontend-Backend Connection Test
Tests all API endpoints and verifies data contracts, error handling, and role-based access.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

API_BASE = "http://127.0.0.1:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_success(msg):
    print(f"{Colors.GREEN}[PASS] {msg}{Colors.END}")

def log_error(msg):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.END}")

def log_info(msg):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.END}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARN] {msg}{Colors.END}")

def log_section(msg):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

results = {"passed": 0, "failed": 0, "warnings": 0}

def test_endpoint(name, method, endpoint, expected_status=200, data=None, headers=None, check_null_handling=False, allow_401=False):
    """Test an API endpoint."""
    global results
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            r = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            log_error(f"{name} - Unknown method: {method}")
            return None
        
        # Allow 401 if authentication is expected
        if r.status_code == expected_status or (allow_401 and r.status_code == 401):
            if r.status_code == 401 and allow_401:
                log_warning(f"{name} - Status 401 (Authentication required - expected)")
                results["warnings"] += 1
            else:
                log_success(f"{name} - Status {r.status_code}")
                results["passed"] += 1
            
            # Check null handling in response
            if check_null_handling and r.status_code == 200:
                try:
                    resp = r.json()
                    null_fields = find_null_values(resp)
                    if null_fields:
                        log_warning(f"  Found null values (should be handled as 'Insufficient Data'): {len(null_fields)} fields")
                        results["warnings"] += 1
                except:
                    pass
            
            return r.json() if r.status_code == 200 else None
        else:
            log_error(f"{name} - Expected {expected_status}, got {r.status_code}")
            if r.status_code >= 400:
                try:
                    error_detail = r.json().get('detail', r.text[:200])
                    print(f"  Error: {error_detail}")
                except:
                    print(f"  Response: {r.text[:200]}")
            results["failed"] += 1
            return None
    except requests.exceptions.ConnectionError:
        log_error(f"{name} - Connection refused (is backend running on {API_BASE}?)")
        results["failed"] += 1
        return None
    except Exception as e:
        log_error(f"{name} - Exception: {str(e)}")
        results["failed"] += 1
        return None

def find_null_values(obj, path=""):
    """Recursively find null values in response."""
    nulls = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if value is None:
                nulls.append(f"{path}.{key}" if path else key)
            elif isinstance(value, (dict, list)):
                nulls.extend(find_null_values(value, f"{path}.{key}" if path else key))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, (dict, list)):
                nulls.extend(find_null_values(item, f"{path}[{i}]"))
    return nulls

def test_health():
    """Test health endpoint."""
    log_section("1. HEALTH CHECK")
    test_endpoint("Health Check", "GET", "/health")
    return True

def test_batch_apis():
    """Test batch creation and listing."""
    log_section("2. BATCH APIs")
    
    # List batches (requires auth)
    batches = test_endpoint("List Batches", "GET", "/batches/list", allow_401=True)
    batch_ids = []
    if batches and isinstance(batches, list):
        log_info(f"  Found {len(batches)} existing batches")
        batch_ids = [b.get("batch_id") for b in batches[:5] if b.get("batch_id")]
    
    # Create new batch (requires auth)
    new_batch = test_endpoint(
        "Create AICTE Batch",
        "POST",
        "/batches/create",
        data={"mode": "aicte"},
        allow_401=True
    )
    
    if new_batch and new_batch.get("batch_id"):
        batch_ids.append(new_batch["batch_id"])
        log_info(f"  Created batch: {new_batch['batch_id']}")
    
    return batch_ids

def test_dashboard_apis(batch_ids):
    """Test dashboard endpoints."""
    log_section("3. DASHBOARD APIs")
    
    if not batch_ids:
        log_warning("  No batches available for dashboard testing")
        return None
    
    batch_id = batch_ids[0]
    log_info(f"  Testing with batch: {batch_id}")
    
    # Test dashboard data
    dashboard = test_endpoint(
        "Get Dashboard Data",
        "GET",
        f"/dashboard/{batch_id}",
        check_null_handling=True
    )
    
    if dashboard:
        # Check for invalid batch handling
        if dashboard.get("batch_status") == "invalid":
            log_warning(f"  Batch {batch_id} is marked as invalid")
        
        # Check KPI cards
        kpi_cards = dashboard.get("kpi_cards", [])
        log_info(f"  Found {len(kpi_cards)} KPI cards")
        
        # Check for null values in KPIs
        null_kpis = [k for k in kpi_cards if k.get("value") is None]
        if null_kpis:
            log_warning(f"  Found {len(null_kpis)} KPIs with null values (should show 'Insufficient Data')")
    
    # Test evaluation list
    evaluations = test_endpoint(
        "List Evaluations",
        "GET",
        "/dashboard/evaluations"
    )
    
    if evaluations:
        log_info(f"  Found {len(evaluations)} evaluations")
    
    # Test trends
    trends = test_endpoint(
        "Get Trends",
        "GET",
        f"/dashboard/trends/{batch_id}",
        check_null_handling=True
    )
    
    if trends:
        has_data = trends.get("has_historical_data", False)
        if not has_data:
            log_info("  Trends: Insufficient data (expected behavior)")
        else:
            log_info(f"  Trends: {len(trends.get('years_available', []))} years available")
    
    # Test forecast
    forecast = test_endpoint(
        "Get Forecast",
        "GET",
        f"/dashboard/forecast/{batch_id}/overall_score",
        check_null_handling=True
    )
    
    if forecast:
        has_forecast = forecast.get("has_forecast") or forecast.get("can_forecast", False)
        if not has_forecast:
            log_info("  Forecast: Insufficient data (expected behavior)")
            if forecast.get("insufficient_data_reason"):
                log_info(f"    Reason: {forecast['insufficient_data_reason']}")
        else:
            log_info(f"  Forecast: {len(forecast.get('forecast', []))} forecast points")
    
    # Test KPI details
    kpi_details = test_endpoint(
        "Get KPI Details",
        "GET",
        f"/dashboard/kpi-details/{batch_id}?kpi_type=overall",
        check_null_handling=True
    )
    
    return dashboard

def test_comparison_apis(batch_ids):
    """Test comparison endpoints."""
    log_section("4. COMPARISON APIs")
    
    if len(batch_ids) < 2:
        log_warning("  Need at least 2 batches for comparison testing")
        return None
    
    # Test comparison
    batch_ids_str = ",".join(batch_ids[:2])
    comparison = test_endpoint(
        "Compare Institutions",
        "GET",
        f"/compare?batch_ids={batch_ids_str}",
        check_null_handling=True
    )
    
    if comparison:
        valid = comparison.get("valid_for_comparison", False)
        if not valid:
            log_warning("  Comparison not valid")
            if comparison.get("validation_message"):
                log_info(f"    Reason: {comparison['validation_message']}")
        else:
            institutions = comparison.get("institutions", [])
            log_info(f"  Compared {len(institutions)} institutions")
            
            # Check for cross-department comparison
            if "Cross-department" in str(comparison.get("validation_message", "")):
                log_warning("  Cross-department comparison detected (should be prevented)")
    
    return comparison

def test_report_apis(batch_ids):
    """Test report generation."""
    log_section("5. REPORT APIs")
    
    if not batch_ids:
        log_warning("  No batches available for report testing")
        return None
    
    batch_id = batch_ids[0]
    
    # Test report generation
    generate_response = test_endpoint(
        "Generate Report",
        "POST",
        "/reports/generate",
        data={
            "batch_id": batch_id,
            "include_evidence": True,
            "include_trends": True,
            "report_type": "standard"
        }
    )
    
    if generate_response:
        log_info(f"  Report generated: {generate_response.get('download_url', 'N/A')}")
    
    return generate_response

def test_chatbot_apis(batch_ids):
    """Test chatbot endpoint."""
    log_section("6. CHATBOT APIs")
    
    if not batch_ids:
        log_warning("  No batches available for chatbot testing")
        return None
    
    batch_id = batch_ids[0]
    
    # Test chatbot query
    chatbot_response = test_endpoint(
        "Chatbot Query",
        "POST",
        "/chatbot/query",
        data={
            "query": "Explain the overall score",
            "batch_id": batch_id,
            "current_page": "dashboard"
        },
        expected_status=200
    )
    
    if chatbot_response:
        has_answer = bool(chatbot_response.get("answer"))
        if has_answer:
            log_info("  Chatbot returned answer")
        else:
            log_warning("  Chatbot response missing answer")
    
    return chatbot_response

def test_invalid_batch_handling(batch_ids):
    """Test invalid batch exclusion."""
    log_section("7. INVALID BATCH HANDLING")
    
    if not batch_ids:
        log_warning("  No batches available for invalid batch testing")
        return
    
    batch_id = batch_ids[0]
    
    # Get batch info
    batch_info = test_endpoint(
        "Get Batch Info",
        "GET",
        f"/batches/{batch_id}"
    )
    
    if batch_info:
        is_invalid = batch_info.get("is_invalid", False)
        if is_invalid:
            log_info("  Batch is marked as invalid")
            
            # Test that invalid batches are excluded
            test_endpoint(
                "Invalid Batch - Dashboard (should fail)",
                "GET",
                f"/dashboard/{batch_id}",
                expected_status=400  # Should fail for invalid batch
            )
        else:
            log_info("  Batch is valid")

def test_role_based_access():
    """Test role-based access control."""
    log_section("8. ROLE-BASED ACCESS CONTROL")
    
    # Test without auth token (should work for public endpoints)
    log_info("  Testing public endpoints (no auth required)")
    
    # Test with invalid token (should fail)
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    test_endpoint(
        "Invalid Auth Token",
        "GET",
        "/batches/list",
        headers=invalid_headers,
        expected_status=401  # Should fail with invalid token
    )
    
    log_info("  Note: Full role-based testing requires valid Firebase tokens")

def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*60)
    print("  FRONTEND-BACKEND CONNECTION TEST SUITE")
    print("="*60)
    print(Colors.END)
    
    # Check if backend is running
    try:
        # Try /api/health first (correct endpoint)
        r = requests.get(f"{API_BASE}/health", timeout=3)
        if r.status_code == 200:
            log_success("Backend is running")
        else:
            # Try root /health as fallback
            r2 = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=3)
            if r2.status_code == 200:
                log_success("Backend is running")
            else:
                log_error("Backend health check failed")
                sys.exit(1)
    except requests.exceptions.ConnectionError:
        log_error(f"Cannot connect to backend at {API_BASE}")
        log_info("Please ensure the backend is running: cd backend && python -m uvicorn main:app --reload")
        sys.exit(1)
    except Exception as e:
        log_error(f"Backend check error: {e}")
        sys.exit(1)
    
    log_success("Backend is running")
    
    # Run tests
    test_health()
    batch_ids = test_batch_apis()
    test_dashboard_apis(batch_ids)
    test_comparison_apis(batch_ids)
    test_report_apis(batch_ids)
    test_chatbot_apis(batch_ids)
    test_invalid_batch_handling(batch_ids)
    test_role_based_access()
    
    # Summary
    log_section("TEST SUMMARY")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.YELLOW}Warnings: {results['warnings']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    
    total = results['passed'] + results['failed']
    if total > 0:
        success_rate = (results['passed'] / total) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if results['failed'] > 0:
        log_error("\nSome tests failed. Please review the errors above.")
        sys.exit(1)
    else:
        log_success("\nAll critical tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()

