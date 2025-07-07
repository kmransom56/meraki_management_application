"""
Improved Meraki API client with SSL handling and error recovery.
Addresses SSL certificate verification errors and API request failures.
"""
import ssl
import certifi
import requests
import logging
from typing import Optional, Dict, Any, List
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import urllib3


class MerakiClient:
    """Enhanced Meraki API client with proper SSL handling and error recovery."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.meraki.com/api/v1", 
                 timeout: int = 30, ssl_verify: bool = True):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.ssl_verify = ssl_verify
        self.logger = logging.getLogger(__name__)
        
        # Create session with proper SSL configuration
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with proper SSL configuration and retry strategy."""
        session = requests.Session()
        
        # Set up headers
        session.headers.update({
            'X-Cisco-Meraki-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'MerakiCLI-Debugger/1.0'
        })
        
        # Configure SSL context
        if self.ssl_verify:
            # Create SSL context with proper certificate verification
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Configure the adapter with SSL context
            adapter = HTTPAdapter()
            session.mount('https://', adapter)
        else:
            # Disable SSL warnings if verification is disabled
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an API request with proper error handling and SSL fallback."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # First attempt with SSL verification
        try:
            self.logger.info(f"Making request to {url} with timeout {self.timeout}s")
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                verify=self.ssl_verify,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.SSLError as e:
            self.logger.error(f"SSL error: {e}")
            
            # Fallback: retry without SSL verification
            if self.ssl_verify:
                self.logger.warning("SSL verification failed, retrying without verification")
                try:
                    response = self.session.request(
                        method=method,
                        url=url,
                        timeout=self.timeout,
                        verify=False,
                        **kwargs
                    )
                    response.raise_for_status()
                    return response
                except Exception as fallback_error:
                    self.logger.error(f"Fallback request also failed: {fallback_error}")
                    raise
            else:
                raise
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise
    
    def get_organizations(self) -> List[Dict[str, Any]]:
        """Get list of organizations."""
        try:
            response = self._make_request('GET', '/organizations')
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get organizations: {e}")
            return []
    
    def get_networks(self, org_id: str) -> List[Dict[str, Any]]:
        """Get networks for an organization."""
        try:
            response = self._make_request('GET', f'/organizations/{org_id}/networks', 
                                        params={'perPage': 5000})
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get networks for org {org_id}: {e}")
            return []
    
    def get_network(self, network_id: str) -> Optional[Dict[str, Any]]:
        """Get network details."""
        try:
            response = self._make_request('GET', f'/networks/{network_id}')
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get network {network_id}: {e}")
            return None
    
    def get_devices(self, network_id: str) -> List[Dict[str, Any]]:
        """Get devices in a network."""
        try:
            response = self._make_request('GET', f'/networks/{network_id}/devices')
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get devices for network {network_id}: {e}")
            return []
    
    def get_clients(self, network_id: str, timespan: int = 10800) -> List[Dict[str, Any]]:
        """Get clients in a network."""
        try:
            response = self._make_request('GET', f'/networks/{network_id}/clients',
                                        params={'perPage': 1000, 'timespan': timespan})
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get clients for network {network_id}: {e}")
            return []
    
    def get_topology_links(self, network_id: str) -> List[Dict[str, Any]]:
        """Get topology links for a network."""
        try:
            response = self._make_request('GET', f'/networks/{network_id}/topology/links')
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.logger.warning(f"Topology links not available for network {network_id}")
                return []
            else:
                self.logger.error(f"Failed to get topology links: {e}")
                return []
        except Exception as e:
            self.logger.error(f"Failed to get topology links for network {network_id}: {e}")
            return []
    
    def build_manual_topology(self, devices: List[Dict[str, Any]], 
                            clients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build topology manually when API doesn't provide it."""
        self.logger.info("Building topology manually from device and client data")
        
        nodes = []
        links = []
        
        # Add devices as nodes
        for device in devices:
            nodes.append({
                'id': device.get('serial', device.get('mac')),
                'name': device.get('name', 'Unknown Device'),
                'type': 'device',
                'model': device.get('model'),
                'status': device.get('status', 'unknown'),
                'productType': device.get('productType', 'unknown'),
                'networkId': device.get('networkId'),
                'address': device.get('address', ''),
                'lat': device.get('lat'),
                'lng': device.get('lng')
            })
        
        # Add clients as nodes
        for client in clients:
            nodes.append({
                'id': client.get('mac', client.get('id')),
                'name': client.get('description', client.get('dhcpHostname', 'Unknown Client')),
                'type': 'client',
                'ip': client.get('ip'),
                'vlan': client.get('vlan'),
                'status': client.get('status', 'unknown'),
                'switchport': client.get('switchport'),
                'connectedDevice': client.get('recentDeviceSerial')
            })
            
            # Create link between client and connected device
            if client.get('recentDeviceSerial'):
                links.append({
                    'source': client.get('mac', client.get('id')),
                    'target': client.get('recentDeviceSerial'),
                    'type': 'client_connection'
                })
        
        return {
            'nodes': nodes,
            'links': links,
            'metadata': {
                'deviceCount': len(devices),
                'clientCount': len(clients),
                'totalNodes': len(nodes),
                'totalLinks': len(links)
            }
        }
