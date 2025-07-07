# Debug Guide for Meraki CLI Tool

## Quick Start Debugging

### 1. Test SSL Connectivity
```bash
python src/main.py --test-ssl
```

### 2. Run with Full Debug Output
```bash
python src/main.py --debug --verbose
```

### 3. Check API Key Configuration
```bash
# Copy .env.example to .env and add your API key
cp .env.example .env
# Edit .env file with your Meraki API key
```

## Common Issues and Solutions

### SSL Certificate Verification Errors

**Symptoms:**
- `SSL: CERTIFICATE_VERIFY_FAILED` errors
- API requests falling back to unverified connections

**Solutions:**
1. **Update Certificate Bundle:**
   ```bash
   pip install --upgrade certifi
   ```

2. **Check Network Connectivity:**
   ```bash
   python src/main.py --test-ssl
   ```

3. **Corporate Firewall Issues:**
   - Check if corporate firewall blocks SSL inspection
   - Try from different network
   - Contact IT department about Meraki API access

### API Request Failures

**Symptoms:**
- 404 errors for topology/links endpoint
- Empty device/client lists
- Authentication failures

**Solutions:**
1. **Verify API Key:**
   - Check API key is valid in Meraki Dashboard
   - Ensure API key has correct permissions

2. **Check Organization/Network Access:**
   - Verify you have access to the selected organization
   - Ensure network exists and is accessible

3. **Rate Limiting:**
   - Wait before retrying requests
   - Check API rate limits in logs

### Web Visualization Issues

**Symptoms:**
- No devices showing in web interface
- Blank topology visualization
- JavaScript errors in browser

**Solutions:**
1. **Check Browser Console:**
   - Open developer tools (F12)
   - Look for JavaScript errors in Console tab
   - Check Network tab for failed API requests

2. **Verify Data Loading:**
   - Visit http://localhost:5001/topology-data
   - Check if JSON data is returned
   - Look for error messages in response

3. **Clear Browser Cache:**
   - Hard refresh (Ctrl+F5)
   - Clear browser cache and cookies

## Debug Commands

### Test Individual Components
```bash
# Test SSL connectivity only
python src/main.py --test-ssl

# Run with debug logging
python src/main.py --debug

# Run with specific org/network (skip interactive selection)
python src/main.py --org-id YOUR_ORG_ID --network-id YOUR_NETWORK_ID

# Run unit tests
python -m pytest tests/ -v
```

### Check Logs
```bash
# View API logs
tail -f logs/api.log

# View SSL logs  
tail -f logs/ssl.log

# View web application logs
tail -f logs/web.log
```

## Troubleshooting Steps

### 1. Environment Check
- [ ] Python 3.7+ installed
- [ ] All dependencies installed from requirements.txt
- [ ] .env file created with valid API key
- [ ] Network connectivity to api.meraki.com

### 2. SSL/TLS Check
- [ ] SSL test passes: `python src/main.py --test-ssl`
- [ ] Certificate bundle is up to date
- [ ] No corporate firewall interference

### 3. API Access Check
- [ ] API key is valid and active
- [ ] Organization access is granted
- [ ] Network permissions are correct
- [ ] Rate limits not exceeded

### 4. Web Interface Check
- [ ] Flask server starts without errors
- [ ] Browser can access http://localhost:5001
- [ ] /topology-data endpoint returns valid JSON
- [ ] No JavaScript errors in browser console

## Getting Help

### Log Analysis
When reporting issues, include:
1. Full error messages from console
2. Relevant log files (logs/api.log, logs/ssl.log)
3. Browser console errors (if web interface issue)
4. Network/organization details (without sensitive data)

### Useful Debug Information
```bash
# System information
python --version
pip list

# SSL diagnostics
python -c "import ssl; print(ssl.get_default_verify_paths())"
python -c "import certifi; print(certifi.where())"

# Network connectivity
ping api.meraki.com
curl -I https://api.meraki.com/api/v1/organizations
```
