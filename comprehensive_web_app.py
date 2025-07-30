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
    print("✅ SSL universal fix applied")
except ImportError:
    try:
        import ssl_patch
        print("✅ SSL patch applied")
    except ImportError:
        print("⚠️ No SSL fixes available - may have issues in corporate environments")

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
    print("✅ All CLI modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Some CLI modules not available: {e}")
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
        
        meraki_manager.api_mode = api_mode
        if meraki_manager.set_api_key(api_key):
            session['api_key'] = api_key
            session['api_mode'] = api_mode
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid API key or API connection failed'})
    
    except Exception as e:
        logger.error(f"API key validation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/organizations')
def get_organizations():
    """Get all organizations"""
    try:
        if 'api_key' not in session:
            return jsonify({'error': 'API key not set'}), 401
        
        orgs = meraki_manager.get_organizations()
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
    print("🌐 Starting Comprehensive Cisco Meraki Web Management Interface")
    print("=" * 70)
    print("✅ Integrates ALL CLI functionality into modern web interface")
    print("🔧 Features: Network Status, Device Management, Topology, Tools, Settings")
    print("🚀 Access at: http://localhost:5000")
    
    if CLI_MODULES_AVAILABLE:
        print("✅ All CLI modules loaded - Full functionality available")
    else:
        print("⚠️ Some CLI modules missing - Limited functionality")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
