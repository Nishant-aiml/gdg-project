# Start Frontend Server
# This script starts the Next.js development server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Server" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Change to frontend directory
$frontendDir = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path $frontendDir)) {
    Write-Host "[ERROR] Frontend directory not found: $frontendDir" -ForegroundColor Red
    exit 1
}

Set-Location $frontendDir
Write-Host "Frontend directory: $frontendDir`n" -ForegroundColor Gray

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "[WARN] node_modules not found. Installing dependencies...`n" -ForegroundColor Yellow
    npm install
}

# Start Next.js dev server
Write-Host "Starting Next.js development server...`n" -ForegroundColor Yellow
npm run dev

