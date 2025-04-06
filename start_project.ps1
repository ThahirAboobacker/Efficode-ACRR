# PowerShell script to start both backend and frontend
Write-Host "Starting Efficode-ACRR application..." -ForegroundColor Green

# Start the backend server
Write-Host "Starting backend server..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend\src"
if (-not (Test-Path $backendPath)) {
    Write-Host "Error: Backend directory not found at $backendPath" -ForegroundColor Red
    exit 1
}
cd $backendPath

# Start Python app in background
Start-Process python -ArgumentList "app.py" -NoNewWindow

Write-Host "Backend server started on http://localhost:5500" -ForegroundColor Green
Write-Host "API available at http://localhost:5500/api/optimize" -ForegroundColor Green

# Wait a moment for server to initialize
Start-Sleep -Seconds 2

# Start the frontend
Write-Host "Starting frontend development server..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path $frontendPath)) {
    Write-Host "Error: Frontend directory not found at $frontendPath" -ForegroundColor Red
    exit 1
}
cd $frontendPath

# Start npm in a new window
Start-Process powershell -ArgumentList "-Command cd '$frontendPath'; npm run dev"

Write-Host "Frontend started on http://localhost:3000" -ForegroundColor Green
Write-Host "`nBoth servers are now running!" -ForegroundColor Yellow
Write-Host "Access the application at http://localhost:3000" -ForegroundColor Yellow 