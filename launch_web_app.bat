@echo off
title Cisco Meraki Web Management Interface
color 0B
echo.
echo ==========================================
echo   🌐 Cisco Meraki Web Management
echo ==========================================
echo.

echo 🚀 Starting the modern web-based interface...
echo.

REM Stop the current container
echo Stopping current container...
docker-compose down

echo.
echo 🔄 Starting with web interface...

REM Start with the new web application
docker-compose up -d

echo.
echo ⏳ Waiting for web interface to start...
timeout /t 10 /nobreak >nul

echo.
echo ✅ Web interface should now be available!
echo.
echo 📍 Open your browser and go to:
echo    http://localhost:5000
echo.
echo 🎯 Features available:
echo    • Modern dashboard interface
echo    • Network topology visualization
echo    • Device and client management
echo    • No CLI commands needed!
echo.
echo 💡 If you need the old CLI interface:
echo    docker exec -it cisco-meraki-cli-app python main.py
echo.

REM Try to open the browser automatically
echo 🌐 Attempting to open browser...
start http://localhost:5000

echo.
echo 📝 Press any key to exit...
pause >nul
