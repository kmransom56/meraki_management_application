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

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Environment variables loaded from .env file")
except ImportError:
    print("[INFO] python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"[WARNING] Could not load .env file: {e}")

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

# Import FortiGate integration
try:
    from modules.fortigate import FortiManagerAPI, FortiGateDirectAPI, build_fortigate_topology_data
    FORTIGATE_AVAILABLE = True
    print("[OK] FortiGate integration modules loaded")
except ImportError as e:
    print(f"[WARNING] FortiGate modules not available: {e}")
    FORTIGATE_AVAILABLE = False

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

# Import QSR device classifier
try:
    from qsr_device_classifier import QSRDeviceClassifier
    QSR_CLASSIFIER_AVAILABLE = True
    print("[OK] QSR device classifier loaded")
except ImportError as e:
    print(f"[WARNING] QSR device classifier not available: {e}")
    QSR_CLASSIFIER_AVAILABLE = False

# Import persistent API key storage
try:
    from api_key_storage import APIKeyStorage, load_meraki_api_key, save_meraki_api_key
    API_KEY_STORAGE_AVAILABLE = True
    print("[OK] Persistent API key storage loaded")
except ImportError as e:
    print(f"[WARNING] API key storage not available: {e}")
    API_KEY_STORAGE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Professional-grade application configuration
app_config = {
    'flask_host': os.environ.get('FLASK_HOST', '0.0.0.0'),
    'flask_port': int(os.environ.get('FLASK_PORT', 10000)),
    'flask_debug': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
    'meraki_api_key': os.environ.get('MERAKI_API_KEY', ''),
    'fortigate_devices': os.environ.get('FORTIGATE_DEVICES', ''),
    'fortimanager_host': os.environ.get('FORTIMANAGER_HOST', ''),
    'qsr_mode': os.environ.get('QSR_MODE', 'True').lower() == 'true',
    'qsr_location_name': os.environ.get('QSR_LOCATION_NAME', 'Restaurant Location')
}

# Auto-load saved API key if available
if API_KEY_STORAGE_AVAILABLE and not app_config['meraki_api_key']:
    saved_key = load_meraki_api_key()
    if saved_key:
        app_config['meraki_api_key'] = saved_key
        print("[CONFIG] Auto-loaded Meraki API key from persistent storage")

# Initialize Flask app with professional-grade configuration
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# Professional-grade Flask configuration
app.config.update({
    'SESSION_TYPE': 'filesystem',
    'SESSION_PERMANENT': False,
    'SESSION_USE_SIGNER': True,
    'SESSION_KEY_PREFIX': 'meraki_',
    'TEMPLATES_AUTO_RELOAD': True,
    'SEND_FILE_MAX_AGE_DEFAULT': 0,
    'JSON_SORT_KEYS': False,
    'JSONIFY_PRETTYPRINT_REGULAR': True
})

# Force template reloading and disable caching for development
app.jinja_env.auto_reload = True
app.jinja_env.cache = {}

# Add professional-grade cache-busting headers
@app.after_request
def add_cache_busting_headers(response):
    """Add cache-busting headers to prevent browser caching issues"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Timestamp'] = str(int(time.time()))
    return response

# Global storage for active visualizations and data
active_visualizations = {}
cached_data = {}

# =============================================================================
# PROFESSIONAL-GRADE WEB PAGE ROUTES
# =============================================================================

@app.route('/')
def index():
    """Main dashboard page with professional UI"""
    timestamp = int(time.time())
    return render_template('index.html', 
                         timestamp=timestamp,
                         cache_bust=timestamp,
                         qsr_mode=app_config['qsr_mode'],
                         location_name=app_config['qsr_location_name'])

@app.route('/visualization/<network_id>')
def visualization_page(network_id):
    """Enhanced network topology visualization page"""
    timestamp = int(time.time())
    return render_template('visualization.html', 
                         network_id=network_id,
                         timestamp=timestamp,
                         cache_bust=timestamp,
                         qsr_mode=app_config['qsr_mode'])

@app.route('/device_inventory/<network_id>')
def device_inventory_page(network_id):
    """Comprehensive device inventory page"""
    timestamp = int(time.time())
    return render_template('device_inventory.html', 
                         network_id=network_id,
                         timestamp=timestamp,
                         cache_bust=timestamp)

@app.route('/ai_maintenance')
def ai_maintenance_dashboard():
    """AI maintenance engine dashboard"""
    timestamp = int(time.time())
    return render_template('ai_maintenance.html',
                         timestamp=timestamp,
                         cache_bust=timestamp)

@app.route('/settings')
def settings_page():
    """Application settings and configuration"""
    timestamp = int(time.time())
    return render_template('settings.html',
                         timestamp=timestamp,
                         cache_bust=timestamp,
                         api_key_storage_available=API_KEY_STORAGE_AVAILABLE)

# =============================================================================
# GLOBAL MANAGER INITIALIZATION
# =============================================================================

# Initialize global Meraki manager
meraki_manager = None

def initialize_meraki_manager():
    """Initialize global Meraki manager with auto-loaded API key"""
    global meraki_manager
    try:
        meraki_manager = ComprehensiveMerakiManager()
        
        # Auto-set API key if available
        if app_config['meraki_api_key']:
            meraki_manager.set_api_key(app_config['meraki_api_key'])
            logger.info("Meraki manager initialized with auto-loaded API key")
        else:
            logger.info("Meraki manager initialized - API key will be set via web interface")
            
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Meraki manager: {e}")
        return False

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

# Load configuration from environment variables
def load_config_from_env():
    """Load configuration from environment variables"""
    config = {}
    
    # Meraki configuration
    config['meraki_api_key'] = os.getenv('MERAKI_API_KEY')
    config['meraki_base_url'] = os.getenv('MERAKI_BASE_URL', 'https://api.meraki.com/api/v1')
    config['meraki_api_mode'] = os.getenv('MERAKI_API_MODE', 'custom')
    
    # FortiGate configuration
    config['fortimanager_host'] = os.getenv('FORTIMANAGER_HOST')
    config['fortimanager_username'] = os.getenv('FORTIMANAGER_USERNAME')
    config['fortimanager_password'] = os.getenv('FORTIMANAGER_PASSWORD')
    
    # Parse FortiGate devices from JSON string
    fortigate_devices_str = os.getenv('FORTIGATE_DEVICES', '[]')
    try:
        config['fortigate_devices'] = json.loads(fortigate_devices_str)
    except json.JSONDecodeError:
        config['fortigate_devices'] = []
    
    # Flask configuration
    config['flask_host'] = os.getenv('FLASK_HOST', '0.0.0.0')
    config['flask_port'] = int(os.getenv('FLASK_PORT', 5000))
    config['flask_debug'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    config['flask_secret_key'] = os.getenv('FLASK_SECRET_KEY')
    
    # Application settings
    config['log_level'] = os.getenv('LOG_LEVEL', 'INFO')
    config['ssl_verify'] = os.getenv('SSL_VERIFY', 'True').lower() == 'true'
    config['request_timeout'] = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    # QSR settings
    config['qsr_mode'] = os.getenv('QSR_MODE', 'True').lower() == 'true'
    config['qsr_location_name'] = os.getenv('QSR_LOCATION_NAME', 'Restaurant Location')
    
    return config

# Load configuration
app_config = load_config_from_env()

# Configure Flask app with environment variables
if app_config['flask_secret_key']:
    app.secret_key = app_config['flask_secret_key']
else:
    app.secret_key = os.urandom(24)

# Configure logging level
log_level = getattr(logging, app_config['log_level'].upper(), logging.INFO)
logging.getLogger().setLevel(log_level)

# Global manager instance
meraki_manager = ComprehensiveMerakiManager()

# Auto-configure API key from environment if available
if app_config['meraki_api_key']:
    print(f"[CONFIG] Auto-configuring Meraki API key from environment")
    meraki_manager.api_mode = app_config['meraki_api_mode']
    if meraki_manager.set_api_key(app_config['meraki_api_key']):
        print("[OK] Meraki API key configured successfully from environment")
        # Session will be configured when the web interface is accessed
    else:
        print("[WARNING] Failed to validate Meraki API key from environment")

# Auto-configure FortiGate devices from environment if available
if FORTIGATE_AVAILABLE:
    # Configure FortiManager if provided
    if app_config['fortimanager_host'] and app_config['fortimanager_username'] and app_config['fortimanager_password']:
        print("[CONFIG] Auto-configuring FortiManager from environment")
        session['fortimanager_config'] = {
            'host': app_config['fortimanager_host'],
            'username': app_config['fortimanager_username'],
            'password': app_config['fortimanager_password']
        }
        print("[OK] FortiManager configuration loaded from environment")
    
    # Configure direct FortiGate devices if provided
    if app_config['fortigate_devices']:
        print(f"[CONFIG] Auto-configuring {len(app_config['fortigate_devices'])} FortiGate devices from environment")
        session['fortigate_configs'] = app_config['fortigate_devices']
        print("[OK] FortiGate device configurations loaded from environment")

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
        from utilities.topology_visualizer import build_topology_from_api_data
        
        # Get devices and clients for the network
        devices = meraki_manager.get_devices(network_id)
        clients = meraki_manager.get_clients(network_id)
        
        logger.info(f"Retrieved {len(devices)} devices and {len(clients)} clients for network {network_id}")
        
        # Create topology data using the existing topology visualizer
        topology_data = build_topology_from_api_data(devices, clients, [])
        
        logger.info(f"Built topology with {len(topology_data.get('nodes', []))} nodes and {len(topology_data.get('links', []))} links")
        
        # Convert topology data to D3.js format
        d3_nodes = []
        d3_edges = []
        
        # Process nodes for D3.js
        for node in topology_data.get('nodes', []):
            device_type = node.get('type', 'unknown')
            
            # Map device types to groups and colors
            if device_type == 'appliance':
                group = 'appliance'
                size = 12
            elif device_type == 'switch':
                group = 'switch'
                size = 10
            elif device_type == 'wireless':
                group = 'wireless'
                size = 10
            elif device_type == 'client':
                group = 'client'
                size = 6
            else:
                group = 'unknown'
                size = 8
            
            # Create D3.js node
            d3_node = {
                'id': node['id'],
                'label': node.get('label', node['id']),
                'group': group,
                'size': size,
                'title': f"<b>{node.get('label', 'Unknown')}</b><br>" +
                        f"Type: {device_type}<br>" +
                        f"IP: {node.get('ip', 'Unknown')}<br>" +
                        f"Status: {node.get('status', 'Unknown')}"
            }
            d3_nodes.append(d3_node)
        
        # Process links/edges for D3.js
        for link in topology_data.get('links', []):
            connection_type = link.get('type', 'unknown')
            
            # Map connection types
            if connection_type == 'uplink':
                edge_type = 'uplink'
                width = 3
            elif connection_type == 'switch':
                edge_type = 'switch'
                width = 2
            elif connection_type == 'wireless':
                edge_type = 'wireless'
                width = 2
            elif connection_type == 'wired':
                edge_type = 'wired'
                width = 1
            else:
                edge_type = 'unknown'
                width = 1
            
            # Create D3.js edge
            d3_edge = {
                'source': link['source'],
                'target': link['target'],
                'type': edge_type,
                'width': width,
                'dashes': connection_type == 'wireless'
            }
            d3_edges.append(d3_edge)
        
        # Return D3.js formatted data
        d3_data = {
            'nodes': d3_nodes,
            'edges': d3_edges
        }
        
        logger.info(f"Returning D3.js data with {len(d3_nodes)} nodes and {len(d3_edges)} edges")
        
        return jsonify(d3_data)
        
    except Exception as e:
        logger.error(f"Error getting network visualization data for {network_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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

# FortiGate Integration Routes
@app.route('/api/fortigate/configure', methods=['POST'])
def configure_fortigate():
    """Configure FortiGate devices for topology integration"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        if not FORTIGATE_AVAILABLE:
            return jsonify({'error': 'FortiGate integration not available'}), 503
        
        data = request.get_json()
        config_type = data.get('type', 'direct')  # 'direct' or 'manager'
        
        if config_type == 'manager':
            # FortiManager configuration
            host = data.get('host')
            username = data.get('username')
            password = data.get('password')
            
            if not all([host, username, password]):
                return jsonify({'error': 'Host, username, and password required for FortiManager'}), 400
            
            # Store FortiManager config in session
            session['fortimanager_config'] = {
                'host': host,
                'username': username,
                'password': password
            }
            
            # Test connection
            fm = FortiManagerAPI(host, username, password)
            if fm.login():
                devices = fm.get_managed_devices()
                fm.logout()
                
                return jsonify({
                    'success': True,
                    'type': 'manager',
                    'message': f'FortiManager configured successfully. Found {len(devices)} devices.',
                    'devices': len(devices)
                })
            else:
                return jsonify({'error': 'Failed to connect to FortiManager'}), 400
                
        else:
            # Direct FortiGate configuration
            fortigate_configs = data.get('fortigates', [])
            
            if not fortigate_configs:
                return jsonify({'error': 'At least one FortiGate configuration required'}), 400
            
            # Store FortiGate configs in session
            session['fortigate_configs'] = fortigate_configs
            
            # Test connections
            successful_connections = 0
            for config in fortigate_configs:
                host = config.get('host')
                api_key = config.get('api_key')
                
                if host and api_key:
                    fg = FortiGateDirectAPI(host, api_key)
                    status = fg.get_system_status()
                    if status:
                        successful_connections += 1
            
            return jsonify({
                'success': True,
                'type': 'direct',
                'message': f'Configured {len(fortigate_configs)} FortiGate devices. {successful_connections} connected successfully.',
                'total': len(fortigate_configs),
                'connected': successful_connections
            })
    
    except Exception as e:
        logger.error(f"Error configuring FortiGate: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/fortigate/test', methods=['POST'])
def test_fortigate_connection():
    """Test connection to FortiGate devices"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        if not FORTIGATE_AVAILABLE:
            return jsonify({'error': 'FortiGate integration not available'}), 503
        
        results = []
        
        # Test FortiManager if configured
        if 'fortimanager_config' in session:
            config = session['fortimanager_config']
            fm = FortiManagerAPI(config['host'], config['username'], config['password'])
            
            if fm.login():
                devices = fm.get_managed_devices()
                fm.logout()
                
                results.append({
                    'type': 'FortiManager',
                    'host': config['host'],
                    'status': 'connected',
                    'devices': len(devices)
                })
            else:
                results.append({
                    'type': 'FortiManager',
                    'host': config['host'],
                    'status': 'failed',
                    'devices': 0
                })
        
        # Test direct FortiGate connections if configured
        if 'fortigate_configs' in session:
            for config in session['fortigate_configs']:
                host = config.get('host')
                api_key = config.get('api_key')
                name = config.get('name', host)
                
                if host and api_key:
                    fg = FortiGateDirectAPI(host, api_key)
                    status = fg.get_system_status()
                    
                    results.append({
                        'type': 'FortiGate',
                        'name': name,
                        'host': host,
                        'status': 'connected' if status else 'failed'
                    })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_tested': len(results)
        })
    
    except Exception as e:
        logger.error(f"Error testing FortiGate connections: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/fortigate/devices')
def get_fortigate_devices():
    """Get FortiGate devices from configured sources"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        if not FORTIGATE_AVAILABLE:
            return jsonify({'error': 'FortiGate integration not available'}), 503
        
        all_devices = []
        
        # Get devices from FortiManager if configured
        if 'fortimanager_config' in session:
            config = session['fortimanager_config']
            fm = FortiManagerAPI(config['host'], config['username'], config['password'])
            
            if fm.login():
                devices = fm.get_managed_devices()
                
                # Add interfaces for each device
                for device in devices:
                    device_name = device.get('name')
                    if device_name:
                        interfaces = fm.get_device_interfaces(device_name)
                        device['interfaces'] = interfaces
                
                all_devices.extend(devices)
                fm.logout()
        
        # Get devices from direct FortiGate connections if configured
        if 'fortigate_configs' in session:
            for config in session['fortigate_configs']:
                host = config.get('host')
                api_key = config.get('api_key')
                name = config.get('name', host)
                
                if host and api_key:
                    fg = FortiGateDirectAPI(host, api_key)
                    status = fg.get_system_status()
                    
                    if status:
                        # Create device object from status
                        device = {
                            'name': name,
                            'host': host,
                            'serial': status.get('results', {}).get('serial', 'unknown'),
                            'platform_str': status.get('results', {}).get('version', 'unknown'),
                            'os_ver': status.get('results', {}).get('version', 'unknown'),
                            'interfaces': fg.get_interfaces()
                        }
                        all_devices.append(device)
        
        return jsonify({
            'success': True,
            'devices': all_devices,
            'total': len(all_devices)
        })
    
    except Exception as e:
        logger.error(f"Error getting FortiGate devices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualization/<network_id>/multi-vendor/data')
def get_multi_vendor_visualization_data(network_id):
    """Get multi-vendor topology data including FortiGate and Meraki devices with QSR device classification"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        # Initialize QSR device classifier
        qsr_classifier = None
        if QSR_CLASSIFIER_AVAILABLE:
            qsr_classifier = QSRDeviceClassifier()
            logger.info("QSR device classifier initialized for restaurant device identification")
        
        # Get Meraki devices and clients
        meraki_devices = meraki_manager.get_devices(network_id)
        meraki_clients = meraki_manager.get_clients(network_id)
        
        # Get FortiGate devices if available
        fortigate_devices = []
        if FORTIGATE_AVAILABLE:
            # Get devices from FortiManager if configured
            if 'fortimanager_config' in session:
                config = session['fortimanager_config']
                fm = FortiManagerAPI(config['host'], config['username'], config['password'])
                
                if fm.login():
                    devices = fm.get_managed_devices()
                    
                    # Add interfaces for each device
                    for device in devices:
                        device_name = device.get('name')
                        if device_name:
                            interfaces = fm.get_device_interfaces(device_name)
                            device['interfaces'] = interfaces
                    
                    fortigate_devices.extend(devices)
                    fm.logout()
            
            # Get devices from direct FortiGate connections if configured
            if 'fortigate_configs' in session:
                for config in session['fortigate_configs']:
                    host = config.get('host')
                    api_key = config.get('api_key')
                    name = config.get('name', host)
                    
                    if host and api_key:
                        fg = FortiGateDirectAPI(host, api_key)
                        status = fg.get_system_status()
                        
                        if status:
                            # Create device object from status
                            device = {
                                'name': name,
                                'host': host,
                                'serial': status.get('results', {}).get('serial', 'unknown'),
                                'platform_str': status.get('results', {}).get('version', 'unknown'),
                                'os_ver': status.get('results', {}).get('version', 'unknown'),
                                'interfaces': fg.get_interfaces()
                            }
                            fortigate_devices.append(device)
        
        logger.info(f"Retrieved {len(meraki_devices)} Meraki devices, {len(fortigate_devices)} FortiGate devices, and {len(meraki_clients)} clients")
        
        # Build topology data with QSR device classification
        topology_data = {
            'nodes': [],
            'edges': [],
            'stats': {},
            'qsr_stats': {}
        }
        
        classified_devices = []
        
        # Process Meraki devices
        for device in meraki_devices:
            device_info = {
                'name': device.get('name', ''),
                'mac': device.get('mac', ''),
                'model': device.get('model', ''),
                'productType': device.get('productType', ''),
                'serial': device.get('serial', ''),
                'networkId': device.get('networkId', ''),
                'status': device.get('status', 'unknown')
            }
            
            # Classify device using QSR classifier
            if qsr_classifier:
                classification = qsr_classifier.classify_device(device_info)
            else:
                # Fallback classification
                product_type = device.get('productType', '').lower()
                if 'switch' in product_type:
                    classification = {'device_type': 'network_switch', 'category': 'Network Infrastructure', 'icon': 'fas fa-network-wired', 'color': '#28A745', 'display_name': 'Network Switch'}
                elif 'wireless' in product_type:
                    classification = {'device_type': 'wifi_access_point', 'category': 'Network Infrastructure', 'icon': 'fas fa-wifi', 'color': '#FD7E14', 'display_name': 'WiFi Access Point'}
                elif 'appliance' in product_type:
                    classification = {'device_type': 'security_appliance', 'category': 'Security & Routing', 'icon': 'fas fa-shield-alt', 'color': '#DC3545', 'display_name': 'Security Appliance'}
                elif 'camera' in product_type:
                    classification = {'device_type': 'security_camera', 'category': 'Security Systems', 'icon': 'fas fa-video', 'color': '#6C757D', 'display_name': 'Security Camera'}
                else:
                    classification = {'device_type': 'unknown', 'category': 'Unknown Device', 'icon': 'fas fa-question-circle', 'color': '#9E9E9E', 'display_name': 'Unknown Device'}
            
            # Create node for visualization
            node = {
                'id': f"meraki_{device.get('serial', 'unknown')}",
                'label': classification.get('display_name', device.get('name', 'Unknown')),
                'group': classification.get('device_type', 'unknown'),
                'size': 12 if classification.get('device_type') in ['security_appliance', 'digital_menu'] else 10,
                'title': f"<b>{classification.get('display_name', 'Unknown')}</b><br>" +
                        f"Category: {classification.get('category', 'Unknown')}<br>" +
                        f"Model: {device.get('model', 'Unknown')}<br>" +
                        f"Serial: {device.get('serial', 'Unknown')}<br>" +
                        f"Status: {device.get('status', 'Unknown')}<br>" +
                        f"IP: {device.get('lanIp', 'Unknown')}"
            }
            topology_data['nodes'].append(node)
            
            # Store classified device for statistics
            classified_devices.append({
                'device_info': device_info,
                'classification': classification
            })
        
        # Process FortiGate devices
        for device in fortigate_devices:
            device_info = {
                'name': device.get('name', ''),
                'mac': '',  # FortiGate MAC not always available
                'model': 'fortigate',
                'productType': 'fortigate',
                'serial': device.get('serial', ''),
                'host': device.get('host', ''),
                'status': 'online'  # Assume online if we can query it
            }
            
            # Classify FortiGate device
            if qsr_classifier:
                classification = qsr_classifier.classify_device(device_info)
            else:
                classification = {'device_type': 'security_appliance', 'category': 'Security & Routing', 'icon': 'fas fa-shield-alt', 'color': '#DC3545', 'display_name': 'FortiGate Firewall'}
            
            # Create node for visualization
            node = {
                'id': f"fortigate_{device.get('serial', device.get('name', 'unknown'))}",
                'label': classification.get('display_name', device.get('name', 'FortiGate')),
                'group': classification.get('device_type', 'security_appliance'),
                'size': 14,  # FortiGates are typically central devices
                'title': f"<b>{classification.get('display_name', 'FortiGate')}</b><br>" +
                        f"Category: {classification.get('category', 'Security & Routing')}<br>" +
                        f"Host: {device.get('host', 'Unknown')}<br>" +
                        f"Serial: {device.get('serial', 'Unknown')}<br>" +
                        f"Platform: {device.get('platform_str', 'Unknown')}"
            }
            topology_data['nodes'].append(node)
            
            # Store classified device for statistics
            classified_devices.append({
                'device_info': device_info,
                'classification': classification
            })
        
        # Process clients with QSR classification
        for client in meraki_clients:
            client_info = {
                'name': client.get('description', client.get('mac', '')),
                'mac': client.get('mac', ''),
                'model': client.get('manufacturer', '').lower(),
                'productType': 'client',
                'ip': client.get('ip', ''),
                'status': client.get('status', 'unknown')
            }
            
            # Classify client device
            if qsr_classifier:
                classification = qsr_classifier.classify_device(client_info)
            else:
                classification = {'device_type': 'unknown', 'category': 'Client Device', 'icon': 'fas fa-laptop', 'color': '#6C757D', 'display_name': 'Client Device'}
            
            # Create client node
            client_node = {
                'id': f"client_{client.get('id', client.get('mac', 'unknown'))}",
                'label': classification.get('display_name', client.get('description', 'Unknown Client')),
                'group': classification.get('device_type', 'unknown'),
                'size': 8 if classification.get('device_type') in ['pos_register', 'pos_tablet', 'kitchen_display'] else 6,
                'title': f"<b>{classification.get('display_name', 'Client Device')}</b><br>" +
                        f"Category: {classification.get('category', 'Client Device')}<br>" +
                        f"MAC: {client.get('mac', 'Unknown')}<br>" +
                        f"IP: {client.get('ip', 'Unknown')}<br>" +
                        f"VLAN: {client.get('vlan', 'Unknown')}<br>" +
                        f"Manufacturer: {client.get('manufacturer', 'Unknown')}"
            }
            topology_data['nodes'].append(client_node)
            
            # Store classified client for statistics
            classified_devices.append({
                'device_info': client_info,
                'classification': classification
            })
            
            # Connect client to appropriate device (simplified logic)
            if meraki_devices:
                # Connect to first switch or AP
                target_device = None
                connection_type = 'wired'
                
                for device in meraki_devices:
                    device_type = device.get('productType', '').lower()
                    if 'switch' in device_type:
                        target_device = f"meraki_{device.get('serial', 'unknown')}"
                        connection_type = 'wired'
                        break
                    elif 'wireless' in device_type:
                        target_device = f"meraki_{device.get('serial', 'unknown')}"
                        connection_type = 'wireless'
                
                if target_device:
                    edge = {
                        'source': target_device,
                        'target': client_node['id'],
                        'type': connection_type,
                        'width': 1,
                        'dashes': connection_type == 'wireless'
                    }
                    topology_data['edges'].append(edge)
        
        # Create connections between infrastructure devices
        # Connect FortiGate to Meraki appliances (uplink)
        fortigate_nodes = [n for n in topology_data['nodes'] if n['group'] == 'security_appliance' and 'fortigate' in n['id']]
        meraki_appliances = [n for n in topology_data['nodes'] if n['group'] == 'security_appliance' and 'meraki' in n['id']]
        
        for fg_node in fortigate_nodes:
            for mx_node in meraki_appliances:
                edge = {
                    'source': fg_node['id'],
                    'target': mx_node['id'],
                    'type': 'uplink',
                    'width': 3
                }
                topology_data['edges'].append(edge)
        
        # Connect appliances to switches
        switches = [n for n in topology_data['nodes'] if n['group'] == 'network_switch']
        for appliance in meraki_appliances:
            for switch in switches:
                edge = {
                    'source': appliance['id'],
                    'target': switch['id'],
                    'type': 'switch',
                    'width': 2
                }
                topology_data['edges'].append(edge)
        
        # Generate QSR statistics
        if qsr_classifier:
            qsr_stats = qsr_classifier.get_qsr_statistics(classified_devices)
            recommendations = qsr_classifier.get_device_recommendations(classified_devices)
            topology_data['qsr_stats'] = qsr_stats
            topology_data['recommendations'] = recommendations
        
        # Update general stats
        topology_data['stats'] = {
            'devices': len([n for n in topology_data['nodes'] if not n['id'].startswith('client_')]),
            'clients': len([n for n in topology_data['nodes'] if n['id'].startswith('client_')]),
            'nodes': len(topology_data['nodes']),
            'edges': len(topology_data['edges'])
        }
        
        logger.info(f"Built QSR multi-vendor topology with {len(topology_data['nodes'])} nodes and {len(topology_data['edges'])} edges")
        
        return jsonify(topology_data)
        
    except Exception as e:
        logger.error(f"Error getting multi-vendor visualization data: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'nodes': [],
            'edges': []
        }), 500

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
    print(f"[ACCESS] http://{app_config['flask_host']}:{app_config['flask_port']}")
    
    # Initialize managers
    print("[INIT] Initializing application managers...")
    if initialize_meraki_manager():
        print("[OK] Meraki manager initialized successfully")
    else:
        print("[WARNING] Meraki manager initialization failed")
    
    # Module availability status
    if CLI_MODULES_AVAILABLE:
        print("[OK] All CLI modules loaded - Full functionality available")
    else:
        print("[WARNING] Some CLI modules missing - Limited functionality")
    
    # API key status
    if app_config['meraki_api_key']:
        if API_KEY_STORAGE_AVAILABLE:
            print("[CONFIG] Meraki API key auto-loaded from persistent storage")
        else:
            print("[CONFIG] Meraki API key loaded from environment")
    else:
        print("[INFO] No Meraki API key found - configure via web interface")
        if API_KEY_STORAGE_AVAILABLE:
            print("[HINT] Use 'python setup_api_key.py' to save your API key permanently")
    
    # Integration status
    if app_config['fortigate_devices'] or app_config['fortimanager_host']:
        print("[CONFIG] FortiGate integration configured from environment")
    
    if app_config['qsr_mode']:
        print(f"[QSR] Restaurant mode enabled for: {app_config['qsr_location_name']}")
    
    # Feature availability
    features = []
    if QSR_CLASSIFIER_AVAILABLE:
        features.append("QSR Device Classification")
    if FORTIGATE_AVAILABLE:
        features.append("FortiGate Integration")
    if API_KEY_STORAGE_AVAILABLE:
        features.append("Persistent API Key Storage")
    
    if features:
        print(f"[FEATURES] Enhanced features available: {', '.join(features)}")
    
    print("=" * 70)
    print("[READY] Professional-grade network management platform ready")
    print("[CACHE] Cache-busting enabled for development")
    print("[SECURITY] Session management and API key encryption active")
    print("=" * 70)
    
    # Start the Flask application
    app.run(
        host=app_config['flask_host'], 
        port=app_config['flask_port'], 
        debug=app_config['flask_debug'], 
        threaded=True
    )
