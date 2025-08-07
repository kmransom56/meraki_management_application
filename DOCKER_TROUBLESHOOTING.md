# Docker Troubleshooting Guide - AI-Powered Network Management

## Issue: Docker Build Hanging or Freezing

### Problem Description
The `docker-compose build --no-cache` command hangs up and freezes, preventing the AI-powered application from being containerized.

### Root Cause Analysis
Based on the error messages:
- Docker Desktop Linux Engine is not accessible
- Server returns 500 Internal Server Error
- Docker daemon is not running properly

### Solution Steps

#### 1. Restart Docker Desktop
```bash
# Close Docker Desktop completely
# Restart Docker Desktop from Windows Start Menu
# Wait for Docker Desktop to fully initialize (green icon in system tray)
```

#### 2. Alternative: Run Application Directly with Python
While Docker issues are resolved, you can run the AI-powered application directly:

```bash
# Navigate to project directory
cd c:\Users\keith.ransom\Utilities\cisco-meraki-cli

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the AI-powered application directly
python app.py
```

#### 3. Docker Desktop Troubleshooting
If Docker Desktop continues to have issues:

**Option A: Reset Docker Desktop**
1. Open Docker Desktop
2. Go to Settings → Troubleshoot
3. Click "Reset to factory defaults"
4. Restart Docker Desktop

**Option B: Switch Docker Engine**
1. Open Docker Desktop Settings
2. Go to General
3. Try switching between WSL 2 and Hyper-V backends
4. Apply & Restart

**Option C: Check Windows Services**
1. Open Services (services.msc)
2. Ensure these services are running:
   - Docker Desktop Service
   - com.docker.service

#### 4. Lightweight Docker Build (When Docker is Working)
Instead of `--no-cache`, try incremental build:

```bash
# Build without cache clearing (faster)
docker-compose build

# Or build specific service only
docker-compose build cisco-meraki-cli

# Alternative: Use docker build directly
docker build -t cisco-meraki-cli-enhanced .
```

#### 5. Docker Build Optimization
To prevent future hanging issues, the Dockerfile has been optimized with:
- Multi-stage builds for faster compilation
- Layer caching for dependencies
- Reduced image size with slim base images
- Proper cleanup of temporary files

### Testing the AI-Powered Application

#### Direct Python Execution
```bash
# Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set AI_MAINTENANCE_ENABLED=true

# Run the application
python app.py
```

#### Access AI Features
Once running, access these URLs:
- **Main Application**: http://localhost:5000
- **Network Topology**: http://localhost:5000/visualization
- **AI Maintenance Dashboard**: http://localhost:5000/ai-maintenance
- **Health Check**: http://localhost:5000/health

### AI Maintenance Engine Features Available

#### Real-time Monitoring
- Continuous health monitoring of APIs and devices
- Performance metrics tracking
- Automated issue detection

#### Professional Dashboard
- Live system health indicators
- Issue management interface
- Performance trend analysis
- AI control panel

#### Auto-Fix Capabilities
- API connectivity restoration
- Performance optimization
- Device reconnection attempts
- System health maintenance

### Environment Configuration

Create a `.env` file for local development:
```bash
# AI Maintenance Engine
AI_MAINTENANCE_ENABLED=true
AI_MAINTENANCE_CHECK_INTERVAL=30
AI_MAINTENANCE_AUTO_FIX=true

# FortiManager Integration
FORTIMANAGER_HOST=your-fortimanager-host
FORTIMANAGER_USERNAME=your-username
FORTIMANAGER_PASSWORD=your-password

# Meraki API
MERAKI_API_KEY=your-meraki-api-key
MERAKI_ORG_ID=your-org-id

# Security
SSL_VERIFY=false
SECRET_KEY=your-secret-key
```

### Next Steps

1. **Immediate**: Run the application directly with Python to test AI features
2. **Short-term**: Resolve Docker Desktop connectivity issues
3. **Long-term**: Deploy using the optimized Docker configuration

### Support and Monitoring

The AI maintenance engine provides:
- **Self-diagnostics**: Built-in health checks and monitoring
- **Automated recovery**: Many issues resolve automatically
- **Professional logging**: Comprehensive audit trail
- **Performance optimization**: Continuous system tuning

### Contact Information

If issues persist:
1. Check the AI maintenance dashboard for system health
2. Review application logs for detailed error information
3. Use the health check endpoint for quick status verification

The AI-powered network management platform is designed to be resilient and self-healing, providing enterprise-grade reliability even when deployment challenges occur.
