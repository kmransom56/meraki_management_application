# Enhanced Docker Setup Guide - FortiManager Integration

## 🚀 Overview

This Docker implementation provides a comprehensive network management solution with:
- **FortiManager Integration**: Complete device inventory and VLAN management
- **Meraki Dashboard Integration**: Multi-vendor network support
- **Professional UI**: FortiGate-inspired interface with tabbed views
- **Device Inventory Table**: Detailed device information in table format
- **Network Topology Visualization**: Interactive network diagrams

## 📋 Prerequisites

- Docker and Docker Compose installed
- Access to FortiManager JSON-RPC API
- Cisco Meraki Dashboard API key
- Network connectivity to your FortiManager and Meraki systems

## 🔧 Quick Start

### 1. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp .env.docker .env
```

Edit `.env` with your actual values:

```bash
# FortiManager Configuration
FORTIMANAGER_HOST=your-fortimanager-host.example.com
FORTIMANAGER_USERNAME=your-username
FORTIMANAGER_PASSWORD=your-password

# Meraki Configuration
MERAKI_API_KEY=your-meraki-api-key
MERAKI_ORG_ID=your-organization-id

# Security Settings
SSL_VERIFY=false  # For corporate environments with SSL inspection
SECRET_KEY=your-secure-secret-key
```

### 2. Build and Run

```bash
# Build the enhanced container
docker-compose build --no-cache

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the Application

- **Web Interface**: http://localhost:5000
- **Network Topology**: Interactive network diagram with device details
- **Device Inventory**: Comprehensive table view with search and filtering

## 🌟 Features Available

### Network Topology View
- Interactive force-directed network diagram
- Hierarchical layout: Internet → FortiGate → Switch → AP → Clients
- Enhanced tooltips with comprehensive device information
- VLAN connection labels and device relationships
- Professional FortiGate-inspired styling

### Device Inventory Table
- Meraki dashboard-style table with all device details
- Status indicators with colored dots (online/offline/warning)
- Device type badges with category-specific colors
- VLAN assignments and parent device relationships
- Real-time search and filtering capabilities
- Sortable columns with comprehensive device information

### FortiManager Integration
- Complete device inventory from centralized FortiManager
- VLAN configuration and assignments
- Device status and interface information
- Connected devices from ARP/DHCP data
- Multi-site support for distributed environments

### Multi-Vendor Support
- FortiGate firewalls and FortiAP access points
- Cisco Meraki switches, access points, and appliances
- Unified device classification and management
- Cross-vendor VLAN and connection mapping

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FORTIMANAGER_HOST` | FortiManager hostname/IP | - |
| `FORTIMANAGER_USERNAME` | FortiManager API username | - |
| `FORTIMANAGER_PASSWORD` | FortiManager API password | - |
| `MERAKI_API_KEY` | Meraki Dashboard API key | - |
| `MERAKI_ORG_ID` | Meraki Organization ID | - |
| `SSL_VERIFY` | Enable SSL verification | false |
| `SECRET_KEY` | Flask secret key | - |
| `DEBUG` | Enable debug mode | false |

### Volume Mounts

- `./config:/app/config` - Configuration files
- `./logs:/app/logs` - Application logs
- `./data:/app/data` - Persistent data storage
- `./templates:/app/templates` - Custom templates
- `./static:/app/static` - Static assets

## 🛠️ Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   ```bash
   # Set SSL_VERIFY=false in .env for corporate environments
   SSL_VERIFY=false
   ```

2. **FortiManager Connection Issues**
   ```bash
   # Check FortiManager connectivity
   docker exec -it cisco-meraki-cli-enhanced python -c "
   from modules.fortigate.fortigate_api import FortiManagerAPI
   fm = FortiManagerAPI('your-host', 'username', 'password')
   print('Login successful:', fm.login())
   "
   ```

3. **Meraki API Issues**
   ```bash
   # Verify Meraki API key
   docker exec -it cisco-meraki-cli-enhanced python -c "
   import meraki
   dashboard = meraki.DashboardAPI('your-api-key')
   print('Organizations:', dashboard.organizations.getOrganizations())
   "
   ```

### Logs and Debugging

```bash
# View application logs
docker-compose logs -f cisco-meraki-cli

# Access container shell
docker exec -it cisco-meraki-cli-enhanced /bin/bash

# Check application status
docker-compose ps
```

## 🔄 Updating

To update to the latest version:

```bash
# Pull latest code
git pull origin main

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🎯 Production Deployment

### Security Considerations

1. **Environment Variables**: Use Docker secrets or external secret management
2. **SSL Certificates**: Configure proper SSL certificates for production
3. **Network Security**: Use Docker networks and firewall rules
4. **Resource Limits**: Set appropriate CPU and memory limits

### Example Production Configuration

```yaml
services:
  cisco-meraki-cli:
    build: .
    container_name: cisco-meraki-cli-prod
    restart: always
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - SSL_VERIFY=true
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review the troubleshooting section above
3. Verify network connectivity to FortiManager and Meraki
4. Ensure all environment variables are properly configured

## 🎉 Success Indicators

After successful deployment, you should see:
- ✅ Container starts without errors
- ✅ Web interface accessible at http://localhost:5000
- ✅ Network topology displays with device data
- ✅ Device inventory table shows comprehensive information
- ✅ FortiManager and Meraki data integration working
- ✅ Professional FortiGate-inspired UI rendering correctly
