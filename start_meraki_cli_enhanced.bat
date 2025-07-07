@echo off
REM Enhanced Cisco Meraki CLI Launcher with SSL Fixes
REM This batch file ensures the CLI runs with all SSL fixes applied

echo 🚀 Starting Cisco Meraki CLI - Enhanced Edition
echo ===============================================

REM Change to the CLI directory
cd /d "C:\Users\keith.ransom\Utilities\cisco-meraki-cli"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found in current directory
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

REM Start the CLI (SSL fixes are auto-applied in main.py)
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ❌ The CLI exited with an error
    pause
)
