# Universal SSL Fix Installer for Python Projects
# PowerShell version - more robust than batch

param(
    [string]$TargetDir = ".",
    [switch]$Test,
    [switch]$Quiet
)

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    
    if ($Quiet) { return }
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor Green }
        "Warning" { Write-Host "⚠️ $Message" -ForegroundColor Yellow }
        "Error"   { Write-Host "❌ $Message" -ForegroundColor Red }
        "Info"    { Write-Host "📋 $Message" -ForegroundColor Cyan }
        default   { Write-Host $Message }
    }
}

function Install-SSLFix {
    param([string]$TargetDir)
    
    Write-Status "Universal SSL Fix Installer" "Info"
    Write-Status "==============================" "Info"
    
    # Get the directory where this script is located
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $SourceFile = Join-Path $ScriptDir "ssl_universal_fix.py"
    $TargetFile = Join-Path $TargetDir "ssl_universal_fix.py"
    $PatchFile = Join-Path $TargetDir "ssl_patch.py"
    
    # Check if source file exists
    if (-not (Test-Path $SourceFile)) {
        Write-Status "ssl_universal_fix.py not found in script directory" "Error"
        Write-Status "Make sure this script is in the same directory as ssl_universal_fix.py" "Error"
        return $false
    }
    
    # Create target directory if it doesn't exist
    if (-not (Test-Path $TargetDir)) {
        Write-Status "Creating directory: $TargetDir" "Info"
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    
    # Copy ssl_universal_fix.py
    if (Test-Path $TargetFile) {
        Write-Status "ssl_universal_fix.py already exists in target directory" "Warning"
    } else {
        Write-Status "Copying ssl_universal_fix.py to $TargetDir..." "Info"
        try {
            Copy-Item $SourceFile $TargetFile -Force
            Write-Status "ssl_universal_fix.py copied successfully" "Success"
        } catch {
            Write-Status "Failed to copy ssl_universal_fix.py: $_" "Error"
            return $false
        }
    }
    
    # Create ssl_patch.py
    Write-Status "Creating ssl_patch.py..." "Info"
    $patchContent = @"
"""
Standalone SSL patch - import this to fix SSL issues instantly
"""
import ssl_universal_fix
ssl_universal_fix.apply_all_ssl_fixes(verbose=False)
"@
    
    try {
        $patchContent | Out-File -FilePath $PatchFile -Encoding UTF8 -Force
        Write-Status "ssl_patch.py created" "Success"
    } catch {
        Write-Status "Failed to create ssl_patch.py: $_" "Error"
        return $false
    }
    
    return $true
}

function Test-SSLFix {
    param([string]$TargetDir)
    
    Write-Status "Testing SSL fixes..." "Info"
    
    $testScript = @"
import sys
sys.path.insert(0, '$($TargetDir.Replace('\', '\\'))')
try:
    import ssl_universal_fix
    ssl_universal_fix.test_ssl_fix(['https://www.google.com'])
    print('SSL_TEST_SUCCESS')
except Exception as e:
    print(f'SSL_TEST_ERROR: {e}')
"@
    
    try {
        $result = python -c $testScript 2>&1
        if ($result -match "SSL_TEST_SUCCESS") {
            Write-Status "SSL fixes working correctly" "Success"
            return $true
        } else {
            Write-Status "SSL test had issues: $result" "Warning"
            return $false
        }
    } catch {
        Write-Status "Could not test SSL fixes: $_" "Warning"
        return $false
    }
}

function Show-Usage {
    if ($Quiet) { return }
    
    Write-Status "" "Info"
    Write-Status "🎉 SSL fixes installed successfully!" "Success"
    Write-Status "" "Info"
    Write-Status "💡 Usage in your Python scripts:" "Info"
    Write-Host "   import ssl_patch  # Easiest method"
    Write-Host "   # or"
    Write-Host "   import ssl_universal_fix  # More control"
    Write-Status "" "Info"
    Write-Status "📋 Files created:" "Info"
    Write-Host "   - ssl_universal_fix.py (main module)"
    Write-Host "   - ssl_patch.py (simple import)"
    Write-Status "" "Info"
}

# Main execution
try {
    $success = Install-SSLFix -TargetDir $TargetDir
    
    if ($success) {
        if ($Test) {
            Test-SSLFix -TargetDir $TargetDir | Out-Null
        }
        Show-Usage
    }
    
    if (-not $Quiet) {
        Write-Host "Press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
} catch {
    Write-Status "Installation failed: $_" "Error"
    exit 1
}
