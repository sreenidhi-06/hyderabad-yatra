@echo off
title Hyderabad Travel Guide
echo ============================================
echo    Smart Travel & Temple Guide - Hyderabad
echo ============================================
echo.
echo Starting the server...
echo Your browser will open automatically.
echo.
echo To stop the server, close this window or press Ctrl+C
echo.

cd /d "%~dp0hyderabad-travel-guide"

start http://127.0.0.1:5000

python app.py

pause
C