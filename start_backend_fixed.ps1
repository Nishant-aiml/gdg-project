# Start Backend Server (Fixed - Uses SQLite)
# This script ensures DATABASE_URL is unset so backend uses SQLite

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Backend Server (SQLite Mode)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Unset DATABASE_URL to force SQLite
$env:DATABASE_URL = $null
Write-Host "[OK] DATABASE_URL unset - will use SQLite`n" -ForegroundColor Green

# Change to backend directory
$backendDir = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendDir)) {
    Write-Host "[ERROR] Backend directory not found: $backendDir" -ForegroundColor Red
    exit 1
}

Set-Location $backendDir
Write-Host "Backend directory: $backendDir`n" -ForegroundColor Gray

# Start uvicorn
Write-Host "Starting uvicorn server...`n" -ForegroundColor Yellow
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

