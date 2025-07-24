// Device Icons and Visual Enhancement Module
class DeviceIcons {
    constructor() {
        this.iconMap = {
            // Security Appliances
            'security_appliance': '🛡️',
            'mx': '🔒',
            'firewall': '🛡️',
            
            // Switches
            'switch': '🔌',
            'ms': '🔌',
            'ethernet': '🔌',
            
            // Wireless Access Points
            'wireless': '📡',
            'mr': '📡',
            'access_point': '📡',
            'ap': '📡',
            
            // Cameras
            'camera': '📹',
            'mv': '📹',
            'security_camera': '📹',
            
            // Phones
            'phone': '📞',
            'voip': '📞',
            
            // Sensors
            'sensor': '🌡️',
            'mt': '🌡️',
            'environmental': '🌡️',
            
            // Clients/Endpoints
            'client': '💻',
            'laptop': '💻',
            'desktop': '🖥️',
            'mobile': '📱',
            'tablet': '📱',
            'phone_client': '📱',
            'printer': '🖨️',
            'server': '🖥️',
            'iot': '🔗',
            
            // Default
            'unknown': '❓',
            'default': '🔘'
        };
        
        this.colorMap = {
            // Device status colors
            'online': '#28a745',
            'offline': '#dc3545',
            'alerting': '#ffc107',
            'dormant': '#6c757d',
            'unknown': '#17a2b8',
            
            // Device type colors
            'security_appliance': '#dc3545',
            'switch': '#007bff',
            'wireless': '#28a745',
            'camera': '#6f42c1',
            'sensor': '#fd7e14',
            'client': '#20c997'
        };
    }
    
    getDeviceIcon(device) {
        const productType = device.productType?.toLowerCase() || '';
        const model = device.model?.toLowerCase() || '';
        
        // Try product type first
        if (this.iconMap[productType]) {
            return this.iconMap[productType];
        }
        
        // Try model prefix (MX, MS, MR, MV, MT)
        const modelPrefix = model.substring(0, 2);
        if (this.iconMap[modelPrefix]) {
            return this.iconMap[modelPrefix];
        }
        
        // Try common device type keywords
        for (const [key, icon] of Object.entries(this.iconMap)) {
            if (model.includes(key) || productType.includes(key)) {
                return icon;
            }
        }
        
        return this.iconMap.default;
    }
    
    getClientIcon(client) {
        const description = client.description?.toLowerCase() || '';
        const manufacturer = client.manufacturer?.toLowerCase() || '';
        const os = client.os?.toLowerCase() || '';
        
        // Check for specific device types
        if (description.includes('iphone') || description.includes('ipad') || os.includes('ios')) {
            return '📱';
        }
        if (description.includes('android') || os.includes('android')) {
            return '📱';
        }
        if (description.includes('windows') || os.includes('windows')) {
            return '💻';
        }
        if (description.includes('mac') || os.includes('mac') || manufacturer.includes('apple')) {
            return '💻';
        }
        if (description.includes('printer') || manufacturer.includes('hp') || manufacturer.includes('canon')) {
            return '🖨️';
        }
        if (description.includes('server') || description.includes('linux')) {
            return '🖥️';
        }
        if (description.includes('camera') || description.includes('surveillance')) {
            return '📹';
        }
        
        return this.iconMap.client;
    }
    
    getDeviceColor(device) {
        const status = device.status?.toLowerCase() || 'unknown';
        const productType = device.productType?.toLowerCase() || '';
        
        // Status takes precedence
        if (this.colorMap[status]) {
            return this.colorMap[status];
        }
        
        // Fall back to device type color
        if (this.colorMap[productType]) {
            return this.colorMap[productType];
        }
        
        return this.colorMap.unknown;
    }
    
    getClientColor(client) {
        const status = client.status?.toLowerCase() || 'unknown';
        
        if (status === 'online' || status === 'active') {
            return this.colorMap.online;
        }
        if (status === 'offline' || status === 'inactive') {
            return this.colorMap.offline;
        }
        
        return this.colorMap.client;
    }
    
    createDeviceNode(device, x = 0, y = 0) {
        return {
            id: device.serial || device.mac || Math.random().toString(36),
            name: device.name || device.model || 'Unknown Device',
            type: 'device',
            productType: device.productType || 'unknown',
            model: device.model || '',
            serial: device.serial || '',
            status: device.status || 'unknown',
            icon: this.getDeviceIcon(device),
            color: this.getDeviceColor(device),
            x: x,
            y: y,
            fx: null,
            fy: null,
            data: device
        };
    }
    
    createClientNode(client, x = 0, y = 0) {
        return {
            id: client.mac || client.id || Math.random().toString(36),
            name: client.description || client.hostname || client.mac || 'Unknown Client',
            type: 'client',
            manufacturer: client.manufacturer || '',
            os: client.os || '',
            status: client.status || 'unknown',
            icon: this.getClientIcon(client),
            color: this.getClientColor(client),
            x: x,
            y: y,
            fx: null,
            fy: null,
            data: client
        };
    }
    
    getDetailedDeviceInfo(device) {
        const info = {
            'Device Name': device.name || 'N/A',
            'Model': device.model || 'N/A',
            'Serial Number': device.serial || 'N/A',
            'Product Type': device.productType || 'N/A',
            'Status': device.status || 'N/A',
            'Firmware': device.firmware || 'N/A',
            'MAC Address': device.mac || 'N/A',
            'Network ID': device.networkId || 'N/A',
            'Tags': Array.isArray(device.tags) ? device.tags.join(', ') : (device.tags || 'N/A')
        };
        
        // Add management interface info if available
        if (device.managementInterface) {
            const mgmt = device.managementInterface;
            info['Management IP'] = mgmt.wan1?.ip || mgmt.ip || 'N/A';
            info['Gateway'] = mgmt.wan1?.gateway || mgmt.gateway || 'N/A';
            info['DNS'] = Array.isArray(mgmt.wan1?.dns) ? mgmt.wan1.dns.join(', ') : 'N/A';
        }
        
        // Add client count if available
        if (device.clientCount !== undefined) {
            info['Connected Clients'] = device.clientCount.toString();
        }
        
        return info;
    }
    
    getDetailedClientInfo(client) {
        return {
            'Description': client.description || 'N/A',
            'MAC Address': client.mac || 'N/A',
            'IP Address': client.ip || 'N/A',
            'Manufacturer': client.manufacturer || 'N/A',
            'Operating System': client.os || 'N/A',
            'Status': client.status || 'N/A',
            'SSID': client.ssid || 'N/A',
            'VLAN': client.vlan || 'N/A',
            'Usage (Sent)': client.usage?.sent ? this.formatBytes(client.usage.sent) : 'N/A',
            'Usage (Received)': client.usage?.recv ? this.formatBytes(client.usage.recv) : 'N/A',
            'First Seen': client.firstSeen ? new Date(client.firstSeen).toLocaleString() : 'N/A',
            'Last Seen': client.lastSeen ? new Date(client.lastSeen).toLocaleString() : 'N/A'
        };
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Export for use in other modules
window.DeviceIcons = DeviceIcons;
