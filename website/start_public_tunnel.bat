@echo off
title Logistics Resilience Network (LRN) - Public Cloudflare Tunnel Launcher
color 0B
echo =========================================================================
echo       LOGISTICS RESILIENCE NETWORK (LRN) - PUBLIC INTERNET LAUNCHER
echo =========================================================================
echo.
echo [1/2] Starting Backend Server on port 8000...
start /B python server.py

timeout /t 3 /nobreak >nul

echo [2/2] Launching Public Cloudflare Tunnel...
echo.
echo -------------------------------------------------------------------------
echo Your website will be accessible globally from any laptop or mobile device!
echo Watch below for your public HTTPS link (https://*.trycloudflare.com):
echo -------------------------------------------------------------------------
echo.

.\cloudflared.exe tunnel --url http://127.0.0.1:8000

pause
