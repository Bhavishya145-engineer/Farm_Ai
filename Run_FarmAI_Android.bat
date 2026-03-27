@echo off
setlocal
cd /d %~dp0

title FarmAI - Android Web App Launcher

echo ============================================================
echo               FarmAI - SMART AGRICULTURE AI
echo                (Android Web App Launcher)
echo ============================================================
echo.

:: 1. Environment Check
echo [STEP 1] Checking Environment...
if exist ".venv\Scripts\activate.bat" (
    echo - Found Virtual Environment. Activating...
    call .venv\Scripts\activate.bat
) else (
    echo - No Virtual Environment found. Using system Python...
)

:: 2. Dependency Check
echo [STEP 2] Verifying Dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [!] Warning: Some dependencies failed to install. Please check your internet.
)

:: 3. Identify IP Address for Android Connection
echo [STEP 3] Identifying Network Details...
echo.
echo ------------------------------------------------------------
echo TO ACCESS FROM YOUR ANDROID PHONE:
echo 1. Connect your phone to the SAME Wi-Fi as this PC.
echo 2. Find your "IPv4 Address" below:
ipconfig | findstr /i "IPv4"
echo.
echo 3. Open Chrome on your Phone and enter: http://YOUR_IP:8000
echo ------------------------------------------------------------
echo.

:: 4. Start Server
echo [STEP 4] Launching Backend Server...
timeout /t 2 /nobreak >nul

:: Open local browser for quick preview
start http://localhost:8000

:: Run the server
cd android_app
python -m uvicorn crop:app --reload --host 0.0.0.0 --port 8000

pause
