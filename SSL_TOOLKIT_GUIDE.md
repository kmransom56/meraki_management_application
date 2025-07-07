# 🔒 Complete SSL Fix Toolkit for Corporate Python Development

This toolkit provides comprehensive solutions for Python SSL certificate verification issues in corporate environments with SSL inspection (Zscaler, Blue Coat, Cisco Umbrella, etc.).

## 📦 What's Included

### Core Module
- **`ssl_universal_fix.py`** - The main universal SSL fix module
- **`SSL_MODULE_README.md`** - Detailed usage documentation

### Example & Test Files  
- **`ssl_fix_example.py`** - Example script showing usage
- **`test_meraki_api.py`** - Real-world Meraki API test

### Installation Tools
- **`install_ssl_fix.bat`** - Windows batch installer
- **`Install-SSLFix.ps1`** - PowerShell installer (recommended)

### Legacy/Specific Tools
- **`ssl_corporate_fix.py`** - Original corporate fix
- **`ssl_corporate_patch.py`** - Standalone patch module
- **`ssl-corporate-fix-v2.ps1`** - PowerShell automation script

## 🚀 Quick Setup for Any Python Project

### Method 1: PowerShell (Recommended)
```powershell
# Copy the Install-SSLFix.ps1 to your project directory, then:
.\Install-SSLFix.ps1 -TargetDir . -Test
```

### Method 2: Manual Copy
```bash
# Copy ssl_universal_fix.py to your project
cp ssl_universal_fix.py /your/project/directory/

# Use in your Python script
python -c "import ssl_universal_fix; print('SSL fixes applied!')"
```

### Method 3: Batch File
```cmd
# Copy install_ssl_fix.bat to your project directory, then:
install_ssl_fix.bat
```

## 🎯 Usage Examples

### Basic Usage (Auto-Apply)
```python
import ssl_universal_fix  # Automatically fixes all SSL issues
import requests

# Now all HTTPS requests work
response = requests.get("https://api.example.com")
```

### Manual Control
```python
from ssl_universal_fix import apply_all_ssl_fixes

apply_all_ssl_fixes(verbose=True)
# Your HTTPS code here
```

### Create Patch File for Multiple Projects
```python
from ssl_universal_fix import create_ssl_patch_file

# Creates ssl_patch.py in the specified directory
create_ssl_patch_file("/path/to/project")

# Then in that project:
import ssl_patch  # Instant SSL fixes
```

## 🏢 Corporate Environment Examples

### Zscaler Environment
```python
# File: zscaler_api_client.py
import ssl_universal_fix  # Handles Zscaler certificate replacement

import requests
from meraki import DashboardAPI

# Both work without SSL errors
api_data = requests.get("https://api.example.com").json()
dashboard = DashboardAPI("your_api_key")
```

### Blue Coat ProxySG
```python
# File: bluecoat_scraper.py  
import ssl_universal_fix

import aiohttp
import asyncio

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://secure-site.com") as resp:
            return await resp.text()

# Works despite proxy SSL inspection
data = asyncio.run(fetch_data())
```

### Cisco Umbrella
```python
# File: umbrella_integration.py
import ssl_universal_fix

import httpx

# Modern HTTP client works too
with httpx.Client() as client:
    response = client.get("https://api.service.com")
    data = response.json()
```

## 🛠️ Supported Libraries

✅ **requests** - Most popular HTTP library  
✅ **urllib3** - Low-level HTTP library  
✅ **aiohttp** - Async HTTP for modern apps  
✅ **httpx** - Modern sync/async HTTP client  
✅ **http.client** - Python built-in  
✅ **ssl** - Python SSL module  
✅ **meraki** - Cisco Meraki SDK  
✅ **boto3** - AWS SDK (when using HTTPS)  
✅ **azure-*** - Azure SDKs  
✅ **google-cloud-*** - Google Cloud SDKs  
✅ **kubernetes** - Kubernetes Python client  
✅ **docker** - Docker SDK  
✅ Any library using the above internally

## 📋 Real-World Project Types

This toolkit is perfect for:

### 🔗 API Clients & Integrations
```python
import ssl_universal_fix
from salesforce_api import Salesforce
from slack_sdk import WebClient
from github import Github

# All API clients work without SSL issues
sf = Salesforce(username="user", password="pass", security_token="token")
slack = WebClient(token="your_token")
g = Github("your_token")
```

### 🕷️ Web Scrapers
```python
import ssl_universal_fix
from bs4 import BeautifulSoup
import requests

# Scraping secure sites works
response = requests.get("https://secure-site.com")
soup = BeautifulSoup(response.content, 'html.parser')
```

