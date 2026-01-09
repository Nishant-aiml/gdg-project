"""Test real data flow: Upload sample.pdf, process, check KPI details."""
import requests
import os
import time

BASE = "http://127.0.0.1:8000/api"

# Find sample.pdf
pdf_path = None
for candidate in ["./sample.pdf", "./tests/sample.pdf", "../sample.pdf"]:
    if os.path.exists(candidate):
        pdf_path = candidate
        break

if not pdf_path:
    print("ERROR: sample.pdf not found")
    exit(1)

print(f"Using: {pdf_path}")

# 1. Create batch
r1 = requests.post(f"{BASE}/batches/", json={
    "mode": "aicte",
    "institution_name": "Test Institute",
    "department_name": "Computer Science",
    "academic_year": "2024-25"
})
print(f"\n1. Create batch: {r1.status_code}")
if not r1.ok:
    print(f"   Error: {r1.text}")
    exit(1)
batch_data = r1.json()
batch_id = batch_data.get("batch_id") or batch_data.get("id")
print(f"   Batch ID: {batch_id}")

# 2. Upload file
with open(pdf_path, 'rb') as f:
    r2 = requests.post(
        f"{BASE}/files/upload",
        files={"file": ("sample.pdf", f, "application/pdf")},
        data={"batch_id": batch_id}
    )
print(f"\n2. Upload file: {r2.status_code}")

# 3. Start processing
r3 = requests.post(f"{BASE}/processing/start", json={"batch_id": batch_id})
print(f"\n3. Start processing: {r3.status_code}")

# 4. Poll status until complete
print("\n4. Waiting for processing...")
for i in range(60):  # Max 2 minutes
    time.sleep(2)
    r4 = requests.get(f"{BASE}/processing/status/{batch_id}")
    if r4.ok:
        status_data = r4.json()
        stage = status_data.get("current_stage", "unknown")
        progress = status_data.get("progress", 0)
        status = status_data.get("status", "unknown")
        print(f"   [{i*2}s] {stage}: {progress}% (status: {status})")
        if status in ["completed", "failed"]:
            break
    else:
        print(f"   Error: {r4.status_code}")
        break

# 5. Check KPI details
print("\n5. Checking KPI details...")
r5 = requests.get(f"{BASE}/dashboard/kpi-details/{batch_id}?kpi_type=infrastructure")
print(f"   Status: {r5.status_code}")
if r5.ok:
    kpi_data = r5.json()
    print(f"   Institution: {kpi_data.get('institution_name')}")
    fsr = kpi_data.get("fsr")
    if fsr:
        print(f"   FSR Score: {fsr.get('final_score')} (quality: {fsr.get('data_quality')})")
        for p in fsr.get("parameters", [])[:3]:
            print(f"     - {p.get('display_name')}: {p.get('raw_value')} (missing: {p.get('missing')})")
    else:
        print("   FSR: None (insufficient data)")
    
    infra = kpi_data.get("infrastructure")
    if infra:
        print(f"   Infrastructure Score: {infra.get('final_score')} (quality: {infra.get('data_quality')})")
    else:
        print("   Infrastructure: None (insufficient data)")
else:
    print(f"   Error: {r5.text[:200]}")

print(f"\n✅ Done! Batch ID: {batch_id}")
