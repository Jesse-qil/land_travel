@echo off
chcp 65001 >nul 2>&1
title Travel Recommender System

echo ========================================
echo   Land Travel Smart Recommender v3.2
echo   One-click Launcher
echo ========================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

python --version
echo.

:: Install dependencies
echo [1/3] Checking Python dependencies...
pip install -r travel-agent\requirements.txt -q 2>nul
pip install -r travel-app\backend\requirements.txt -q 2>nul
echo OK
echo.

:: Start AI Agent (port 8001)
echo [2/3] Starting AI Agent (port 8001)...
start "AI Agent" cmd /k "title AI Agent && cd /d "%~dp0travel-agent" && python -m uvicorn server:app --port 8001 --reload"
timeout /t 3 /nobreak >nul

:: Start Backend (port 8000)
echo [3/3] Starting Backend (port 8000)...
start "Backend" cmd /k "title Backend && cd /d "%~dp0travel-app\backend" && python -m uvicorn main:app --port 8000 --reload"

echo.
echo ========================================
echo   All services started!
echo.
echo   Backend:     http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo   AI Agent:    http://localhost:8001/health
echo.
echo   Close the new windows to stop services.
echo ========================================
echo.
pause >nul
