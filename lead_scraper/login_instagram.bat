@echo off
title Nebulyx Instagram Account Switcher & Login
cd /d "%~dp0\.."
echo ========================================================
echo   NEBULYX - INSTAGRAM ACCOUNT LOGIN / SWITCHER
echo ========================================================
echo.
set /p IG_USER="Enter Instagram handle to prefill (or press Enter for blank login): "
echo.
if "%IG_USER%"=="" (
    python lead_scraper\login_manager.py --switch
) else (
    python lead_scraper\login_manager.py --switch --username %IG_USER%
)
pause
