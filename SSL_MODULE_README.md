# Universal SSL Fix Module 🔒

A comprehensive Python module to suppress SSL certificate verification errors in corporate environments with SSL inspection (Zscaler, Blue Coat, etc.).

## 🚀 Quick Start

### Method 1: Auto-Apply (Easiest)
Simply import the module at the top of your Python script:
```python
import ssl_universal_fix  # Automatically applies all SSL fixes
import requests

# Now all HTTPS requests work without SSL errors
response = requests.get("https://api.github.com")
```

### Method 2: Manual Control
```python
from ssl_universal_fix import apply_all_ssl_fixes

# Apply fixes with verbose output
apply_all_ssl_fixes(verbose=True)

# Your HTTPS code here
import requests
response = requests.get("https://example.com")
```

### Method 3: Environment Variable Control
```python
import os
os.environ['SSL_AUTO_APPLY'] = 'false'  # Disable auto-apply
import ssl_universal_fix

# Manually apply when needed
ssl_universal_fix.apply_all_ssl_fixes()
```

## 📦 Installation

1. Copy `ssl_universal_fix.py` to your project directory
2. Import it in your Python scripts
3. That's it! No pip install needed.

## 🎯 Supported Libraries

This module automatically configures:
- ✅ **requests** - Most common HTTP library
- ✅ **urllib3** - Low-level HTTP library  
- ✅ **aiohttp** - Async HTTP library
- ✅ **httpx** - Modern HTTP library
- ✅ **http.client** - Built-in HTTP client
- ✅ **ssl** - Python's SSL module
- ✅ **meraki** - Cisco Meraki SDK
- ✅ Any library using the above

## 🛠️ Command Line Usage

Test SSL fixes:
```bash
python ssl_universal_fix.py --test
```

Create a patch file for other projects:
```bash
python ssl_universal_fix.py --create-patch /path/to/project
```

Apply fixes silently:
```bash
python ssl_universal_fix.py --quiet
```

## 📁 Use in Multiple Projects

### Option 1: Copy the file
Copy `ssl_universal_fix.py` to each project and import it.

### Option 2: Create a patch file
```bash
cd /your/project/directory
python /path/to/ssl_universal_fix.py --create-patch .
```

This creates `ssl_patch.py` in your project. Then just:
```python
import ssl_patch  # Applies fixes instantly
```

### Option 3: Environment variable
Add to your system/project environment:
```bash
export PYTHONPATH="/path/to/ssl_universal_fix/directory:$PYTHONPATH"
```

Then import from anywhere:
```python
import ssl_universal_fix
```

## 🔧 Advanced Usage

### Test specific URLs
```python
from ssl_universal_fix import test_ssl_fix

test_ssl_fix([
    'https://your-api.com',
    'https://another-service.com'
])
```

### Disable auto-apply for specific scripts
```python
import os
os.environ['SSL_AUTO_APPLY'] = 'false'
import ssl_universal_fix

# SSL fixes won't be applied automatically
# Apply manually when needed:
ssl_universal_fix.apply_all_ssl_fixes()
```

### Check if fixes are applied
```python
import ssl_universal_fix
print(ssl_universal_fix._SSL_FIXES_APPLIED)  # True if applied
```

## 🏢 Corporate Environment Examples

### Zscaler
```python
import ssl_universal_fix  # Handles Zscaler SSL inspection
import requests

# Works despite Zscaler certificate replacement
data = requests.get("https://api.example.com").json()
```

### Blue Coat ProxySG
```python
import ssl_universal_fix  # Handles Blue Coat SSL inspection
from meraki import DashboardAPI

# Meraki SDK works without SSL errors
dashboard = DashboardAPI(api_key="your_key")
orgs = dashboard.organizations.getOrganizations()
```

### Cisco Umbrella
```python
import ssl_universal_fix  # Handles Umbrella SSL filtering
import aiohttp

# Async requests work too
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.service.com") as resp:
        data = await resp.json()
```

## ⚠️ Security Note

This module disables SSL certificate verification, which reduces security. Only use in trusted corporate environments where SSL inspection is performed by your organization's security infrastructure.

## 🐛 Troubleshooting

### Still getting SSL errors?
1. Make sure you import `ssl_universal_fix` before other libraries
2. Try manual application: `ssl_universal_fix.apply_all_ssl_fixes(verbose=True)`
3. Check environment variables: `echo $PYTHONHTTPSVERIFY`

### Module not found?
1. Ensure `ssl_universal_fix.py` is in the same directory as your script
2. Or add the directory to your Python path
3. Or use the patch file method

### Want to see what's happening?
```python
import ssl_universal_fix
ssl_universal_fix.apply_all_ssl_fixes(verbose=True)
ssl_universal_fix.test_ssl_fix()
```

## 📋 Example Projects

This module is perfect for:
- 🔗 **API clients** (REST APIs, GraphQL, etc.)
- 🕷️ **Web scrapers** (BeautifulSoup, Scrapy, etc.)  
- 🤖 **Automation scripts** (CI/CD, monitoring, etc.)
- 📊 **Data pipelines** (ETL, data fetching, etc.)
- 🎮 **Discord/Slack bots** (API interactions)
- 🔄 **Integration scripts** (Webhooks, API sync, etc.)

## 🚀 Real-World Example

Here's a complete example for a Meraki topology script:

```python
#!/usr/bin/env python3
"""
Meraki Network Topology Fetcher
Works in corporate environments with SSL inspection
"""

# Fix SSL issues first
import ssl_universal_fix

# Now import your libraries
import requests
import json
from meraki import DashboardAPI

def get_network_topology(api_key, org_id):
    """Fetch network topology data"""
    dashboard = DashboardAPI(api_key)
    
    # These calls work without SSL errors
    networks = dashboard.organizations.getOrganizationNetworks(org_id)
    devices = dashboard.organizations.getOrganizationDevices(org_id)
    
    return {
        'networks': networks,
        'devices': devices
    }

if __name__ == "__main__":
    api_key = "your_meraki_api_key"
    org_id = "your_org_id"
    
    topology = get_network_topology(api_key, org_id)
    print(f"Found {len(topology['networks'])} networks")
    print(f"Found {len(topology['devices'])} devices")
```

---

**Created by:** GitHub Copilot  
**Date:** July 2025  
**License:** MIT  
**Compatibility:** Python 3.6+
