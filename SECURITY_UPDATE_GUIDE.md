# Security Update Guide for Cisco Meraki CLI

## 🚨 GitHub Security Alerts

GitHub has detected 7 vulnerabilities in the repository dependencies (4 high, 3 moderate).

## 🔧 Quick Security Fixes

### Step 1: Update Core Dependencies
```bash
pip install --upgrade requests urllib3 certifi setuptools wheel pip
```

### Step 2: Update All Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Step 3: Update Docker Dependencies
If using Docker, rebuild the container:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📋 Common Vulnerable Packages to Update

Based on typical Python security alerts:

### High Priority Updates
- **requests** - HTTP library security fixes
- **urllib3** - SSL/TLS security improvements  
- **certifi** - Certificate bundle updates
- **setuptools** - Package installation security
- **cryptography** - Encryption library updates

### Moderate Priority Updates
- **Pillow** - Image processing security
- **Jinja2** - Template engine fixes
- **tornado** - Web framework security

## 🛡️ Automated Security Updates

### Option 1: Use Dependabot (Recommended)
1. Go to repository Settings → Security & analysis
2. Enable "Dependabot security updates"
3. Enable "Dependabot version updates"

### Option 2: Manual Updates
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Update all packages
pip install --upgrade pip
pip install --upgrade -r requirements.txt
pip freeze > requirements-updated.txt
```

## 🧪 Testing After Updates

After updating dependencies, test the CLI:

```bash
# Test SSL fixes
python quick_ssl_test.py

# Test API connectivity
python test_meraki_api.py

# Test pagination
python test_pagination.py

# Test main CLI
python main.py
```

## 📊 Monitoring Security

### Regular Maintenance
- Check for updates monthly: `pip list --outdated`
- Monitor GitHub security alerts
- Update Docker base images regularly
- Review dependency changes in pull requests

### Security Best Practices
- Use virtual environments
- Pin dependency versions in production
- Regularly update SSL certificates
- Monitor for security advisories

## 🔄 Automated Update Script

Create `update-dependencies.py`:
```python
import subprocess
import sys

def update_dependencies():
    packages = [
        'requests', 'urllib3', 'certifi', 'setuptools', 
        'cryptography', 'Pillow', 'Jinja2'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package])
            print(f"✅ Updated {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to update {package}")

if __name__ == "__main__":
    update_dependencies()
```

## 📞 Support

If you encounter issues after updates:
1. Check the DEBUG_GUIDE.md
2. Review error logs in `log/error.log`
3. Test with `emergency_fix.py` if needed
4. Revert to previous working versions if necessary

---
**Last Updated:** July 2025  
**Repository:** https://github.com/kmransom56/cisco-meraki-cli
