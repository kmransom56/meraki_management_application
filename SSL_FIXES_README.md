# 🔒 SSL Fixes for Cisco Meraki CLI

This directory now includes comprehensive SSL fix tools for corporate environments with SSL inspection (Zscaler, Blue Coat, Cisco Umbrella, etc.).

## 🚀 SSL Fixes Are Auto-Applied

The main CLI (`main.py`) now automatically applies SSL fixes when it starts up. You should see this message:
```
🔒 SSL fixes applied for corporate environment
```

## 📁 SSL Fix Files Added

- **`ssl_universal_fix.py`** - Main SSL fix module
- **`ssl_patch.py`** - Simple import for instant SSL fixes  
- **`SSL_MODULE_README.md`** - Detailed usage documentation
- **`SSL_TOOLKIT_GUIDE.md`** - Comprehensive guide with examples
- **`Install-SSLFix.ps1`** - PowerShell installer for other projects
- **`install_ssl_fix.bat`** - Batch installer for other projects
- **`ssl_fix_example.py`** - Example script showing usage
- **`test_meraki_api.py`** - Test script to verify API connectivity

## 🎯 Using SSL Fixes in Other Python Scripts

If you create additional Python scripts in this directory that need to make HTTPS requests:

### Method 1: Auto-Apply (Easiest)
```python
import ssl_patch  # Applies all SSL fixes instantly
import requests

# Now all HTTPS requests work
response = requests.get("https://api.example.com")
```

### Method 2: Full Control
```python
import ssl_universal_fix
ssl_universal_fix.apply_all_ssl_fixes(verbose=True)

# Your HTTPS code here
```

## 🧪 Testing SSL Fixes

Test that SSL fixes are working:
```bash
python ssl_universal_fix.py --test
```

Test Meraki API connectivity:
```bash
python test_meraki_api.py
```

## 📋 For Other Python Projects

To add SSL fixes to other Python projects, use the installer:

**PowerShell (Recommended):**
```powershell
.\Install-SSLFix.ps1 -TargetDir "C:\path\to\your\project" -Test
```

**Batch:**
```cmd
install_ssl_fix.bat
```

## ⚠️ Corporate Environment Notes

These SSL fixes are specifically designed for corporate environments where:
- SSL inspection is performed by trusted corporate infrastructure
- Zscaler, Blue Coat, or similar proxies are in use
- SSL certificate verification fails due to certificate replacement

The fixes should NOT be used on public internet or untrusted networks.

---

**Updated by:** GitHub Copilot  
**Date:** July 2025  
**Purpose:** Corporate SSL inspection compatibility
