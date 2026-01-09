@echo off
title Brainwave Stress System
echo ===================================================
echo   Starting Brainwave Stress Detection System
echo ===================================================
echo.
cd /d "%~dp0"

echo [1/3] Launching Dashboard in Browser...
start "" "http://localhost:5000"

echo [2/3] Starting Server...
echo.
echo       -------------------------------------------------------------
echo       PERMANENT NETWORK LINK (Use this on other devices):
for /f "tokens=14" %%a in ('ipconfig ^| findstr IPv4') do echo       http://%%a:5000
echo       -------------------------------------------------------------
echo.
echo [3/3] System Logic Running...
echo.
echo       NOTE: Do NOT close this window. Minimize it to keep the app running.
echo       To stop the app, close this window.
echo.

if exist ".\.venv\Scripts\python.exe" (
    ".\.venv\Scripts\python.exe" server.py
) else (
    echo Virtual Environment Python not found! Trying global python...
    python server.py
)

if %errorlevel% neq 0 (
    echo.
    echo !!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!
    echo The application crashed.
    pause
    exit /b
)
pause
