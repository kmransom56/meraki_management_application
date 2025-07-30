# Multi-Vendor Network Topology Integration

## Overview

The Cisco Meraki Web Management Application now supports comprehensive multi-vendor network topology visualization, specifically designed for restaurant networks that combine Cisco Meraki and Fortinet infrastructure.

## Supported Vendors

### Cisco Meraki
- **Security Appliances (MX)** - Firewalls, routers, SD-WAN
- **Switches (MS)** - Network switches and PoE devices  
- **Access Points (MR)** - Wireless access points
- **Cameras (MV)** - Security cameras
- **Sensors (MT)** - Environmental sensors

### Fortinet
- **Fortigate Firewalls** - Next-generation firewalls
- **FortiAP Access Points** - Wireless access points managed by Fortigate
- **WiFi Clients** - Devices connected to FortiAP networks

## Features

### 🔧 **Device Configuration**
- **Fortigate Management** - Add multiple Fortigate firewalls by IP/hostname
- **API Token Authentication** - Secure FortiOS API integration
- **Connection Testing** - Verify connectivity to all configured devices
- **Device Naming** - Custom names for easy identification

### 🌐 **Unified Topology Generation**
- **Cross-Vendor Discovery** - Automatic device enumeration across vendors
- **Relationship Mapping** - Intelligent connection discovery between devices
- **Visual Differentiation** - Color-coded devices by vendor (Meraki=Blue, Fortinet=Orange)
- **Device Type Icons** - Appropriate icons for firewalls, APs, switches, clients

### 📊 **Comprehensive Statistics**
- **Device Counts** - Total devices by vendor and type
- **Client Statistics** - Connected clients across all access points
- **Connection Mapping** - Network relationships and topology links
- **Health Monitoring** - Status and performance metrics

### 🎨 **Interactive Visualization**
- **HTML Export** - Standalone interactive topology maps
- **D3.js Integration** - Professional network diagrams
- **Zoom and Pan** - Navigate large network topologies
- **Device Details** - Click for detailed device information

## Configuration Guide

### Step 1: Configure Fortinet Devices

1. **Navigate to Multi-Vendor Topology**
   - Open your Meraki Web Management Application
   - Click "Multi-Vendor Topology" in the navigation menu

2. **Add Fortigate Firewalls**
   - Enter Fortigate **Host/IP Address** (e.g., 192.168.1.1)
   - Provide **API Token** from FortiOS
   - Add **Device Name** for identification (e.g., "Restaurant Main Firewall")
   - Click "Add Fortigate"

3. **Test Connections**
   - Click "Test Connections" to verify API connectivity
   - Review connection status for each device
   - Troubleshoot any failed connections

### Step 2: Generate Multi-Vendor Topology

1. **Select Meraki Network**
   - Choose the target network from the dropdown
   - Ensure you have valid Meraki API access

2. **Generate Topology**
   - Click "Generate Multi-Vendor Topology"
   - Wait for device discovery and relationship mapping
   - Review the unified network visualization

3. **Export Interactive Visualization**
   - Click "Generate Interactive Visualization"
   - Open the exported HTML file for detailed analysis

## API Endpoints

### Fortinet Configuration
```
POST /api/fortinet/configure
Body: {
  "fortigates": [
    {
      "host": "192.168.1.1",
      "api_token": "your-api-token",
      "name": "Restaurant Firewall"
    }
  ]
}
```

### Connection Testing
```
POST /api/fortinet/test
Response: {
  "success": true,
  "results": [
    {
      "name": "Restaurant Firewall",
      "host": "192.168.1.1",
      "status": "connected"
    }
  ]
}
```

### Multi-Vendor Topology
```
GET /api/topology/multi-vendor/{network_id}?network_name=Network%20Name
Response: {
  "success": true,
  "topology": {
    "devices": [...],
    "clients": [...],
    "connections": [...]
  },
  "stats": {
    "total_devices": 15,
    "total_clients": 45,
    "total_connections": 12
  }
}
```

## Architecture

### Backend Components

#### `fortinet_api.py`
- **FortinetAPIManager** - Core API integration class
- **Device Discovery** - Fortigate and FortiAP enumeration
- **Status Monitoring** - Health and performance metrics
- **Client Tracking** - WiFi client management

#### `multi_vendor_topology.py`
- **MultiVendorTopologyEngine** - Unified topology builder
- **Cross-Vendor Mapping** - Device relationship discovery
- **HTML Generation** - Interactive visualization export
- **Statistics Calculation** - Network metrics and analytics

### Frontend Components

#### Multi-Vendor UI Section
- **Configuration Panel** - Fortinet device management
- **Network Selection** - Meraki network dropdown
- **Topology Display** - Unified device visualization
- **Statistics Dashboard** - Real-time network metrics

## Use Cases

### Restaurant Network Management
Perfect for restaurant chains using mixed vendor equipment:

- **Arby's Locations** - Meraki wireless + Fortigate security
- **BWW Restaurants** - Unified view of all network infrastructure
- **Multi-Site Management** - Consistent topology across locations
- **Troubleshooting** - Complete network visibility for faster issue resolution

### Enterprise Scenarios
- **Branch Office Networks** - Mixed vendor deployments
- **Legacy Integration** - Combining existing Fortinet with new Meraki
- **Security Compliance** - Comprehensive firewall and AP monitoring
- **Network Planning** - Complete infrastructure visualization

## Security Considerations

### API Token Management
- **Secure Storage** - API tokens stored in Flask sessions
- **HTTPS Recommended** - Use SSL/TLS for production deployments
- **Token Rotation** - Regularly update API tokens
- **Access Control** - Limit API permissions to read-only where possible

### Network Access
- **Firewall Rules** - Ensure management access to Fortigate devices
- **VPN Access** - Secure remote management capabilities
- **Network Segmentation** - Isolate management traffic

## Troubleshooting

### Common Issues

#### Connection Failures
- **Verify IP/Hostname** - Ensure Fortigate is reachable
- **Check API Token** - Validate FortiOS API token permissions
- **Firewall Rules** - Confirm management access is allowed
- **SSL Certificates** - Corporate SSL interception may cause issues

#### Missing Devices
- **API Permissions** - Ensure token has device read access
- **Network Connectivity** - Verify management network access
- **FortiAP Registration** - Check AP registration with Fortigate
- **Meraki API Limits** - Monitor API rate limiting

#### Visualization Issues
- **Browser Compatibility** - Use modern browsers with JavaScript enabled
- **Network Size** - Large topologies may require performance optimization
- **Data Refresh** - Clear browser cache if seeing stale data

### Debug Logging
Enable debug logging in the web application for detailed troubleshooting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Additional Vendors** - Support for Ubiquiti, Aruba, etc.
- **Real-time Updates** - Live topology refresh capabilities
- **Performance Metrics** - Bandwidth utilization and performance data
- **Alerting Integration** - Notifications for device status changes
- **Configuration Management** - Device configuration backup and restore

### API Expansion
- **Device Configuration** - Remote configuration capabilities
- **Firmware Management** - Update tracking and management
- **Security Policies** - Unified security policy visualization
- **Traffic Analysis** - Network flow and usage analytics

## Support

For technical support or feature requests:
- **GitHub Issues** - Report bugs and request features
- **Documentation** - Comprehensive guides and API reference
- **Community** - User forums and discussion groups

---

**Multi-Vendor Network Topology Integration** - Bringing unified visibility to complex restaurant and enterprise networks.
