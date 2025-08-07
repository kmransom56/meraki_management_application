"""
Fortigate API Integration Module
Handles connections to FortiManager and FortiGate devices
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class FortiManagerAPI:
    """FortiManager API client for managing Fortigate devices"""
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session_id = None
        self.base_url = f"https://{self.host}/jsonrpc"
        
    def login(self) -> bool:
        """Authenticate with FortiManager"""
        try:
            payload = {
                "id": 1,
                "method": "exec",
                "params": [{
                    "url": "/sys/login/user",
                    "data": {
                        "user": self.username,
                        "passwd": self.password
                    }
                }]
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    self.session_id = result['session']
                    logger.info("Successfully authenticated with FortiManager")
                    return True
                    
            logger.error(f"FortiManager authentication failed: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to FortiManager: {str(e)}")
            return False
    
    def logout(self):
        """Logout from FortiManager"""
        if not self.session_id:
            return
            
        try:
            payload = {
                "id": 1,
                "method": "exec",
                "params": [{
                    "url": "/sys/logout"
                }],
                "session": self.session_id
            }
            
            requests.post(
                self.base_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=10
            )
            
            self.session_id = None
            logger.info("Logged out from FortiManager")
            
        except Exception as e:
            logger.error(f"Error during FortiManager logout: {str(e)}")
    
    def get_managed_devices(self) -> List[Dict]:
        """Get list of managed FortiGate devices"""
        if not self.session_id:
            if not self.login():
                return []
        
        try:
            payload = {
                "id": 1,
                "method": "get",
                "params": [{
                    "url": "/dvmdb/device"
                }],
                "session": self.session_id
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    devices = result['result'][0].get('data', [])
                    logger.info(f"Retrieved {len(devices)} FortiGate devices")
                    return devices
                    
            logger.error(f"Failed to get FortiGate devices: {response.text}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting FortiGate devices: {str(e)}")
            return []
    
    def get_device_interfaces(self, device_name: str) -> List[Dict]:
        """Get interfaces for a specific FortiGate device"""
        if not self.session_id:
            if not self.login():
                return []
        
        try:
            payload = {
                "id": 1,
                "method": "get",
                "params": [{
                    "url": f"/pm/config/device/{device_name}/global/system/interface"
                }],
                "session": self.session_id
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    interfaces = result['result'][0].get('data', [])
                    logger.info(f"Retrieved {len(interfaces)} interfaces for {device_name}")
                    return interfaces
                    
            logger.error(f"Failed to get interfaces for {device_name}: {response.text}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting interfaces for {device_name}: {str(e)}")
            return []
    
    def get_device_inventory(self) -> List[Dict]:
        """Get comprehensive device inventory from FortiManager including all managed devices"""
        if not self.session_id:
            if not self.login():
                return []
        
        device_inventory = []
        
        try:
            # Get all managed devices first
            managed_devices = self.get_managed_devices()
            
            for device in managed_devices:
                device_name = device.get('name')
                if not device_name:
                    continue
                
                # Get device status and details
                device_info = self.get_device_status(device_name)
                
                # Create comprehensive device inventory entry
                inventory_entry = {
                    'id': device.get('oid') or device_name,
                    'name': device_name,
                    'hostname': device.get('hostname', device_name),
                    'ip': device.get('ip', 'Unknown'),
                    'mac': device.get('mac', 'Unknown'),
                    'serial': device.get('sn', 'Unknown'),
                    'model': device.get('platform_str', 'FortiGate'),
                    'os_version': device.get('os_ver', 'Unknown'),
                    'firmware': device.get('os_ver', 'Unknown'),
                    'vendor': 'Fortinet',
                    'device_type': 'FortiGate Firewall',
                    'device_family': 'Security Appliance',
                    'status': device_info.get('status', 'Unknown') if device_info else 'Unknown',
                    'uptime': device_info.get('uptime', 0) if device_info else 0,
                    'location': device.get('desc', ''),
                    'group': 'fortigate',
                    'managed_by': 'FortiManager',
                    'last_seen': device_info.get('last_checkin', 'Unknown') if device_info else 'Unknown',
                    'interfaces': self.get_device_interfaces(device_name),
                    'vlans': self.get_device_vlans(device_name)
                }
                
                device_inventory.append(inventory_entry)
                
                # Get connected devices (ARP table, DHCP leases, etc.)
                connected_devices = self.get_connected_devices(device_name)
                device_inventory.extend(connected_devices)
            
            logger.info(f"Retrieved comprehensive inventory for {len(device_inventory)} devices")
            return device_inventory
            
        except Exception as e:
            logger.error(f"Error getting device inventory: {str(e)}")
            return []
    
    def get_device_status(self, device_name: str) -> Optional[Dict]:
        """Get detailed status information for a specific device"""
        if not self.session_id:
            if not self.login():
                return None
        
        try:
            payload = {
                "id": 1,
                "method": "exec",
                "params": [{
                    "url": f"/sys/proxy/json",
                    "data": {
                        "target": [device_name],
                        "action": "get",
                        "resource": "/api/v2/monitor/system/status"
                    }
                }],
                "session": self.session_id
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    status_data = result['result'][0].get('data', [{}])[0]
                    return status_data.get('response', {}).get('results', {})
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting device status for {device_name}: {str(e)}")
            return None
    
    def get_device_vlans(self, device_name: str) -> List[Dict]:
        """Get VLAN information for a specific device"""
        if not self.session_id:
            if not self.login():
                return []
        
        try:
            payload = {
                "id": 1,
                "method": "get",
                "params": [{
                    "url": f"/pm/config/device/{device_name}/global/system/interface"
                }],
                "session": self.session_id
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                verify=self.verify_ssl,
                timeout=30
            )
            
            vlans = []
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    interfaces = result['result'][0].get('data', [])
                    
                    for interface in interfaces:
                        if interface.get('vlanid'):
                            vlan_info = {
                                'id': interface.get('vlanid'),
                                'name': interface.get('alias') or f"VLAN{interface.get('vlanid')}",
                                'interface': interface.get('name'),
                                'ip': interface.get('ip', ['0.0.0.0', '0.0.0.0'])[0],
                                'description': interface.get('description', '')
                            }
                            vlans.append(vlan_info)
            
            return vlans
            
        except Exception as e:
            logger.error(f"Error getting VLANs for {device_name}: {str(e)}")
            return []
    
    def get_connected_devices(self, device_name: str) -> List[Dict]:
        """Get devices connected to a specific FortiGate (from ARP table, DHCP leases, etc.)"""
        if not self.session_id:
            if not self.login():
                return []
        
        connected_devices = []
        
        try:
            # Get ARP table
            arp_payload = {
                "id": 1,
                "method": "exec",
                "params": [{
                    "url": f"/sys/proxy/json",
                    "data": {
                        "target": [device_name],
                        "action": "get",
                        "resource": "/api/v2/monitor/system/arp"
                    }
                }],
                "session": self.session_id
            }
            
            response = requests.post(
                self.base_url,
                json=arp_payload,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    arp_data = result['result'][0].get('data', [{}])[0]
                    arp_entries = arp_data.get('response', {}).get('results', [])
                    
                    for entry in arp_entries:
                        # Skip FortiGate's own interfaces
                        if entry.get('interface', '').startswith(('lo', 'mgmt')):
                            continue
                            
                        device_entry = {
                            'id': entry.get('mac', f"unknown_{len(connected_devices)}"),
                            'name': entry.get('hostname', f"Device-{entry.get('mac', 'Unknown')[-6:]}"),
                            'hostname': entry.get('hostname', 'Unknown'),
                            'ip': entry.get('ip', 'Unknown'),
                            'mac': entry.get('mac', 'Unknown'),
                            'interface': entry.get('interface', 'Unknown'),
                            'vendor': 'Unknown',
                            'device_type': 'Connected Device',
                            'device_family': 'Client Device',
                            'status': 'Online',
                            'group': 'client',
                            'managed_by': f'FortiGate-{device_name}',
                            'parent_device': device_name
                        }
                        
                        # Try to identify device type based on MAC address or other info
                        mac = entry.get('mac', '').upper()
                        if mac.startswith(('00:09:0F', '34:17:EB', '88:15:44')):
                            device_entry['vendor'] = 'Cisco Meraki'
                            device_entry['device_type'] = 'Meraki Switch'
                            device_entry['group'] = 'switch'
                        elif mac.startswith(('F0:9F:C2', '34:56:FE')):
                            device_entry['vendor'] = 'Fortinet'
                            device_entry['device_type'] = 'FortiAP'
                            device_entry['group'] = 'fortiap'
                        
                        connected_devices.append(device_entry)
            
            return connected_devices
            
        except Exception as e:
            logger.error(f"Error getting connected devices for {device_name}: {str(e)}")
            return []

class FortiGateDirectAPI:
    """Direct FortiGate API client for single device management"""
    
    def __init__(self, host: str, api_key: str, verify_ssl: bool = False):
        self.host = host.rstrip('/')
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{self.host}/api/v2"
        
    def get_system_status(self) -> Dict:
        """Get FortiGate system status"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/monitor/system/status",
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get FortiGate status: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting FortiGate status: {str(e)}")
            return {}
    
    def get_interfaces(self) -> List[Dict]:
        """Get FortiGate interfaces"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/cmdb/system/interface",
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('results', [])
            else:
                logger.error(f"Failed to get FortiGate interfaces: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting FortiGate interfaces: {str(e)}")
            return []
    
    def get_arp_table(self) -> List[Dict]:
        """Get FortiGate ARP table"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/monitor/system/arp",
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('results', [])
            else:
                logger.error(f"Failed to get FortiGate ARP table: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting FortiGate ARP table: {str(e)}")
            return []

