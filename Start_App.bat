@echo off
echo Starting Brainwave Stress System...
echo Note: Do not close this window while using the app.
cd /d "%~dp0"
.\.venv\Scripts\python.exe app4.py
pause
