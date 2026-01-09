"""Quick test for sample.pdf upload and processing"""
import requests
import time

API_BASE = "http://localhost:8000/api"

print("1. Creating batch...")
batch_resp = requests.post(f"{API_BASE}/batches/create", json={
    "mode": "aicte",
    "institution_name": "Test University"
})
print(f"   Response: {batch_resp.status_code}")
batch_data = batch_resp.json()
batch_id = batch_data.get("batch_id")
print(f"   Batch ID: {batch_id}")

print("\n2. Uploading sample.pdf...")
with open("../sample.pdf", "rb") as f:
    upload_resp = requests.post(
        f"{API_BASE}/documents/upload",
        files={"files": ("sample.pdf", f, "application/pdf")},
        data={"batch_id": batch_id}
    )
print(f"   Response: {upload_resp.status_code}")
print(f"   Data: {upload_resp.json()}")

print("\n3. Starting processing...")
proc_resp = requests.post(f"{API_BASE}/processing/start", json={
    "batch_id": batch_id
})
print(f"   Response: {proc_resp.status_code}")
print(f"   Data: {proc_resp.json()}")

print("\n4. Polling status (60 seconds max)...")
for i in range(30):
    time.sleep(2)
    status_resp = requests.get(f"{API_BASE}/processing/status/{batch_id}")
    status_data = status_resp.json()
    status = status_data.get("status", "unknown")
    progress = status_data.get("progress", 0)
    stage = status_data.get("current_stage", "")
    errors = status_data.get("errors", [])
    
    print(f"   {i*2:3d}s: {progress:3.0f}% | {status:20s} | {stage}")
    
    if errors:
        print(f"        ERRORS: {errors}")
    
    if status in ["completed", "failed"]:
        break

print("\n5. Final status check...")
final_resp = requests.get(f"{API_BASE}/processing/status/{batch_id}")
print(f"   Final: {final_resp.json()}")

print("\nDone!")