def build_fortigate_topology_data(fortigate_devices: List[Dict], meraki_devices: List[Dict] = None) -> Dict:
    """
    Build topology data including FortiGate devices
    
    Args:
        fortigate_devices: List of FortiGate device data
        meraki_devices: List of Meraki device data (optional)
    
    Returns:
        Dict containing nodes and edges for topology visualization
    """
    nodes = []
    edges = []
    
    # Process FortiGate devices
    for device in fortigate_devices:
        # Add FortiGate firewall node
        node = {
            'id': f"fortigate_{device.get('name', device.get('serial', 'unknown'))}",
            'label': device.get('name', f"FortiGate-{device.get('serial', 'Unknown')}"),
            'group': 'fortigate',
            'size': 12,
            'title': f"FortiGate Firewall<br>Name: {device.get('name', 'Unknown')}<br>Model: {device.get('platform_str', 'Unknown')}<br>Version: {device.get('os_ver', 'Unknown')}<br>Serial: {device.get('serial', 'Unknown')}"
        }
        nodes.append(node)
        
        # Add interfaces as potential connection points
        interfaces = device.get('interfaces', [])
        for interface in interfaces:
            if interface.get('ip') and interface.get('ip') != '0.0.0.0':
                # Create interface node for significant interfaces
                if any(keyword in interface.get('name', '').lower() for keyword in ['lan', 'internal', 'dmz']):
                    interface_node = {
                        'id': f"fortigate_int_{device.get('name', 'unknown')}_{interface.get('name', 'unknown')}",
                        'label': f"{interface.get('name', 'Interface')}",
                        'group': 'fortigate',
                        'size': 8,
                        'title': f"FortiGate Interface<br>Name: {interface.get('name', 'Unknown')}<br>IP: {interface.get('ip', 'Unknown')}<br>Status: {interface.get('status', 'Unknown')}"
                    }
                    nodes.append(interface_node)
                    
                    # Connect interface to FortiGate
                    edge = {
                        'source': node['id'],
                        'target': interface_node['id'],
                        'type': 'uplink',
                        'width': 2
                    }
                    edges.append(edge)
    
    # If Meraki devices are provided, integrate them
    if meraki_devices:
        # Add Meraki devices
        for device in meraki_devices:
            device_type = device.get('productType', 'unknown').lower()
            if 'switch' in device_type:
                group = 'switch'
                size = 10
            elif 'wireless' in device_type or 'ap' in device_type:
                group = 'wireless'
                size = 8
            elif 'appliance' in device_type or 'mx' in device_type:
                group = 'appliance'
                size = 12
            else:
                group = 'unknown'
                size = 6
            
            meraki_node = {
                'id': f"meraki_{device.get('serial', 'unknown')}",
                'label': device.get('name', f"Meraki-{device.get('serial', 'Unknown')}"),
                'group': group,
                'size': size,
                'title': f"Meraki {device_type.title()}<br>Name: {device.get('name', 'Unknown')}<br>Model: {device.get('model', 'Unknown')}<br>Serial: {device.get('serial', 'Unknown')}<br>Status: {device.get('status', 'Unknown')}"
            }
            nodes.append(meraki_node)
            
            # Connect Meraki switches to FortiGate (assuming they're downstream)
            if group == 'switch' and nodes:
                # Find the first FortiGate device to connect to
                fortigate_node = next((n for n in nodes if n['group'] == 'fortigate'), None)
                if fortigate_node:
                    edge = {
                        'source': fortigate_node['id'],
                        'target': meraki_node['id'],
                        'type': 'switch',
                        'width': 3
                    }
                    edges.append(edge)
    
    return {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'devices': len([n for n in nodes if n['group'] != 'client']),
            'clients': len([n for n in nodes if n['group'] == 'client']),
            'nodes': len(nodes),
            'edges': len(edges)
        }
    }

# Example usage and testing functions
def test_fortimanager_connection(host: str, username: str, password: str):
    """Test FortiManager connection"""
    fm = FortiManagerAPI(host, username, password)
    if fm.login():
        devices = fm.get_managed_devices()
        print(f"Found {len(devices)} FortiGate devices")
        for device in devices[:3]:  # Show first 3 devices
            print(f"  - {device.get('name', 'Unknown')}: {device.get('platform_str', 'Unknown')}")
        fm.logout()
        return True
    return False

def test_fortigate_direct_connection(host: str, api_key: str):
    """Test direct FortiGate connection"""
    fg = FortiGateDirectAPI(host, api_key)
    status = fg.get_system_status()
    if status:
        print(f"FortiGate Status: {status.get('results', {}).get('hostname', 'Unknown')}")
        interfaces = fg.get_interfaces()
        print(f"Found {len(interfaces)} interfaces")
        return True
    return False
