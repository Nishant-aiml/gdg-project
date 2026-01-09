# Start Preview Script - AI-Powered Accreditation Platform
Write-Host "Starting AI-Powered Accreditation Platform Preview..." -ForegroundColor Green
Write-Host ""

# Check if backend venv exists
$backendVenv = "backend\venv\Scripts\Activate.ps1"
if (-not (Test-Path $backendVenv)) {
    Write-Host "Backend virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Check if frontend node_modules exists
$frontendNodeModules = "frontend\node_modules"
if (-not (Test-Path $frontendNodeModules)) {
    Write-Host "Frontend node_modules not found. Installing..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host "Environment check passed!" -ForegroundColor Green
Write-Host ""

# Start Backend Server
Write-Host "Starting Backend Server on port 8000..." -ForegroundColor Cyan
$backendScript = @"
cd '$PWD\backend'
.\venv\Scripts\Activate.ps1
python main.py
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "Starting Frontend Server on port 3000..." -ForegroundColor Cyan
$frontendScript = @"
cd '$PWD\frontend'
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

# Wait for frontend to start
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# Open browser after delay
Start-Sleep -Seconds 8
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Preview is ready!" -ForegroundColor Green
Write-Host ""
