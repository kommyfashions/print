@echo off
title PDF SKU Sorter

cd /d %~dp0

echo =====================================
echo Starting PDF SKU Sorter...
echo =====================================
echo.

REM Check Python availability
python --version
if errorlevel 1 (
    echo.
    echo ❌ Python not found. Please install Python and add it to PATH.
    echo.
    pause
    exit /b
)

echo.
echo Starting Flask server...
echo.

REM Start Flask in same window so we see errors
start "" /B cmd /C "python app.py"

REM Give server time to start
timeout /t 3 > nul

echo Opening browser...
start "" http://localhost:5000

echo.
echo -------------------------------------
echo App is running.
echo DO NOT close this window.
echo -------------------------------------
echo.

pause
