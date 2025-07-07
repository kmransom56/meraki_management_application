# Enhanced Cisco Meraki CLI Launcher with SSL Fixes
# PowerShell version with better error handling

Write-Host "🚀 Starting Cisco Meraki CLI - Enhanced Edition" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Change to the CLI directory
Set-Location "C:\Users\keith.ransom\Utilities\cisco-meraki-cli"

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python or add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "❌ main.py not found in current directory" -ForegroundColor Red
    Write-Host "Please ensure you're in the correct directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if SSL fixes are available
if (Test-Path "ssl_patch.py") {
    Write-Host "🔒 SSL fixes available - corporate environment ready" -ForegroundColor Green
} else {
    Write-Host "⚠️ SSL fixes not found - you may see SSL warnings" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Launching CLI (SSL fixes auto-applied)..." -ForegroundColor Cyan

# Start the CLI (SSL fixes are auto-applied in main.py)
try {
    python main.py
} catch {
    Write-Host ""
    Write-Host "❌ The CLI encountered an error: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
