@echo off
title Cisco Meraki CLI - Topology Launcher
color 0B
echo.
echo ==========================================
echo   🌐 Cisco Meraki CLI - Quick Launch
echo ==========================================
echo.

REM Check if Docker container is running
echo Checking Docker container status...
docker ps | findstr cisco-meraki-cli-app >nul
if %errorlevel% neq 0 (
    echo.
    echo 🚀 Starting Docker container...
    docker-compose up -d
    echo Waiting for container to be ready...
    timeout /t 8 /nobreak >nul
    echo.
)

echo ✅ Docker container is running
echo.
echo 🌐 Launching Topology Visualization...
echo.
echo This will open a simple interface to:
echo   1. Enter your Meraki API key
echo   2. Select your organization
echo   3. Select your network
echo   4. Launch topology visualization
echo.

REM Launch the quick launch script
docker exec -it cisco-meraki-cli-app python quick_launch.py

echo.
echo 📝 Press any key to exit...
pause >nul
