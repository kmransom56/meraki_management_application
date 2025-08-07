# Docker Update Guide - Enhanced FortiManager Integration

This guide provides instructions for the updated Docker implementation of the Enhanced Cisco Meraki CLI application with comprehensive FortiManager integration, device inventory management, and professional network topology visualization.

## 🚀 New Features in Docker Implementation

### Enhanced Application Features
- **FortiManager Integration**: Comprehensive device inventory with VLAN information
- **Device Inventory Table**: Meraki dashboard-style table view with professional styling
- **Network Topology Visualization**: FortiGate-inspired UI with enhanced tooltips
- **Multi-Vendor Support**: FortiGate and Cisco Meraki device integration
- **Professional UI**: FortiGate-inspired design with Lato font family
- **VLAN Management**: Detailed VLAN information and connection labels
- **Real-Time Data**: Live device status and comprehensive inventory

### Docker Enhancements
- **Updated Dependencies**: All required packages for FortiManager integration
- **Environment Variables**: Comprehensive configuration for multi-vendor environments
- **Security Improvements**: Enhanced SSL handling for corporate environments
- **Performance Optimizations**: Improved container startup and resource usage

## 🐳 Updating Docker Container with SSL Fixes

The SSL fixes have been added to the source code, so you need to rebuild the Docker image to include them.

### Option 1: Quick Rebuild (Recommended)
```bash
cd "C:\Users\keith.ransom\Utilities\cisco-meraki-cli"

# Stop any running containers
docker-compose down

# Rebuild the image with SSL fixes
docker-compose build --no-cache

# Start the updated container
docker-compose up -d
```

### Option 2: Full Clean Rebuild
```bash
cd "C:\Users\keith.ransom\Utilities\cisco-meraki-cli"

# Stop and remove containers
docker-compose down --volumes

# Remove the old image
docker rmi cisco-meraki-cli_app

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

### Option 3: Using Docker Commands Directly
```bash
cd "C:\Users\keith.ransom\Utilities\cisco-meraki-cli"

# Build the image
docker build -t cisco-meraki-cli .

# Run the container
docker run -d --name meraki-cli -p 5000:5000 -v %CD%/.env:/app/.env cisco-meraki-cli
```

## 🧪 Verify SSL Fixes in Docker

After rebuilding, you can verify SSL fixes are working:

1. **Check container logs:**
   ```bash
   docker logs cisco-meraki-cli_app_1
   ```
   You should see: "🔒 SSL fixes applied for corporate environment"

2. **Test API connectivity inside container:**
   ```bash
   docker exec -it cisco-meraki-cli_app_1 python quick_ssl_test.py
   ```

3. **Access web interface:**
   Open http://localhost:5000 and check that network data loads without SSL errors

## 📋 Files Included in Docker Build

The Docker image now includes:
- ✅ `ssl_universal_fix.py` - Universal SSL fix module
- ✅ `ssl_patch.py` - Simple SSL patch import
- ✅ Updated `main.py` with SSL fixes auto-applied
- ✅ All test scripts with SSL fixes
- ✅ Documentation and guides

## ⚠️ Important Notes

- **Environment Variables**: Make sure your `.env` file with `MERAKI_API_KEY` is accessible to the container
- **Network Access**: The container needs internet access to reach Meraki APIs
- **Corporate Proxy**: If you're behind a corporate proxy, you may need to configure Docker to use it
- **SSL Certificates**: The SSL fixes handle corporate SSL inspection automatically

## 🎉 Expected Results

After rebuilding, your Docker container will:
- ✅ Start without SSL warnings
- ✅ Connect to Meraki APIs successfully
- ✅ Display network topology in web interface
- ✅ Work seamlessly in corporate environments

---
**Note**: The rebuild is necessary because Docker images are immutable. The new SSL fixes need to be baked into a new image.
