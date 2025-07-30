@echo off
echo.
echo ==========================================
echo   Cisco Meraki CLI - Web Interface
echo ==========================================
echo.
echo Starting web interface...
echo.

REM Check if Docker container is running
docker ps | findstr cisco-meraki-cli-app >nul
if %errorlevel% neq 0 (
    echo Starting Docker container...
    docker-compose up -d
    timeout /t 5 /nobreak >nul
)

echo.
echo Web interface will be available at:
echo   http://localhost:5002
echo.
echo Starting web CLI interface...
docker exec cisco-meraki-cli-app python web_cli.py

pause
