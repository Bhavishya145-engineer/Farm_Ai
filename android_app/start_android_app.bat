@echo off
title FarmAI Android Web App Server
echo Starting FarmAI PWA Backend...
cd /d %~dp0
python -m uvicorn crop:app --reload --host 0.0.0.0 --port 8000
pause
