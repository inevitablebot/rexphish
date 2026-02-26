@echo off
cd /d "%~dp0"
echo Starting Cloudflare Tunnel Setup...


echo.
echo Starting tunnel...
echo COPY THE URL BELOW (e.g., https://warm-sunset-....trycloudflare.com)
echo Paste it into the "Public Base URL" field on the dashboard.
echo.
cloudflared.exe tunnel --url http://localhost:5000
pause
