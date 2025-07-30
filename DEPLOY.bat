@echo off
title Cisco Meraki Web Management - One-Click Deploy
color 0B
cls

echo.
echo ========================================================
echo   🌐 Cisco Meraki Web Management - One-Click Deploy
echo ========================================================
echo.
echo 🚀 This will deploy the complete Cisco Meraki web interface
echo 📦 Includes all CLI functionality in a modern web UI
echo 🔧 No technical knowledge required - just Docker!
echo.

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Docker is not running or not installed!
    echo.
    echo 📋 Please ensure Docker Desktop is:
    echo    1. Installed on your system
    echo    2. Running ^(Docker Desktop started^)
    echo    3. Accessible from command line
    echo.
    echo 💡 Download Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running!
echo.

REM Create required directories
echo 📁 Creating required directories...
if not exist "config" mkdir config
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "static" mkdir static
echo ✅ Directories created!
echo.

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker-compose down 2>nul
echo ✅ Cleanup complete!
echo.

REM Build and start the application
echo 🔨 Building and starting Cisco Meraki Web Management...
echo    This may take a few minutes on first run...
echo.

docker-compose up --build -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Deployment failed!
    echo 📋 Common solutions:
    echo    1. Ensure Docker Desktop has enough resources ^(4GB+ RAM^)
    echo    2. Check if port 5000 is already in use
    echo    3. Restart Docker Desktop and try again
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Deployment successful!
echo.

REM Wait for application to be ready
echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if application is responding
echo 🔍 Checking application health...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:5000 >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Application is ready!
        goto :app_ready
    )
    timeout /t 2 /nobreak >nul
)

echo ⚠️ Application may still be starting...

:app_ready
echo.
echo ========================================================
echo   🎉 DEPLOYMENT COMPLETE!
echo ========================================================
echo.
echo 🌐 Web Interface: http://localhost:5000
echo 📱 Access from any browser on your network
echo 🔧 All CLI features available in modern web UI
echo.
echo 📋 Next Steps:
echo    1. Open your browser to http://localhost:5000
echo    2. Enter your Cisco Meraki API key
echo    3. Select your organization and networks
echo    4. Enjoy the modern web interface!
echo.
echo 🛠️ Management Commands:
echo    • View logs: docker-compose logs -f
echo    • Stop app:  docker-compose down
echo    • Restart:   docker-compose restart
echo.

REM Try to open browser automatically
echo 🌐 Opening browser...
start http://localhost:5000

echo.
echo 💡 Keep this window open to see deployment status
echo 📝 Press any key to view application logs...
pause >nul

echo.
echo 📊 Application Logs ^(Press Ctrl+C to exit^):
echo ========================================================
docker-compose logs -f
