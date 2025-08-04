#!/usr/bin/env python3
"""
Comprehensive Cisco Meraki Web Management Interface
Integrates ALL CLI functionality into a modern web application
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import uuid
import threading
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import SSL fixes for corporate environments
try:
    import ssl_universal_fix
    print("[OK] SSL universal fix applied")
except ImportError:
    try:
        import ssl_patch
        print("[OK] SSL patch applied")
    except ImportError:
        print("[WARNING] No SSL fixes available - may have issues in corporate environments")

# Import multi-vendor topology modules
try:
    from fortinet_api import fortinet_manager
    from multi_vendor_topology import multi_vendor_engine, MultiVendorTopologyEngine
    print("[OK] Multi-vendor topology modules loaded")
except ImportError as e:
    print(f"[WARNING] Multi-vendor modules not available: {e}")
    fortinet_manager = None
    multi_vendor_engine = None

# Import existing modules with error handling
try:
    from api import meraki_api_manager
    from settings import db_creator, term_extra
    from modules.meraki import meraki_api, meraki_ms_mr, meraki_mx, meraki_network
    from modules.tools.utilities import tools_passgen, tools_subnetcalc, tools_ipcheck
    from modules.tools.dnsbl import dnsbl_check
    from enhanced_visualizer import create_enhanced_visualization, build_topology_from_api_data
    from utilities import submenu
    CLI_MODULES_AVAILABLE = True
    print("[OK] All CLI modules loaded successfully")
except ImportError as e:
    print(f"[WARNING] Some CLI modules not available: {e}")
    CLI_MODULES_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'meraki_'

# Global storage for active visualizations and data
active_visualizations = {}
cached_data = {}

class ComprehensiveMerakiManager:
    """Comprehensive Meraki Web Management Class - Integrates ALL CLI functionality"""
    
    def __init__(self):
        self.fernet = None
        self.api_key = None
        self.api_mode = 'custom'
        self.dashboard = None
        
    def initialize_crypto(self, password):
        """Initialize encryption for secure credential storage"""
        try:
            if CLI_MODULES_AVAILABLE:
                self.fernet = db_creator.generate_fernet_key(password)
                return True
            return False
        except Exception as e:
            logger.error(f"Crypto initialization failed: {e}")
            return False
    
    def set_api_key(self, api_key):
        """Set and validate API key"""
        try:
            self.api_key = api_key
            
            # Test API key by getting organizations
            if self.api_mode == 'sdk':
                try:
                    import meraki
                    self.dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
                except ImportError:
                    # Fall back to custom API if SDK not available
                    self.api_mode = 'custom'
            
            if self.api_mode == 'custom' and CLI_MODULES_AVAILABLE:
                # Use custom API through existing CLI modules
                from main import create_custom_dashboard_object
                self.dashboard = create_custom_dashboard_object(api_key)
            
            # Test the API key
            if self.dashboard:
                orgs = self.dashboard.organizations.getOrganizations()
                if orgs:
                    return True
            return False
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    def get_organizations(self):
        """Get all organizations"""
        try:
            if not self.dashboard:
                return []
            return self.dashboard.organizations.getOrganizations()
        except Exception as e:
            logger.error(f"Error getting organizations: {e}")
            return []
    
    def get_networks(self, org_id):
        """Get networks for an organization"""
        try:
            if not self.dashboard:
                return []
            return self.dashboard.organizations.getOrganizationNetworks(org_id)
        except Exception as e:
            logger.error(f"Error getting networks: {e}")
            return []
    
    def get_devices(self, network_id):
        """Get devices for a network"""
        try:
            if not self.dashboard:
                return []
            return self.dashboard.networks.getNetworkDevices(network_id)
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return []
    
    def get_clients(self, network_id, timespan=86400):
        """Get clients for a network"""
        try:
            if not self.dashboard:
                return []
            return self.dashboard.networks.getNetworkClients(network_id, timespan=timespan)
        except Exception as e:
            logger.error(f"Error getting clients: {e}")
            return []
    
    def create_speed_test(self, device_serial):
        """Create a speed test for a device"""
        try:
            if not self.dashboard:
                return None
            # Create speed test job
            result = self.dashboard.devices.createDeviceLiveToolsSpeedTest(device_serial)
            return result
        except Exception as e:
            logger.error(f"Error creating speed test: {e}")
            return None
    
    def get_speed_test_result(self, device_serial, speed_test_id):
        """Get speed test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsSpeedTest(device_serial, speed_test_id)
            return result
        except Exception as e:
            logger.error(f"Error getting speed test result: {e}")
            return None
    
    def create_throughput_test(self, device_serial):
        """Create a throughput test for a device"""
        try:
            if not self.dashboard:
                return None
            # Create throughput test job
            result = self.dashboard.devices.createDeviceLiveToolsThroughputTest(device_serial)
            return result
        except Exception as e:
            logger.error(f"Error creating throughput test: {e}")
            return None
    
    def get_throughput_test_result(self, device_serial, throughput_test_id):
        """Get throughput test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsThroughputTest(device_serial, throughput_test_id)
            return result
        except Exception as e:
            logger.error(f"Error getting throughput test result: {e}")
            return None
    
    # Additional Live Tools Methods
    
    def create_arp_table_test(self, device_serial):
        """Create ARP table live tool job"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.createDeviceLiveToolsArpTable(device_serial)
            return result
        except Exception as e:
            logger.error(f"Error creating ARP table test: {e}")
            return None
    
    def get_arp_table_results(self, device_serial, arp_table_id):
        """Get ARP table test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsArpTable(device_serial, arp_table_id)
            return result
        except Exception as e:
            logger.error(f"Error getting ARP table results: {e}")
            return None
    
    def create_mac_table_test(self, device_serial):
        """Create MAC table live tool job"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.createDeviceLiveToolsMacTable(device_serial)
            return result
        except Exception as e:
            logger.error(f"Error creating MAC table test: {e}")
            return None
    
    def get_mac_table_results(self, device_serial, mac_table_id):
        """Get MAC table test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsMacTable(device_serial, mac_table_id)
            return result
        except Exception as e:
            logger.error(f"Error getting MAC table results: {e}")
            return None
    
    def create_ping_test(self, device_serial, target, count=5):
        """Create ping live tool job"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.createDeviceLiveToolsPing(device_serial, target=target, count=count)
            return result
        except Exception as e:
            logger.error(f"Error creating ping test: {e}")
            return None
    
    def get_ping_results(self, device_serial, ping_id):
        """Get ping test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsPing(device_serial, ping_id)
            return result
        except Exception as e:
            logger.error(f"Error getting ping results: {e}")
            return None
    
    def create_routing_table_test(self, device_serial):
        """Create routing table live tool job"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.createDeviceLiveToolsRoutingTable(device_serial)
            return result
        except Exception as e:
            logger.error(f"Error creating routing table test: {e}")
            return None
    
    def get_routing_table_results(self, device_serial, routing_table_id):
        """Get routing table test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsRoutingTable(device_serial, routing_table_id)
            return result
        except Exception as e:
            logger.error(f"Error getting routing table results: {e}")
            return None
    
    def create_cycle_port_test(self, device_serial, ports):
        """Create cycle port live tool job"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.createDeviceLiveToolsCyclePort(device_serial, ports=ports)
            return result
        except Exception as e:
            logger.error(f"Error creating cycle port test: {e}")
            return None
    
    def get_cycle_port_results(self, device_serial, cycle_port_id):
        """Get cycle port test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsCyclePort(device_serial, cycle_port_id)
            return result
        except Exception as e:
            logger.error(f"Error getting cycle port results: {e}")
            return None
    
    def create_ospf_neighbors_test(self, device_serial):
        """Create OSPF neighbors live tool job"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.createDeviceLiveToolsOspfNeighbors(device_serial)
            return result
        except Exception as e:
            logger.error(f"Error creating OSPF neighbors test: {e}")
            return None
    
    def get_ospf_neighbors_results(self, device_serial, ospf_neighbors_id):
        """Get OSPF neighbors test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsOspfNeighbors(device_serial, ospf_neighbors_id)
            return result
        except Exception as e:
            logger.error(f"Error getting OSPF neighbors results: {e}")
            return None
    
    def create_dhcp_leases_test(self, device_serial):
        """Create DHCP leases live tool job"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.createDeviceLiveToolsDhcpLeases(device_serial)
            return result
        except Exception as e:
            logger.error(f"Error creating DHCP leases test: {e}")
            return None
    
    def get_dhcp_leases_results(self, device_serial, dhcp_leases_id):
        """Get DHCP leases test results"""
        try:
            if not self.dashboard:
                return None
            result = self.dashboard.devices.getDeviceLiveToolsDhcpLeases(device_serial, dhcp_leases_id)
            return result
        except Exception as e:
            logger.error(f"Error getting DHCP leases results: {e}")
            return None

