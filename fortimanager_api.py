"""
FortiManager API Module
Provides FortiManager JSON-RPC API integration for centralized device management
"""

import json
import requests
import logging
from typing import Dict, List, Optional, Any

# Apply SSL fixes for corporate environments with self-signed certificates
try:
    from ssl_universal_fix import apply_all_ssl_fixes
    apply_all_ssl_fixes(verbose=False)
    print("[FortiManager API] SSL fixes applied successfully")
except ImportError:
    print("[FortiManager API] SSL fix module not found, using manual SSL bypass")
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning
    urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class FortiManagerAPI:
    """FortiManager JSON-RPC API client for centralized device management"""
    
    def __init__(self, host, username, password, port=443, timeout=30, site=None):
        """
        Initialize FortiManager API client
        
        Args:
            host (str): FortiManager IP address or hostname
            username (str): FortiManager username
            password (str): FortiManager password
            port (int): HTTPS port (default: 443)
            timeout (int): Request timeout (default: 30)
            site (str): Site name for Redis session management (default: 'default')
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.site = site or 'default'
        self.base_url = f"https://{host}:{port}/jsonrpc"
        self.session_id = None
        
        # Create session with SSL verification disabled
        self.session = requests.Session()
        self.session.verify = False
        
        # Initialize session managers if available
        self.redis_session_manager = None
        self.fm_session_manager = None
        self._initialize_session_managers()
        
    def _initialize_session_managers(self):
        """Initialize Redis and FortiManager session managers if available"""
        try:
            from redis_session_manager import get_session_managers
            self.redis_session_manager, self.fm_session_manager = get_session_managers()
            if self.redis_session_manager:
                logger.info(f"Redis session management enabled for {self.site}")
        except ImportError:
            logger.info("Redis session management not available - using direct connections")
        except Exception as e:
            logger.warning(f"Session manager initialization failed: {str(e)}")
    
    def login(self):
        """
        Login to FortiManager and establish session with Redis token reuse
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # First, try to get cached session token from Redis
            if self.fm_session_manager:
                cached_session = self.fm_session_manager.get_fortimanager_session(
                    self.site, self.host, self.username
                )
                if cached_session:
                    self.session_id = cached_session
                    logger.info(f"Using cached FortiManager session for {self.site}: {self.host}")
                    return True
            
            logger.info(f"Attempting new login to FortiManager: {self.host}:{self.port}")
            logger.info(f"Using username: {self.username}")
            logger.info(f"JSON-RPC URL: {self.base_url}")
            
            payload = {
                "method": "exec",
                "params": [{
                    "url": "/sys/login/user",
                    "data": {
                        "user": self.username,
                        "passwd": self.password
                    }
                }],
                "id": 1
            }
            
            logger.debug(f"Login payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            logger.info(f"Login response status: {response.status_code}")
            logger.debug(f"Login response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.debug(f"Login response JSON: {json.dumps(result, indent=2)}")
                    
                    if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                        self.session_id = result.get('session')
                        logger.info(f"Successfully logged into FortiManager: {self.host}")
                        logger.info(f"Session ID: {self.session_id}")
                        
                        # Store session token in Redis for reuse
                        if self.fm_session_manager and self.session_id:
                            self.fm_session_manager.store_fortimanager_session(
                                self.site, self.host, self.username, self.session_id
                            )
                            logger.info(f"Stored FortiManager session token in Redis for {self.site}")
                        
                        return True
                    else:
                        error_code = result.get('result', [{}])[0].get('status', {}).get('code', 'Unknown')
                        error_msg = result.get('result', [{}])[0].get('status', {}).get('message', 'Unknown error')
                        logger.error(f"FortiManager login failed - Code: {error_code}, Message: {error_msg}")
                        return False
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {str(e)}")
                    logger.error(f"Raw response: {response.text[:500]}")
                    return False
            else:
                logger.error(f"FortiManager login HTTP error: {response.status_code}")
                logger.error(f"Response text: {response.text[:500]}")
                return False
                
        except requests.exceptions.ConnectTimeout as e:
            logger.error(f"FortiManager connection timeout: {str(e)}")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"FortiManager connection error: {str(e)}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"FortiManager request error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"FortiManager login unexpected error: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return False
    
    def logout(self):
        """Logout from FortiManager"""
        try:
            if self.session_id:
                payload = {
                    "method": "exec",
                    "params": [{
                        "url": "/sys/logout"
                    }],
                    "session": self.session_id,
                    "id": 1
                }
                
                self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                self.session_id = None
                logger.info("Logged out from FortiManager")
                
        except Exception as e:
            logger.error(f"FortiManager logout error: {str(e)}")
    
    def get_managed_devices(self):
        """
        Get list of managed devices from FortiManager
        
        Returns:
            list: List of managed devices with details
        """
        try:
            if not self.session_id:
                logger.error("Not logged into FortiManager")
                return []
            
            payload = {
                "method": "get",
                "params": [{
                    "url": "/dvmdb/device"
                }],
                "session": self.session_id,
                "id": 1
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    devices = result.get('result', [{}])[0].get('data', [])
                    
                    # Process device information
                    processed_devices = []
                    for device in devices:
                        processed_device = {
                            'name': device.get('name', 'Unknown'),
                            'serial': device.get('sn', 'N/A'),
                            'model': device.get('platform_str', 'N/A'),
                            'os_ver': device.get('os_ver', 'N/A'),
                            'status': 'online' if device.get('conn_status') == 1 else 'offline',
                            'ip': device.get('ip', 'N/A'),
                            'site': device.get('meta fields', {}).get('Company/Organization', 'N/A'),
                            'device_type': 'FortiGate',
                            'vendor': 'Fortinet'
                        }
                        processed_devices.append(processed_device)
                    
                    logger.info(f"Retrieved {len(processed_devices)} managed devices")
                    return processed_devices
                else:
                    error_msg = result.get('result', [{}])[0].get('status', {}).get('message', 'Unknown error')
                    logger.error(f"Failed to get managed devices: {error_msg}")
                    return []
            else:
                logger.error(f"Get managed devices HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting managed devices: {str(e)}")
            return []
    
    def get_device_interfaces(self, device_name):
        """
        Get interfaces for a specific device
        
        Args:
            device_name (str): Name of the device
            
        Returns:
            list: List of device interfaces
        """
        try:
            if not self.session_id:
                logger.error("Not logged into FortiManager")
                return []
            
            payload = {
                "method": "get",
                "params": [{
                    "url": f"/pm/config/device/{device_name}/global/system/interface"
                }],
                "session": self.session_id,
                "id": 1
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    interfaces = result.get('result', [{}])[0].get('data', [])
                    
                    # Process interface information
                    processed_interfaces = []
                    for interface in interfaces:
                        processed_interface = {
                            'name': interface.get('name', 'Unknown'),
                            'ip': interface.get('ip', ['0.0.0.0', '0.0.0.0'])[0],
                            'status': interface.get('status', 'down'),
                            'type': interface.get('type', 'unknown'),
                            'vdom': interface.get('vdom', 'root')
                        }
                        processed_interfaces.append(processed_interface)
                    
                    return processed_interfaces
                else:
                    logger.error(f"Failed to get interfaces for {device_name}")
                    return []
            else:
                logger.error(f"Get interfaces HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting interfaces for {device_name}: {str(e)}")
            return []
    
    def get_device_inventory(self):
        """
        Get comprehensive device inventory with VLAN information
        
        Returns:
            dict: Device inventory data with nodes and connections
        """
        try:
            devices = self.get_managed_devices()
            
            inventory_data = {
                'nodes': [],
                'edges': [],
                'vlans': {},
                'stats': {
                    'total_devices': len(devices),
                    'online_devices': len([d for d in devices if d['status'] == 'online']),
                    'offline_devices': len([d for d in devices if d['status'] == 'offline'])
                }
            }
            
            # Process devices into nodes
            for device in devices:
                node = {
                    'id': device['name'],
                    'name': device['name'],
                    'type': 'fortigate',
                    'vendor': 'Fortinet',
                    'model': device['model'],
                    'serial': device['serial'],
                    'status': device['status'],
                    'ip': device['ip'],
                    'site': device['site'],
                    'size': 35,  # Enhanced icon size
                    'icon': 'fas fa-shield-alt',
                    'color': '#d43527' if device['status'] == 'online' else '#6c757d'
                }
                inventory_data['nodes'].append(node)
                
                # Get interfaces for connection mapping
                interfaces = self.get_device_interfaces(device['name'])
                for interface in interfaces:
                    if interface['status'] == 'up' and interface['ip'] != '0.0.0.0':
                        # Create VLAN/network information
                        vlan_key = f"{device['name']}_{interface['name']}"
                        inventory_data['vlans'][vlan_key] = {
                            'name': interface['name'],
                            'ip': interface['ip'],
                            'device': device['name'],
                            'type': interface['type'],
                            'vdom': interface['vdom']
                        }
            
            logger.info(f"Generated inventory with {len(inventory_data['nodes'])} nodes and {len(inventory_data['vlans'])} VLANs")
            return inventory_data
            
        except Exception as e:
            logger.error(f"Error getting device inventory: {str(e)}")
            return {'nodes': [], 'edges': [], 'vlans': {}, 'stats': {}}
    
    def get_device_status(self, device_name):
        """
        Get detailed status for a specific device
        
        Args:
            device_name (str): Name of the device
            
        Returns:
            dict: Device status information
        """
        try:
            if not self.session_id:
                logger.error("Not logged into FortiManager")
                return {}
            
            payload = {
                "method": "get",
                "params": [{
                    "url": f"/dvmdb/device/{device_name}"
                }],
                "session": self.session_id,
                "id": 1
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    device_data = result.get('result', [{}])[0].get('data', {})
                    
                    status = {
                        'name': device_data.get('name', 'Unknown'),
                        'status': 'online' if device_data.get('conn_status') == 1 else 'offline',
                        'last_seen': device_data.get('last_resync', 'N/A'),
                        'uptime': device_data.get('uptime', 'N/A'),
                        'cpu_usage': device_data.get('cpu', 'N/A'),
                        'memory_usage': device_data.get('mem', 'N/A'),
                        'version': device_data.get('os_ver', 'N/A')
                    }
                    
                    return status
                else:
                    logger.error(f"Failed to get status for {device_name}")
                    return {}
            else:
                logger.error(f"Get device status HTTP error: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting device status for {device_name}: {str(e)}")
            return {}
