@echo off
title Nebulyx Cloudflare Tunnel Exposer
color 0A

echo ===========================================================================
echo       NEBULYX // CLOUDFLARE PUBLIC HTTPS TUNNEL EXPOSER
echo ===========================================================================
echo.
echo [*] Exposing local port 8088 to a secure public HTTPS URL...
echo [*] This allows accessing your dashboard from your smartphone anywhere!
echo.

where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo [NOTICE] Cloudflare Tunnel (cloudflared) is not found in PATH.
    echo Downloading lightweight cloudflared.exe for Windows...
    curl -L --output "%~dp0cloudflared.exe" https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
    "%~dp0cloudflared.exe" tunnel --url http://localhost:8088
) else (
    cloudflared tunnel --url http://localhost:8088
)

pause
