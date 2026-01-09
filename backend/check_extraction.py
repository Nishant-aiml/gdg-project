"""Check what data was extracted from a batch."""
import requests

BASE = "http://127.0.0.1:8000/api"

# Get recent batches
r = requests.get(f"{BASE}/batches")
if r.status_code == 405:
    print("Using dashboard endpoint instead...")
else:
    print(f"Batches status: {r.status_code}")

# Get dashboard data for a recent batch
batch_id = "batch_aicte_20260109_162823_1f54b44e"  # From previous test
print(f"\nChecking batch: {batch_id}")

r = requests.get(f"{BASE}/dashboard/{batch_id}")
print(f"Dashboard status: {r.status_code}")
if r.ok:
    data = r.json()
    print(f"\nInstitution: {data.get('institution_name')}")
    print(f"Status: {data.get('batch_status')}")
    print(f"Invalid: {data.get('is_invalid')}")
    print(f"Invalid reason: {data.get('invalid_reason')}")
    
    # Check blocks
    print(f"\n=== BLOCKS ===")
    for block in data.get("blocks", [])[:5]:
        print(f"- {block.get('block_type')}: present={block.get('is_present')}, conf={block.get('confidence')}")
        if block.get("data"):
            block_data = block.get("data")
            print(f"  Data keys: {list(block_data.keys())[:10]}")
            # Show some values
            for k, v in list(block_data.items())[:5]:
                print(f"    {k}: {v}")
    
    # Check KPIs
    print(f"\n=== KPIs ===")
    for kpi in data.get("kpi_cards", []):
        print(f"- {kpi.get('name')}: {kpi.get('value')} ({kpi.get('label')})")
else:
    print(f"Error: {r.text[:500]}")
