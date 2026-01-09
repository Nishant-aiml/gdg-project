# PowerShell script to start backend and run tests
Write-Host "Starting backend server..." -ForegroundColor Cyan
Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory "backend" -WindowStyle Hidden

Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
$maxWait = 20
$waited = 0
$ready = $false

while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Backend is ready!" -ForegroundColor Green
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
        $waited++
        Write-Host "Waiting... ($waited/$maxWait)" -ForegroundColor Gray
    }
}

if (-not $ready) {
    Write-Host "Backend did not start in time. Please start it manually:" -ForegroundColor Red
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  python -m uvicorn main:app --reload" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nRunning test suite..." -ForegroundColor Cyan
python test_frontend_backend_connections.py

