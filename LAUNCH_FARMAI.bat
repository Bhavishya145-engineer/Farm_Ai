@echo off
setlocal enabledelayedexpansion
title FarmAI - Universal App Launcher
color 0A

:: Set working directory to the script's location
cd /d %~dp0

cls
echo =========================================================================
echo                   FARMAI - SMART AGRICULTURE ECOSYSTEM
echo =========================================================================
echo.
echo  [1] Starting Backend Services...
echo  [2] Checking Python Environment...

:: Check for Virtual Environment
if exist ".venv\Scripts\activate.bat" (
    echo      - Activating Virtual Environment...
    call .venv\Scripts\activate.bat
) else (
    echo      - Using System Python (No virtual env detected).
)

:: Check for requirements
if exist "requirements.txt" (
    echo  [3] Checking Dependencies (this may take a moment on first run)...
    pip install -r requirements.txt --quiet
)

:: Identify Local IP Address
echo.
echo =========================================================================
echo              >>> HOW TO CONNECT YOUR ANDROID DEVICE <<<
echo =========================================================================
echo.
echo  STAY ON THE SAME WI-FI!
echo.
echo  1. Your Computer's IP is:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set "ip=%%a"
    set "ip=!ip: =!"
    echo     --^> !ip!
)
echo.
echo  2. On your Android Phone:
echo     --^> Open the FarmAI App (or Chrome browser)
echo     --^> Connect to: http://!ip!:8000
echo.
echo =========================================================================
echo.

:: Launch local browser for PC access
start http://localhost:8000

:: Run the FastAPI server
echo  [4] SERVER STARTING... Press Ctrl+C to stop.
echo.
:: We use the root crop.py as it's the primary source
python -m uvicorn crop:app --reload --host 0.0.0.0 --port 8000

pause
