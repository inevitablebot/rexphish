@echo off
cd /d "%~dp0"
echo Starting Cloudflare Tunnel Setup...


echo.
echo Starting tunnel...
echo Paste it into the "Public Base URL" field on the dashboard.
echo.
cloudflared tunnel run rex
pause
