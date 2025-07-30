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
except ImportError as e:
    print(f"⚠️ Some CLI modules not available: {e}")
    CLI_MODULES_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'cisco_meraki_web_app_2024'

# Global variables for active visualizations
active_visualizations = {}

class MerakiWebApp:
    def __init__(self):
        self.dashboard = None
        self.organizations = []
        self.networks = []
        
    def set_api_key(self, api_key):
        """Set and validate API key"""
        try:
            self.dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
            # Test the API key by getting organizations
            self.organizations = self.dashboard.organizations.getOrganizations()
            return True, "API key validated successfully"
        except Exception as e:
            return False, f"Invalid API key: {str(e)}"
    
    def get_organizations(self):
        """Get list of organizations"""
        return self.organizations
    
    def get_networks(self, org_id):
        """Get networks for an organization"""
        try:
            networks = self.dashboard.organizations.getOrganizationNetworks(org_id)
            return networks
        except Exception as e:
            logging.error(f"Error getting networks: {e}")
            return []
    
    def get_network_devices(self, network_id):
        """Get devices for a network"""
        try:
            devices = self.dashboard.networks.getNetworkDevices(network_id)
            return devices if isinstance(devices, list) else []
        except Exception as e:
            logging.error(f"Error getting devices: {e}")
            return []
    
    def get_network_clients(self, network_id, timespan=86400):
        """Get clients for a network"""
        try:
            clients = self.dashboard.networks.getNetworkClients(network_id, timespan=timespan)
            return clients if isinstance(clients, list) else []
        except Exception as e:
            logging.error(f"Error getting clients: {e}")
            return []
    
    def build_network_topology(self, network_id):
        """Build enhanced network topology"""
        try:
            devices = self.get_network_devices(network_id)
            clients = self.get_network_clients(network_id)
            
            # Build topology using enhanced method
            topology_data = build_topology_from_api_data(devices, clients, links=None)
            vis_data = create_vis_network_data(topology_data)
            
            return {
                'success': True,
                'topology': vis_data,
                'stats': {
                    'devices': len(devices),
                    'clients': len(clients),
                    'nodes': len(vis_data.get('nodes', [])),
                    'edges': len(vis_data.get('edges', []))
                }
            }
        except Exception as e:
            logging.error(f"Error building topology: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global app instance
meraki_app = MerakiWebApp()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/validate-key', methods=['POST'])
def validate_api_key():
    """Validate and set API key"""
    data = request.get_json()
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'success': False, 'error': 'API key is required'}), 400
    
    success, message = meraki_app.set_api_key(api_key)
    
    if success:
        session['api_key'] = api_key
        session['authenticated'] = True
        return jsonify({
            'success': True,
            'message': message,
            'organizations': meraki_app.get_organizations()
        })
    else:
        return jsonify({'success': False, 'error': message}), 400

@app.route('/api/organizations')
def get_organizations():
    """Get list of organizations"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'success': True,
        'organizations': meraki_app.get_organizations()
    })

@app.route('/api/networks/<org_id>')
def get_networks(org_id):
    """Get networks for an organization"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    networks = meraki_app.get_networks(org_id)
    return jsonify({
        'success': True,
        'networks': networks
    })

@app.route('/api/network/<network_id>/devices')
def get_network_devices(network_id):
    """Get devices for a network"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    devices = meraki_app.get_network_devices(network_id)
    return jsonify({
        'success': True,
        'devices': devices,
        'count': len(devices)
    })

@app.route('/api/network/<network_id>/clients')
def get_network_clients(network_id):
    """Get clients for a network"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    clients = meraki_app.get_network_clients(network_id)
    return jsonify({
        'success': True,
        'clients': clients,
        'count': len(clients)
    })

@app.route('/api/network/<network_id>/topology')
def get_network_topology(network_id):
    """Get enhanced network topology"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    result = meraki_app.build_network_topology(network_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/network/<network_id>/launch-visualization')
def launch_network_visualization(network_id):
    """Launch network topology visualization"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get network info
        network = meraki_app.dashboard.networks.getNetwork(network_id)
        network_name = network.get('name', 'Unknown Network')
        
        # Build topology
        result = meraki_app.build_network_topology(network_id)
        
        if not result['success']:
            return jsonify(result), 500
        
        # Store visualization data
        viz_id = str(uuid.uuid4())
        active_visualizations[viz_id] = {
            'network_id': network_id,
            'network_name': network_name,
            'topology': result['topology'],
            'stats': result['stats'],
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': f'Visualization created for {network_name}',
            'visualization_id': viz_id,
            'url': f'/visualization/{viz_id}',
            'stats': result['stats']
        })
        
    except Exception as e:
        logging.error(f"Error launching visualization: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/visualization/<viz_id>')
def show_visualization(viz_id):
    """Show network topology visualization"""
    if viz_id not in active_visualizations:
        return "Visualization not found", 404
    
    viz_data = active_visualizations[viz_id]
    return render_template('visualization.html', 
                         viz_id=viz_id,
                         network_name=viz_data['network_name'],
                         stats=viz_data['stats'])

@app.route('/api/visualization/<viz_id>/data')
def get_visualization_data(viz_id):
    """Get topology data for visualization"""
    if viz_id not in active_visualizations:
        return jsonify({'error': 'Visualization not found'}), 404
    
    viz_data = active_visualizations[viz_id]
    return jsonify(viz_data['topology'])

@app.route('/api/visualizations')
def list_visualizations():
    """List active visualizations"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    viz_list = []
    for viz_id, data in active_visualizations.items():
        viz_list.append({
            'id': viz_id,
            'network_name': data['network_name'],
            'network_id': data['network_id'],
            'created_at': data['created_at'],
            'stats': data['stats'],
            'url': f'/visualization/{viz_id}'
        })
    
    return jsonify({
        'success': True,
        'visualizations': viz_list
    })

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create templates and static directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🌐 Starting Cisco Meraki Web Management Interface...")
    print("📍 Access at: http://localhost:5000")
    print("🔧 Features: Network topology, device management, client monitoring")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
