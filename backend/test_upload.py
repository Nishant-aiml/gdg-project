import requests

# Create batch
r = requests.post('http://127.0.0.1:8000/api/batches/create', json={'mode': 'aicte', 'institution_name': 'Python Upload Test'})
batch_id = r.json()['batch_id']
print(f'Batch created: {batch_id}')

# Upload file
with open(r'c:\Users\datta\OneDrive\Desktop\gdg\sample.pdf', 'rb') as f:
    r = requests.post(
        f'http://127.0.0.1:8000/api/documents/{batch_id}/upload',
        files={'file': ('sample.pdf', f, 'application/pdf')}
    )
    print(f'Upload status: {r.status_code}')
    print(f'Upload response: {r.text[:200]}')

# Check batch
r = requests.get(f'http://127.0.0.1:8000/api/batches/{batch_id}')
batch = r.json()
print(f'Batch status: {batch.get("status")}')
print(f'Total documents: {batch.get("total_documents")}')

# Start processing
r = requests.post('http://127.0.0.1:8000/api/processing/start', json={'batch_id': batch_id})
print(f'Processing started: {r.json()}')

print(f'\nBATCH_ID: {batch_id}')