# Global manager instance
meraki_manager = ComprehensiveMerakiManager()

@app.route('/')
def dashboard():
    """Main comprehensive dashboard page"""
    return render_template('comprehensive_dashboard.html')

@app.route('/api/validate_key', methods=['POST'])
def validate_api_key():
    """Validate Meraki API key"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        api_mode = data.get('api_mode', 'custom')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key is required'})
        
        logger.info(f"Validating API key with mode: {api_mode}")
        meraki_manager.api_mode = api_mode
        
        if meraki_manager.set_api_key(api_key):
            session['api_key'] = api_key
            session['api_mode'] = api_mode
            session.permanent = True
            logger.info(f"API key validated and stored in session. Session ID: {session.get('_permanent', 'N/A')}")
            return jsonify({'success': True})
        else:
            logger.warning(f"API key validation failed for key ending in: ...{api_key[-4:] if len(api_key) > 4 else 'short'}")
            return jsonify({'success': False, 'error': 'Invalid API key or API connection failed'})
    
    except Exception as e:
        logger.error(f"API key validation error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/organizations')
def get_organizations():
    """Get all organizations"""
    try:
        # Check session first, then fallback to current API key
        if 'api_key' not in session and not meraki_manager.api_key:
            logger.warning(f"No API key in session. Session keys: {list(session.keys())}")
            return jsonify({'error': 'API key not set'}), 401
        
        # Use session API key if available, otherwise use current manager key
        if 'api_key' in session and session['api_key'] != meraki_manager.api_key:
            meraki_manager.set_api_key(session['api_key'])
        
        orgs = meraki_manager.get_organizations()
        if orgs is None:
            return jsonify({'error': 'Failed to retrieve organizations'}), 500
            
        return jsonify({'organizations': orgs})
    
    except Exception as e:
        logger.error(f"Error getting organizations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/networks/<org_id>')
def get_networks(org_id):
    """Get networks for an organization"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        networks = meraki_manager.get_networks(org_id)
        return jsonify({'networks': networks})
    
    except Exception as e:
        logger.error(f"Error getting networks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<network_id>')
def get_devices(network_id):
    """Get devices for a network"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        devices = meraki_manager.get_devices(network_id)
        return jsonify({'devices': devices})
    
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients/<network_id>')
def get_clients(network_id):
    """Get clients for a network"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        timespan = request.args.get('timespan', 86400, type=int)
        clients = meraki_manager.get_clients(network_id, timespan)
        return jsonify({'clients': clients})
    
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/<network_id>')
def get_topology(network_id):
    """Get network topology data using enhanced visualizer"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Get devices and clients
        devices = meraki_manager.get_devices(network_id)
        clients = meraki_manager.get_clients(network_id)
        
        # Build topology using enhanced visualizer
        if CLI_MODULES_AVAILABLE:
            topology_data = build_topology_from_api_data(devices, clients, links=None)
        else:
            # Fallback topology structure
            topology_data = {
                'nodes': [{'id': d.get('serial', d.get('id')), 'name': d.get('name', 'Unknown'), 'type': 'device'} for d in devices],
                'links': []
            }
        
        return jsonify({
            'topology': topology_data,
            'stats': {
                'devices': len(devices),
                'clients': len(clients),
                'links': len(topology_data.get('links', []))
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting topology: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualization/data')
def get_visualization_data():
    """Get visualization data for topology - generic endpoint"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Return basic visualization configuration
        return jsonify({
            'success': True,
            'device_icons': {
                'switch': 'settings_ethernet',
                'wireless': 'wifi',
                'appliance': 'security',
                'camera': 'videocam',
                'client': 'devices_other',
                'unknown': 'device_unknown'
            },
            'connection_styles': {
                'uplink': {'color': '#00C853', 'width': 3},
                'switch': {'color': '#2196F3', 'width': 2},
                'wireless': {'color': '#FF9800', 'width': 2},
                'wired': {'color': '#607D8B', 'width': 1},
                'unknown': {'color': '#9E9E9E', 'width': 1}
            }
        })
    except Exception as e:
        logger.error(f"Error getting visualization data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualization/<network_id>/data')
def get_network_visualization_data(network_id):
    """Get actual topology data for a specific network"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Use the topology visualizer to get actual network data
        from utilities.topology_visualizer import create_topology_data
        
        # Get devices and clients for the network
        devices = meraki_manager.get_devices(network_id)
        clients = meraki_manager.get_clients(network_id)
        
        # Create topology data using the existing topology visualizer
        topology_data = create_topology_data(devices, clients, [])
        
        return jsonify(topology_data)
        
    except Exception as e:
        logger.error(f"Error getting network visualization data for {network_id}: {e}")
        return jsonify({
            'error': str(e),
            'nodes': [],
            'edges': []
        }), 500

# Multi-Vendor Topology Routes
@app.route('/api/fortinet/configure', methods=['POST'])
def configure_fortinet():
    """Configure Fortinet devices for topology integration"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        data = request.get_json()
        fortigate_configs = data.get('fortigates', [])
        
        if not fortinet_manager:
            return jsonify({'error': 'Fortinet integration not available'}), 503
        
        # Clear existing configurations
        fortinet_manager.fortigate_hosts = []
        fortinet_manager.api_tokens = {}
        
        # Add new Fortigate configurations
        for config in fortigate_configs:
            host = config.get('host')
            api_token = config.get('api_token')
            name = config.get('name')
            
            if host and api_token:
                fortinet_manager.add_fortigate(host, api_token, name)
        
        return jsonify({
            'success': True,
            'message': f'Configured {len(fortigate_configs)} Fortigate devices',
            'fortigates': len(fortinet_manager.fortigate_hosts)
        })
    
    except Exception as e:
        logger.error(f"Error configuring Fortinet: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/fortinet/test', methods=['POST'])
def test_fortinet_connection():
    """Test connection to Fortinet devices"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        if not fortinet_manager:
            return jsonify({'error': 'Fortinet integration not available'}), 503
        
        results = []
        for fortigate_config in fortinet_manager.fortigate_hosts:
            test_result = fortinet_manager.test_connection(fortigate_config)
            results.append({
                'name': fortigate_config['name'],
                'host': fortigate_config['host'],
                'status': 'connected' if test_result else 'failed'
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_tested': len(results)
        })
    
    except Exception as e:
        logger.error(f"Error testing Fortinet connections: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/multi-vendor/<network_id>')
def get_multi_vendor_topology(network_id):
    """Get comprehensive multi-vendor topology including Meraki and Fortinet devices"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Get network name
        network_name = request.args.get('network_name', 'Multi-Vendor Network')
        
        # Initialize multi-vendor engine with current managers
        if multi_vendor_engine:
            multi_vendor_engine.meraki_manager = meraki_manager
            multi_vendor_engine.fortinet_manager = fortinet_manager
            
            # Build unified topology
            topology_data = multi_vendor_engine.build_unified_topology(network_id, network_name)
            
            return jsonify({
                'success': True,
                'topology': topology_data,
                'stats': topology_data.get('stats', {}),
                'vendor_stats': topology_data.get('vendor_stats', {})
            })
        else:
            return jsonify({'error': 'Multi-vendor topology engine not available'}), 503
    
    except Exception as e:
        logger.error(f"Error getting multi-vendor topology: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/multi-vendor/html/<network_id>')
def generate_multi_vendor_html(network_id):
    """Generate HTML visualization for multi-vendor topology"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        network_name = request.args.get('network_name', 'Multi-Vendor Network')
        
        if multi_vendor_engine:
            multi_vendor_engine.meraki_manager = meraki_manager
            multi_vendor_engine.fortinet_manager = fortinet_manager
            
            # Build topology data
            topology_data = multi_vendor_engine.build_unified_topology(network_id, network_name)
            
            # Generate HTML visualization
            html_path = multi_vendor_engine.generate_multi_vendor_html(topology_data)
            
            if html_path:
                return jsonify({
                    'success': True,
                    'html_path': html_path,
                    'message': 'Multi-vendor topology HTML generated successfully'
                })
            else:
                return jsonify({'error': 'Failed to generate HTML visualization'}), 500
        else:
            return jsonify({'error': 'Multi-vendor topology engine not available'}), 503
    
    except Exception as e:
        logger.error(f"Error generating multi-vendor HTML: {e}")
        return jsonify({'error': str(e)}), 500

# Swiss Army Knife Tools Routes
@app.route('/api/tools/password_generator', methods=['POST'])
def generate_password():
    """Generate secure password"""
    try:
        data = request.get_json()
        length = data.get('length', 12)
        include_symbols = data.get('symbols', True)
        
        if CLI_MODULES_AVAILABLE:
            password = tools_passgen.generate_password(length, include_symbols)
        else:
            # Fallback password generation
            import string
            import random
            chars = string.ascii_letters + string.digits
            if include_symbols:
                chars += "!@#$%^&*"
            password = ''.join(random.choice(chars) for _ in range(length))
        
        return jsonify({'password': password})
    
    except Exception as e:
        logger.error(f"Password generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools/subnet_calculator', methods=['POST'])
def calculate_subnet():
    """Calculate subnet information"""
    try:
        data = request.get_json()
        network = data.get('network')
        
        if not network:
            return jsonify({'error': 'Network address required'}), 400
        
        if CLI_MODULES_AVAILABLE:
            result = tools_subnetcalc.calculate_subnet(network)
        else:
            # Fallback subnet calculation
            import ipaddress
            net = ipaddress.IPv4Network(network, strict=False)
            result = {
                'network': str(net.network_address),
                'netmask': str(net.netmask),
                'broadcast': str(net.broadcast_address),
                'hosts': net.num_addresses - 2,
                'first_host': str(net.network_address + 1),
                'last_host': str(net.broadcast_address - 1)
            }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Subnet calculation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools/ip_check', methods=['POST'])
def check_ip():
    """Check IP address information"""
    try:
        data = request.get_json()
        ip_address = data.get('ip')
        
        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400
        
        if CLI_MODULES_AVAILABLE:
            result = tools_ipcheck.check_ip(ip_address)
        else:
            # Fallback IP check
            import ipaddress
            try:
                ip = ipaddress.ip_address(ip_address)
                result = {
                    'ip': str(ip),
                    'version': ip.version,
                    'is_private': ip.is_private,
                    'is_global': ip.is_global,
                    'is_reserved': ip.is_reserved
                }
            except ValueError:
                result = {'error': 'Invalid IP address'}
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"IP check error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools/dnsbl_check', methods=['POST'])
def check_dnsbl():
    """Check IP against DNS blacklists"""
    try:
        data = request.get_json()
        ip_address = data.get('ip')
        
        if not ip_address:
            return jsonify({'error': 'IP address required'}), 400
        
        if CLI_MODULES_AVAILABLE:
            result = dnsbl_check.check_ip(ip_address)
        else:
            # Fallback DNSBL check
            result = {
                'ip': ip_address,
                'blacklisted': False,
                'message': 'DNSBL check not available (CLI modules not loaded)'
            }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"DNSBL check error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_ssl')
def test_ssl_connection():
    """Test SSL connection for corporate environments"""
    try:
        import requests
        
        # Test connection to Meraki API
        response = requests.get('https://api.meraki.com/api/v1/organizations', 
                              headers={'X-Cisco-Meraki-API-Key': 'test'}, 
                              timeout=10)
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'ssl_working': True,
            'message': 'SSL connection successful'
        })
    
    except Exception as e:
        logger.error(f"SSL test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'ssl_working': False,
            'message': 'SSL connection failed - may need corporate SSL fixes'
        })

@app.route('/api/settings/api_mode', methods=['POST'])
def toggle_api_mode():
    """Toggle between Custom API and SDK modes"""
    try:
        data = request.get_json()
        new_mode = data.get('mode', 'custom')
        
        if new_mode not in ['custom', 'sdk']:
            return jsonify({'error': 'Invalid API mode'}), 400
        
        session['api_mode'] = new_mode
        meraki_manager.api_mode = new_mode
        
        # Re-initialize with new mode if API key exists
        if 'api_key' in session:
            meraki_manager.set_api_key(session['api_key'])
        
        return jsonify({'success': True, 'mode': new_mode})
    
    except Exception as e:
        logger.error(f"API mode toggle error: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced Visualization Routes
@app.route('/visualization/<network_id>')
def network_visualization(network_id):
    """Enhanced network visualization page"""
    # Get network name and stats for the template
    network_name = f"Network {network_id}"
    stats = {
        'devices': 0,
        'clients': 0,
        'links': 0
    }
    
    # Try to get actual stats if API key is available
    if 'api_key' in session:
        try:
            devices = meraki_manager.get_devices(network_id)
            clients = meraki_manager.get_clients(network_id)
            stats = {
                'devices': len(devices),
                'clients': len(clients),
                'links': 0  # Will be calculated by topology
            }
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
    
    return render_template('visualization.html', 
                         network_id=network_id, 
                         network_name=network_name,
                         stats=stats)

@app.route('/api/create_visualization', methods=['POST'])
def create_visualization():
    """Create a new network visualization"""
    try:
        data = request.get_json()
        network_id = data.get('network_id')
        network_name = data.get('network_name', f'Network {network_id}')
        
        if not network_id:
            return jsonify({'error': 'Network ID required'}), 400
        
        # Generate unique visualization ID
        viz_id = str(uuid.uuid4())
        
        # Get topology data
        devices = meraki_manager.get_devices(network_id)
        clients = meraki_manager.get_clients(network_id)
        
        if CLI_MODULES_AVAILABLE:
            topology_data = build_topology_from_api_data(devices, clients, links=None)
        else:
            # Fallback topology
            topology_data = {
                'nodes': [{'id': d.get('serial', d.get('id')), 'name': d.get('name', 'Unknown'), 'type': 'device'} for d in devices],
                'links': []
            }
        
        # Store visualization data
        active_visualizations[viz_id] = {
            'id': viz_id,
            'network_id': network_id,
            'network_name': network_name,
            'topology': topology_data,
            'created': datetime.now().isoformat(),
            'stats': {
                'devices': len(devices),
                'clients': len(clients),
                'links': len(topology_data.get('links', []))
            }
        }
        
        return jsonify({
            'success': True,
            'visualization_id': viz_id,
            'url': f'/visualization/{network_id}?viz_id={viz_id}'
        })
    
    except Exception as e:
        logger.error(f"Visualization creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations')
def list_visualizations():
    """List all active visualizations"""
    try:
        viz_list = []
        for viz_id, viz_data in active_visualizations.items():
            viz_list.append({
                'id': viz_id,
                'network_id': viz_data['network_id'],
                'network_name': viz_data['network_name'],
                'created': viz_data['created'],
                'stats': viz_data['stats']
            })
        
        return jsonify({'visualizations': viz_list})
    
    except Exception as e:
        logger.error(f"Visualization list error: {e}")
        return jsonify({'error': str(e)}), 500

# Device Live Tools - Speed Test and Throughput Test
@app.route('/api/devices/<device_serial>/speed_test', methods=['POST'])
def create_device_speed_test(device_serial):
    """Create a speed test for a device"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Create speed test job
        result = meraki_manager.create_speed_test(device_serial)
        
        if result:
            return jsonify({
                'success': True,
                'speed_test_id': result.get('speedTestId'),
                'status': result.get('status', 'running'),
                'url': result.get('url'),
                'message': 'Speed test initiated successfully'
            })
        else:
            return jsonify({'error': 'Failed to create speed test'}), 500
    
    except Exception as e:
        logger.error(f"Speed test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<device_serial>/speed_test/<speed_test_id>')
def get_device_speed_test_result(device_serial, speed_test_id):
    """Get speed test results for a device"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Get speed test results
        result = meraki_manager.get_speed_test_result(device_serial, speed_test_id)
        
        if result:
            return jsonify({
                'success': True,
                'speed_test_id': speed_test_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'download_mbps': result.get('results', {}).get('downloadMbps'),
                'upload_mbps': result.get('results', {}).get('uploadMbps'),
                'latency_ms': result.get('results', {}).get('latencyMs'),
                'jitter_ms': result.get('results', {}).get('jitterMs'),
                'packet_loss_percent': result.get('results', {}).get('packetLossPercent'),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'Speed test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"Speed test result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<device_serial>/throughput_test', methods=['POST'])
def create_device_throughput_test(device_serial):
    """Create a throughput test for a device"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Create throughput test job
        result = meraki_manager.create_throughput_test(device_serial)
        
        if result:
            return jsonify({
                'success': True,
                'throughput_test_id': result.get('throughputTestId'),
                'status': result.get('status', 'running'),
                'url': result.get('url'),
                'message': 'Throughput test initiated successfully'
            })
        else:
            return jsonify({'error': 'Failed to create throughput test'}), 500
    
    except Exception as e:
        logger.error(f"Throughput test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<device_serial>/throughput_test/<throughput_test_id>')
def get_device_throughput_test_result(device_serial, throughput_test_id):
    """Get throughput test results for a device"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Get throughput test results
        result = meraki_manager.get_throughput_test_result(device_serial, throughput_test_id)
        
        if result:
            return jsonify({
                'success': True,
                'throughput_test_id': throughput_test_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'throughput_mbps': result.get('results', {}).get('throughputMbps'),
                'interface': result.get('results', {}).get('interface'),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'Throughput test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"Throughput test result error: {e}")
        return jsonify({'error': str(e)}), 500

# Additional Live Tools Endpoints

@app.route('/api/devices/<serial>/arp_table', methods=['POST'])
def create_arp_table_test(serial):
    """Create ARP table live tool job"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.create_arp_table_test(serial)
        if result:
            return jsonify({
                'success': True,
                'arp_table_id': result.get('arpTableId'),
                'status': result.get('status'),
                'created_at': result.get('createdAt')
            })
        else:
            return jsonify({'error': 'Failed to create ARP table test'}), 500
    
    except Exception as e:
        logger.error(f"ARP table test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/arp_table/<arp_table_id>')
def get_arp_table_results(serial, arp_table_id):
    """Get ARP table test results"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.get_arp_table_results(serial, arp_table_id)
        if result:
            return jsonify({
                'success': True,
                'arp_table_id': arp_table_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'entries': result.get('results', {}).get('entries', []),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'ARP table test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"ARP table result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/mac_table', methods=['POST'])
def create_mac_table_test(serial):
    """Create MAC table live tool job"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.create_mac_table_test(serial)
        if result:
            return jsonify({
                'success': True,
                'mac_table_id': result.get('macTableId'),
                'status': result.get('status'),
                'created_at': result.get('createdAt')
            })
        else:
            return jsonify({'error': 'Failed to create MAC table test'}), 500
    
    except Exception as e:
        logger.error(f"MAC table test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/mac_table/<mac_table_id>')
def get_mac_table_results(serial, mac_table_id):
    """Get MAC table test results"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.get_mac_table_results(serial, mac_table_id)
        if result:
            return jsonify({
                'success': True,
                'mac_table_id': mac_table_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'entries': result.get('results', {}).get('entries', []),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'MAC table test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"MAC table result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/ping', methods=['POST'])
def create_ping_test(serial):
    """Create ping live tool job"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        data = request.get_json() or {}
        target = data.get('target', '8.8.8.8')  # Default to Google DNS
        count = data.get('count', 5)
        
        result = meraki_manager.create_ping_test(serial, target, count)
        if result:
            return jsonify({
                'success': True,
                'ping_id': result.get('pingId'),
                'status': result.get('status'),
                'target': target,
                'count': count,
                'created_at': result.get('createdAt')
            })
        else:
            return jsonify({'error': 'Failed to create ping test'}), 500
    
    except Exception as e:
        logger.error(f"Ping test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/ping/<ping_id>')
def get_ping_results(serial, ping_id):
    """Get ping test results"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.get_ping_results(serial, ping_id)
        if result:
            return jsonify({
                'success': True,
                'ping_id': ping_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'target': result.get('results', {}).get('target'),
                'sent': result.get('results', {}).get('sent'),
                'received': result.get('results', {}).get('received'),
                'loss_percent': result.get('results', {}).get('lossPercent'),
                'latencies': result.get('results', {}).get('latencies', []),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'Ping test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"Ping result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/routing_table', methods=['POST'])
def create_routing_table_test(serial):
    """Create routing table live tool job"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.create_routing_table_test(serial)
        if result:
            return jsonify({
                'success': True,
                'routing_table_id': result.get('routingTableId'),
                'status': result.get('status'),
                'created_at': result.get('createdAt')
            })
        else:
            return jsonify({'error': 'Failed to create routing table test'}), 500
    
    except Exception as e:
        logger.error(f"Routing table test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/routing_table/<routing_table_id>')
def get_routing_table_results(serial, routing_table_id):
    """Get routing table test results"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.get_routing_table_results(serial, routing_table_id)
        if result:
            return jsonify({
                'success': True,
                'routing_table_id': routing_table_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'entries': result.get('results', {}).get('entries', []),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'Routing table test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"Routing table result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/cycle_port', methods=['POST'])
def create_cycle_port_test(serial):
    """Create cycle port live tool job"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        data = request.get_json() or {}
        ports = data.get('ports', [])
        
        if not ports:
            return jsonify({'error': 'Ports parameter is required'}), 400
        
        result = meraki_manager.create_cycle_port_test(serial, ports)
        if result:
            return jsonify({
                'success': True,
                'cycle_port_id': result.get('cyclePortId'),
                'status': result.get('status'),
                'ports': ports,
                'created_at': result.get('createdAt')
            })
        else:
            return jsonify({'error': 'Failed to create cycle port test'}), 500
    
    except Exception as e:
        logger.error(f"Cycle port test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/cycle_port/<cycle_port_id>')
def get_cycle_port_results(serial, cycle_port_id):
    """Get cycle port test results"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.get_cycle_port_results(serial, cycle_port_id)
        if result:
            return jsonify({
                'success': True,
                'cycle_port_id': cycle_port_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'ports': result.get('results', {}).get('ports', []),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'Cycle port test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"Cycle port result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/ospf_neighbors', methods=['POST'])
def create_ospf_neighbors_test(serial):
    """Create OSPF neighbors live tool job"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.create_ospf_neighbors_test(serial)
        if result:
            return jsonify({
                'success': True,
                'ospf_neighbors_id': result.get('ospfNeighborsId'),
                'status': result.get('status'),
                'created_at': result.get('createdAt')
            })
        else:
            return jsonify({'error': 'Failed to create OSPF neighbors test'}), 500
    
    except Exception as e:
        logger.error(f"OSPF neighbors test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/ospf_neighbors/<ospf_neighbors_id>')
def get_ospf_neighbors_results(serial, ospf_neighbors_id):
    """Get OSPF neighbors test results"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.get_ospf_neighbors_results(serial, ospf_neighbors_id)
        if result:
            return jsonify({
                'success': True,
                'ospf_neighbors_id': ospf_neighbors_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'neighbors': result.get('results', {}).get('neighbors', []),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'OSPF neighbors test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"OSPF neighbors result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/dhcp_leases', methods=['POST'])
def create_dhcp_leases_test(serial):
    """Create DHCP leases live tool job"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.create_dhcp_leases_test(serial)
        if result:
            return jsonify({
                'success': True,
                'dhcp_leases_id': result.get('dhcpLeasesId'),
                'status': result.get('status'),
                'created_at': result.get('createdAt')
            })
        else:
            return jsonify({'error': 'Failed to create DHCP leases test'}), 500
    
    except Exception as e:
        logger.error(f"DHCP leases test creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<serial>/dhcp_leases/<dhcp_leases_id>')
def get_dhcp_leases_results(serial, dhcp_leases_id):
    """Get DHCP leases test results"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        result = meraki_manager.get_dhcp_leases_results(serial, dhcp_leases_id)
        if result:
            return jsonify({
                'success': True,
                'dhcp_leases_id': dhcp_leases_id,
                'status': result.get('status'),
                'results': result.get('results', {}),
                'leases': result.get('results', {}).get('leases', []),
                'created_at': result.get('createdAt'),
                'completed_at': result.get('completedAt')
            })
        else:
            return jsonify({'error': 'DHCP leases test not found or failed'}), 404
    
    except Exception as e:
        logger.error(f"DHCP leases result error: {e}")
        return jsonify({'error': str(e)}), 500

# Network Status and Monitoring
@app.route('/api/network_status/<network_id>')
def get_network_status(network_id):
    """Get comprehensive network status"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Get network information
        devices = meraki_manager.get_devices(network_id)
        clients = meraki_manager.get_clients(network_id)
        
        # Calculate status metrics
        online_devices = len([d for d in devices if d.get('status') == 'online'])
        total_devices = len(devices)
        active_clients = len([c for c in clients if c.get('status') == 'Online'])
        
        status_data = {
            'network_id': network_id,
            'devices': {
                'total': total_devices,
                'online': online_devices,
                'offline': total_devices - online_devices,
                'details': devices
            },
            'clients': {
                'total': len(clients),
                'active': active_clients,
                'details': clients
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(status_data)
    
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[STARTING] Comprehensive Cisco Meraki Web Management Interface")
    print("=" * 70)
    print("[OK] Integrates ALL CLI functionality into modern web interface")
    print("[FEATURES] Network Status, Device Management, Topology, Tools, Settings")
    print("[ACCESS] http://localhost:5000")
    
    if CLI_MODULES_AVAILABLE:
        print("[OK] All CLI modules loaded - Full functionality available")
    else:
        print("[WARNING] Some CLI modules missing - Limited functionality")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
