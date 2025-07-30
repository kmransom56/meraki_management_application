@echo off
title Cisco Meraki Web Management - Deployment Validation
color 0B
cls

echo.
echo ========================================================
echo   🔍 Cisco Meraki Web Management - Deployment Validation
echo ========================================================
echo.

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not running!
    goto :end
)
echo ✅ Docker is running!

REM Check if container is running
echo.
echo 🔍 Checking container status...
docker ps --filter "name=cisco-meraki-web-app" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr cisco-meraki-web-app >nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Container is not running!
    echo 💡 Run DEPLOY.bat to start the application
    goto :end
)
echo ✅ Container is running!

REM Check if web interface is responding
echo.
echo 🔍 Testing web interface...
curl -s -o nul -w "%%{http_code}" http://localhost:5000 | findstr "200" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Web interface not responding on port 5000
    echo 💡 Container may still be starting up...
    echo 💡 Wait 1-2 minutes and try again
    goto :logs
)
echo ✅ Web interface is responding!

REM All checks passed
echo.
echo ========================================================
echo   🎉 VALIDATION SUCCESSFUL!
echo ========================================================
echo.
echo ✅ Docker is running
echo ✅ Container is healthy  
echo ✅ Web interface is accessible
echo.
echo 🌐 Access your application at: http://localhost:5000
echo.
goto :end

:logs
echo.
echo 📊 Recent application logs:
echo ----------------------------------------
docker-compose logs --tail=20 cisco-meraki-web
echo ----------------------------------------
echo.

:end
echo 📝 Press any key to exit...
pause >nul
