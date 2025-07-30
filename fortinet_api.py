#!/usr/bin/env python3
"""
Fortinet API Integration Module
Provides integration with Fortigate firewalls and FortiAP access points
for multi-vendor network topology visualization
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
import urllib3
from urllib.parse import urljoin

# Disable SSL warnings for corporate environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class FortinetAPIManager:
    """Fortinet API Manager for Fortigate and FortiAP integration"""
    
    def __init__(self):
        self.fortigate_hosts = []
        self.api_tokens = {}
        self.session = requests.Session()
        self.session.verify = False  # For corporate SSL environments
        
    def add_fortigate(self, host: str, api_token: str, name: str = None):
        """Add a Fortigate firewall to manage"""
        fortigate_config = {
            'host': host,
            'api_token': api_token,
            'name': name or host,
            'base_url': f"https://{host}/api/v2/"
        }
        self.fortigate_hosts.append(fortigate_config)
        self.api_tokens[host] = api_token
        logger.info(f"Added Fortigate: {name or host} ({host})")
        
    def _make_request(self, fortigate_config: Dict, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Make API request to Fortigate"""
        try:
            url = urljoin(fortigate_config['base_url'], endpoint)
            headers = {
                'Authorization': f"Bearer {fortigate_config['api_token']}",
                'Content-Type': 'application/json'
            }
            
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Fortigate API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Fortigate API request failed: {e}")
            return None
    
    def get_fortigate_system_status(self, fortigate_config: Dict) -> Optional[Dict]:
        """Get Fortigate system status and information"""
        result = self._make_request(fortigate_config, 'monitor/system/status')
        if result and 'results' in result:
            return result['results']
        return None
    
    def get_fortigate_interfaces(self, fortigate_config: Dict) -> List[Dict]:
        """Get Fortigate network interfaces"""
        result = self._make_request(fortigate_config, 'monitor/system/interface')
        if result and 'results' in result:
            return result['results']
        return []
    
    def get_fortiaps(self, fortigate_config: Dict) -> List[Dict]:
        """Get FortiAP access points managed by this Fortigate"""
        # Get managed FortiAPs
        result = self._make_request(fortigate_config, 'monitor/wifi/managed_ap')
        if result and 'results' in result:
            return result['results']
        return []
    
    def get_fortiap_status(self, fortigate_config: Dict) -> List[Dict]:
        """Get detailed FortiAP status information"""
        result = self._make_request(fortigate_config, 'monitor/wifi/ap_status')
        if result and 'results' in result:
            return result['results']
        return []
    
    def get_wifi_clients(self, fortigate_config: Dict) -> List[Dict]:
        """Get WiFi clients connected to FortiAPs"""
        result = self._make_request(fortigate_config, 'monitor/wifi/client')
        if result and 'results' in result:
            return result['results']
        return []
    
    def get_network_topology_data(self) -> Dict:
        """Get comprehensive network topology data from all Fortigate devices"""
        topology_data = {
            'fortigates': [],
            'fortiaps': [],
            'wifi_clients': [],
            'interfaces': [],
            'connections': []
        }
        
        for fortigate_config in self.fortigate_hosts:
            try:
                # Get Fortigate system info
                system_status = self.get_fortigate_system_status(fortigate_config)
                if system_status:
                    fortigate_info = {
                        'id': fortigate_config['host'],
                        'name': fortigate_config['name'],
                        'host': fortigate_config['host'],
                        'type': 'fortigate',
                        'vendor': 'fortinet',
                        'model': system_status.get('model', 'Unknown'),
                        'version': system_status.get('version', 'Unknown'),
                        'serial': system_status.get('serial', 'Unknown'),
                        'hostname': system_status.get('hostname', fortigate_config['name']),
                        'status': 'online' if system_status else 'offline',
                        'uptime': system_status.get('uptime', 0),
                        'cpu_usage': system_status.get('cpu', 0),
                        'memory_usage': system_status.get('mem', 0)
                    }
                    topology_data['fortigates'].append(fortigate_info)
                
                # Get interfaces
                interfaces = self.get_fortigate_interfaces(fortigate_config)
                for interface in interfaces:
                    interface_info = {
                        'fortigate_id': fortigate_config['host'],
                        'name': interface.get('name'),
                        'ip': interface.get('ip'),
                        'status': interface.get('status'),
                        'type': interface.get('type'),
                        'speed': interface.get('speed'),
                        'duplex': interface.get('duplex')
                    }
                    topology_data['interfaces'].append(interface_info)
                
                # Get FortiAPs
                fortiaps = self.get_fortiaps(fortigate_config)
                ap_status = self.get_fortiap_status(fortigate_config)
                
                # Create status lookup for APs
                ap_status_map = {ap.get('name', ap.get('serial', '')): ap for ap in ap_status}
                
                for ap in fortiaps:
                    ap_name = ap.get('name', ap.get('serial', ''))
                    status_info = ap_status_map.get(ap_name, {})
                    
                    fortiap_info = {
                        'id': ap.get('serial', ap_name),
                        'name': ap_name,
                        'serial': ap.get('serial'),
                        'type': 'fortiap',
                        'vendor': 'fortinet',
                        'model': ap.get('model', 'FortiAP'),
                        'ip': ap.get('ip', status_info.get('ip')),
                        'mac': ap.get('mac'),
                        'status': status_info.get('status', 'unknown'),
                        'fortigate_id': fortigate_config['host'],
                        'location': ap.get('location'),
                        'clients': status_info.get('client_count', 0),
                        'uptime': status_info.get('uptime', 0),
                        'channel_2g': status_info.get('radio_2g', {}).get('channel'),
                        'channel_5g': status_info.get('radio_5g', {}).get('channel')
                    }
                    topology_data['fortiaps'].append(fortiap_info)
                    
                    # Create connection between Fortigate and FortiAP
                    connection = {
                        'source': fortigate_config['host'],
                        'target': fortiap_info['id'],
                        'type': 'management',
                        'vendor': 'fortinet'
                    }
                    topology_data['connections'].append(connection)
                
                # Get WiFi clients
                wifi_clients = self.get_wifi_clients(fortigate_config)
                for client in wifi_clients:
                    client_info = {
                        'id': client.get('mac'),
                        'mac': client.get('mac'),
                        'ip': client.get('ip'),
                        'hostname': client.get('hostname'),
                        'ap_serial': client.get('ap'),
                        'ssid': client.get('ssid'),
                        'signal': client.get('signal'),
                        'type': 'wifi_client',
                        'vendor': 'fortinet_managed'
                    }
                    topology_data['wifi_clients'].append(client_info)
                    
                    # Create connection between client and FortiAP
                    if client.get('ap'):
                        connection = {
                            'source': client.get('mac'),
                            'target': client.get('ap'),
                            'type': 'wifi',
                            'vendor': 'fortinet'
                        }
                        topology_data['connections'].append(connection)
                        
            except Exception as e:
                logger.error(f"Error getting topology data from {fortigate_config['name']}: {e}")
                continue
        
        return topology_data
    
    def test_connection(self, fortigate_config: Dict) -> bool:
        """Test connection to a Fortigate device"""
        try:
            result = self.get_fortigate_system_status(fortigate_config)
            return result is not None
        except Exception as e:
            logger.error(f"Connection test failed for {fortigate_config['name']}: {e}")
            return False
    
    def get_device_details(self, device_id: str, device_type: str) -> Optional[Dict]:
        """Get detailed information about a specific device"""
        for fortigate_config in self.fortigate_hosts:
            if device_type == 'fortigate' and device_id == fortigate_config['host']:
                return self.get_fortigate_system_status(fortigate_config)
            elif device_type == 'fortiap':
                fortiaps = self.get_fortiaps(fortigate_config)
                for ap in fortiaps:
                    if ap.get('serial') == device_id or ap.get('name') == device_id:
                        return ap
        return None

# Global Fortinet API manager instance
fortinet_manager = FortinetAPIManager()
