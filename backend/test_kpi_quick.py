"""Quick test for KPI details endpoint."""
import requests

BASE = "http://127.0.0.1:8000/api"
batch_id = "batch_aicte_20260109_161540_073bbce7"

# Test batch exists
r1 = requests.get(f"{BASE}/batches")
print(f"All batches: {r1.status_code}")
if r1.ok:
    batches = r1.json()
    print(f"  Found {len(batches)} batches")
    matching = [b for b in batches if isinstance(b, dict) and batch_id in str(b.get('id', ''))]
    print(f"  Matching batch: {matching}")

# Test KPI details
r2 = requests.get(f"{BASE}/dashboard/kpi-details/{batch_id}?kpi_type=infrastructure")
print(f"\nKPI details: {r2.status_code}")
print(f"  Response: {r2.text[:500] if r2.text else 'empty'}")

# Test demo batch
r3 = requests.get(f"{BASE}/dashboard/kpi-details/demo-batch-aicte-2024?kpi_type=infrastructure")
print(f"\nDemo KPI details: {r3.status_code}")
print(f"  Response: {r3.text[:500] if r3.text else 'empty'}")
