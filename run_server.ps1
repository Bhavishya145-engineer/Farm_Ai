# FarmAI Server Launcher (PowerShell)
Write-Host "========================================" -ForegroundColor Green
Write-Host "  FarmAI - Crop Recommendation System" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "Checking dependencies..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "`nStarting backend server..." -ForegroundColor Cyan
Start-Process "powershell" -ArgumentList "-NoExit -Command & '.\.venv\Scripts\python.exe' -m uvicorn crop:app --reload --port 8000"

Start-Sleep -Seconds 5
Write-Host "Opening web interface: http://127.0.0.1:8000" -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

Write-Host "`nFarmAI is now running!" -ForegroundColor Green
