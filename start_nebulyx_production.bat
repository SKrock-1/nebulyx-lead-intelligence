@echo off
title Nebulyx Lead Intelligence & Sellbird Sales CRM
color 0B

echo ===========================================================================
echo        NEBULYX // AUTONOMOUS INSTAGRAM REEL LEAD INTELLIGENCE
echo                Technology, Thoughtfully Engineered.
echo ===========================================================================
echo.

cd /d "%~dp0"

echo [*] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo [*] Checking dependencies...
pip show playwright >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing required packages...
    pip install -r requirements.txt
    playwright install chromium msedge
)

echo [*] Checking Instagram Authentication...
if exist "lead_scraper\auth_state.json" (
    echo [OK] Authenticated session detected.
) else (
    echo [WARN] No active session found. Running login manager...
    python lead_scraper\login_manager.py --interactive
)

echo.
echo ===========================================================================
echo [STATUS] Starting Nebulyx Production Server on Port 8088...
echo [STATUS] Opening Command Center at http://localhost:8088/dashboard.html
echo ===========================================================================
echo.

start "" "http://localhost:8088/dashboard.html"
python lead_scraper\server.py

pause
