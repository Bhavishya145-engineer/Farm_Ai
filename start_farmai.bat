@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   FarmAI - Crop Recommendation System
echo ========================================
echo.

REM Check if .venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Install dependencies
echo Checking dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Starting backend server...
echo.

REM Start the FastAPI server in a new window
start "FarmAI Backend Server" cmd /k ".\.venv\Scripts\python.exe -m uvicorn crop:app --reload --port 8000"

REM Wait for server to start
timeout /t 5 /nobreak >nul

REM Open the web interface via HTTP
echo.
echo Opening web interface in your browser...
start "" "http://127.0.0.1:8000"

echo.
echo ========================================
echo   FarmAI is now running!
echo ========================================
echo.
echo Backend & UI: http://127.0.0.1:8000
echo.
echo Press any key to finish setup...
pause >nul
exit