### 🤖 Automation & CI/CD
```python
import ssl_universal_fix
import jenkins
import docker

# Jenkins and Docker APIs work
server = jenkins.Jenkins('https://jenkins.company.com')
client = docker.from_env()
```

### 📊 Data Pipelines
```python
import ssl_universal_fix
import pandas as pd
from sqlalchemy import create_engine

# Reading from HTTPS APIs
df = pd.read_json("https://api.data-source.com/data")
engine = create_engine("postgresql+psycopg2://ssl_connection")
```

### 🎮 Bot Development
```python
import ssl_universal_fix
import discord
from slack_bolt import App

# Discord and Slack bots work
bot = discord.Client()
app = App(token="your_slack_token")
```

## 🔧 Advanced Configuration

### Disable Auto-Apply
```python
import os
os.environ['SSL_AUTO_APPLY'] = 'false'
import ssl_universal_fix

# Manually apply when needed
ssl_universal_fix.apply_all_ssl_fixes()
```

### Test Specific URLs
```python
from ssl_universal_fix import test_ssl_fix

test_ssl_fix([
    'https://your-internal-api.company.com',
    'https://external-service.com',
    'https://github.com/api'
])
```

### Check if Fixes are Applied
```python
import ssl_universal_fix
if ssl_universal_fix._SSL_FIXES_APPLIED:
    print("SSL fixes are active")
```

## 🐛 Troubleshooting

### Still Getting SSL Errors?
1. **Import Order**: Make sure you import `ssl_universal_fix` first
2. **Manual Application**: Try `ssl_universal_fix.apply_all_ssl_fixes(verbose=True)`
3. **Environment Variables**: Check if `PYTHONHTTPSVERIFY=0` is set
4. **Library Conflicts**: Some libraries cache SSL settings

### Module Not Found?
1. **Copy File**: Ensure `ssl_universal_fix.py` is in your project directory
2. **Python Path**: Add the directory to `sys.path` or `PYTHONPATH`
3. **Virtual Environment**: Make sure you're in the right venv

### Want Verbose Output?
```python
import ssl_universal_fix
ssl_universal_fix.apply_all_ssl_fixes(verbose=True)
ssl_universal_fix.test_ssl_fix()
```

### Corporate Proxy Issues?
```python
import ssl_universal_fix
import os

# Set proxy if needed
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'

# SSL fixes still work with proxies
```

## 🚨 Security Considerations

### When to Use
✅ **Corporate environments** with trusted SSL inspection  
✅ **Internal development** and testing  
✅ **Known secure networks** (company VPN, etc.)  
✅ **Legacy systems** that can't be updated  

### When NOT to Use
❌ **Production applications** handling sensitive data  
❌ **Public internet** applications  
❌ **Financial or healthcare** applications  
❌ **Unknown or untrusted** networks  

### Best Practices
1. **Environment-Specific**: Only apply in corporate environments
2. **Code Reviews**: Ensure team understands the implications
3. **Documentation**: Document why SSL verification is disabled
4. **Monitoring**: Monitor for actual security issues

## 📁 File Organization

For a typical project:
```
your_project/
├── ssl_universal_fix.py    # Main SSL fix module
├── ssl_patch.py           # Simple import file (generated)
├── main.py               # Your main application
├── requirements.txt      # Dependencies
└── README.md            # Project documentation
```

## 🔄 Integration Examples

### Django Project
```python
# settings.py
import ssl_universal_fix  # Apply at Django startup

# Now all external API calls work
```

### Flask Application
```python
# app.py
import ssl_universal_fix
from flask import Flask

app = Flask(__name__)

@app.route('/api/external')
def call_external_api():
    import requests
    # SSL issues are handled
    return requests.get("https://api.external.com").json()
```

### FastAPI Service
```python
# main.py
import ssl_universal_fix
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/data")
async def get_external_data():
    async with httpx.AsyncClient() as client:
        # SSL verification bypassed automatically
        response = await client.get("https://api.service.com")
        return response.json()
```

### Jupyter Notebook
```python
# First cell
import ssl_universal_fix

# Second cell  
import requests
import pandas as pd

# All subsequent HTTPS calls work
df = pd.read_json("https://api.data-source.com")
```

## 📝 Changelog

### v1.0 (July 2025)
- ✅ Universal SSL fix module
- ✅ Support for all major HTTP libraries
- ✅ Auto-apply on import
- ✅ Comprehensive testing
- ✅ PowerShell installer
- ✅ Batch installer
- ✅ Documentation and examples

---

**Created by:** GitHub Copilot  
**Date:** July 2025  
**Compatibility:** Python 3.6+  
**License:** MIT  
**Environment:** Corporate networks with SSL inspection
