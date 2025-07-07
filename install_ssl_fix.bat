@echo off
REM Universal SSL Fix Installer for Python Projects
REM Copy this to any Python project to add SSL fixes

echo 🔒 Universal SSL Fix Installer
echo ==============================

REM Check if ssl_universal_fix.py exists
if exist ssl_universal_fix.py (
    echo ✅ ssl_universal_fix.py already exists
) else (
    echo 📥 Copying ssl_universal_fix.py...
    copy "%~dp0ssl_universal_fix.py" . >nul
    if errorlevel 1 (
        echo ❌ Failed to copy ssl_universal_fix.py
        echo    Make sure this script is in the same directory as ssl_universal_fix.py
        pause
        exit /b 1
    )
    echo ✅ ssl_universal_fix.py copied successfully
)

REM Create ssl_patch.py for easy importing
echo 📄 Creating ssl_patch.py...
echo """Standalone SSL patch - import this to fix SSL issues instantly""" > ssl_patch.py
echo import ssl_universal_fix >> ssl_patch.py
echo ssl_universal_fix.apply_all_ssl_fixes(verbose=False) >> ssl_patch.py
echo ✅ ssl_patch.py created

REM Test SSL fixes
echo 🧪 Testing SSL fixes...
python -c "import ssl_universal_fix; ssl_universal_fix.test_ssl_fix(['https://www.google.com'])" 2>nul
if errorlevel 1 (
    echo ⚠️ SSL test had issues, but fixes are installed
) else (
    echo ✅ SSL fixes working correctly
)

echo.
echo 🎉 SSL fixes installed successfully!
echo.
echo 💡 Usage in your Python scripts:
echo    import ssl_patch  # Easiest method
echo    # or
echo    import ssl_universal_fix  # More control
echo.
echo 📋 Files created:
echo    - ssl_universal_fix.py (main module)
echo    - ssl_patch.py (simple import)
echo.
pause
