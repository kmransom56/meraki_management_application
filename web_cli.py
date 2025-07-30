#!/usr/bin/env python3
"""
Web-based CLI Interface for Cisco Meraki CLI
Provides an easy way to access CLI functionality through a web browser
"""

from flask import Flask, render_template, request, jsonify, session
import subprocess
import threading
import queue
import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append('/app')
sys.path.append('.')

# Import the main CLI modules
from utilities.submenu import (
    select_organization, select_network, network_wide_operations,
    submenu_network_wide, submenu_mx, submenu_sw_and_ap
)

app = Flask(__name__)
app.secret_key = 'meraki_cli_web_interface_2024'

class WebCLI:
    def __init__(self):
        self.current_state = 'main_menu'
        self.api_key = None
        self.organization_id = None
        self.network_id = None
        
    def set_api_key(self, api_key):
        self.api_key = api_key
        
    def get_organizations(self):
        """Get list of organizations for the current API key"""
        if not self.api_key:
            return {'error': 'API key not set'}
        
        try:
            # Use the select_organization function but capture the data
            organizations = []  # This would need to be implemented
            return {'organizations': organizations}
        except Exception as e:
            return {'error': str(e)}

# Global WebCLI instance
web_cli = WebCLI()

@app.route('/')
def index():
    """Main web interface page"""
    return render_template('web_cli.html')

@app.route('/api/set-key', methods=['POST'])
def set_api_key():
    """Set the Meraki API key"""
    data = request.get_json()
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    web_cli.set_api_key(api_key)
    session['api_key'] = api_key
    
    return jsonify({'success': True, 'message': 'API key set successfully'})

@app.route('/api/organizations')
def get_organizations():
    """Get list of organizations"""
    api_key = session.get('api_key')
    if not api_key:
        return jsonify({'error': 'API key not set'}), 400
    
    try:
        # Import and use the existing organization selection logic
        from modules.meraki import meraki_api
        organizations = meraki_api.get_organizations(api_key)
        return jsonify({'organizations': organizations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/networks/<organization_id>')
def get_networks(organization_id):
    """Get networks for an organization"""
    api_key = session.get('api_key')
    if not api_key:
        return jsonify({'error': 'API key not set'}), 400
    
    try:
        from modules.meraki import meraki_api
        networks = meraki_api.get_networks(api_key, organization_id)
        return jsonify({'networks': networks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/<network_id>')
def get_network_topology(network_id):
    """Get enhanced network topology"""
    api_key = session.get('api_key')
    if not api_key:
        return jsonify({'error': 'API key not set'}), 400
    
    try:
        # Import enhanced visualizer
        from enhanced_visualizer import build_topology_from_api_data, create_vis_network_data
        import meraki
        
        # Create dashboard
        dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
        
        # Fetch data
        devices = dashboard.networks.getNetworkDevices(network_id)
        clients = dashboard.networks.getNetworkClients(network_id, timespan=86400)
        
        # Build topology
        topology_data = build_topology_from_api_data(devices, clients, links=None)
        vis_data = create_vis_network_data(topology_data)
        
        return jsonify({
            'topology': vis_data,
            'stats': {
                'devices': len(devices) if isinstance(devices, list) else 0,
                'clients': len(clients) if isinstance(clients, list) else 0,
                'nodes': len(vis_data.get('nodes', [])),
                'edges': len(vis_data.get('edges', []))
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/launch-topology/<network_id>')
def launch_topology_visualization(network_id):
    """Launch the topology visualization for a network"""
    api_key = session.get('api_key')
    if not api_key:
        return jsonify({'error': 'API key not set'}), 400
    
    try:
        # Import required modules
        from utilities.submenu import create_web_visualization
        from enhanced_visualizer import build_topology_from_api_data, create_vis_network_data
        import meraki
        
        # Create dashboard
        dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
        
        # Get network name
        network = dashboard.networks.getNetwork(network_id)
        network_name = network.get('name', 'Unknown Network')
        
        # Fetch data
        devices = dashboard.networks.getNetworkDevices(network_id)
        clients = dashboard.networks.getNetworkClients(network_id, timespan=86400)
        
        # Build topology
        topology_data = build_topology_from_api_data(devices, clients, links=None)
        topology_data['network_name'] = network_name
        
        # Convert to visualization format
        vis_data = create_vis_network_data(topology_data)
        vis_data['network_name'] = network_name
        
        # Launch web visualization in a separate thread
        def launch_viz():
            create_web_visualization(vis_data)
        
        viz_thread = threading.Thread(target=launch_viz, daemon=True)
        viz_thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Topology visualization launched for {network_name}',
            'url': 'http://localhost:5001',
            'stats': {
                'devices': len(devices) if isinstance(devices, list) else 0,
                'clients': len(clients) if isinstance(clients, list) else 0,
                'nodes': len(vis_data.get('nodes', [])),
                'edges': len(vis_data.get('edges', []))
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cisco Meraki CLI - Web Interface</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .header h1 {
            color: #1f5582;
            margin: 0;
        }
        .section {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background: #fafafa;
        }
        .section h3 {
            margin-top: 0;
            color: #333;
        }
        .form-group {
            margin: 15px 0;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .btn {
            background-color: #1f5582;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        .btn:hover {
            background-color: #164466;
        }
        .btn:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .success {
            color: #28a745;
            background-color: #d4edda;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .hidden {
            display: none;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #1f5582;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Cisco Meraki CLI - Web Interface</h1>
            <p>Easy access to network topology visualization and management</p>
        </div>

        <!-- API Key Section -->
        <div class="section">
            <h3>🔑 API Configuration</h3>
            <div class="form-group">
                <label for="apiKey">Meraki API Key:</label>
                <input type="password" id="apiKey" placeholder="Enter your Meraki API key">
            </div>
            <button class="btn" onclick="setApiKey()">Set API Key</button>
            <div id="apiKeyStatus"></div>
        </div>

        <!-- Organization Selection -->
        <div class="section hidden" id="orgSection">
            <h3>🏢 Organization Selection</h3>
            <div class="form-group">
                <label for="orgSelect">Select Organization:</label>
                <select id="orgSelect" onchange="loadNetworks()">
                    <option value="">Choose an organization...</option>
                </select>
            </div>
        </div>

        <!-- Network Selection -->
        <div class="section hidden" id="networkSection">
            <h3>🌐 Network Selection</h3>
            <div class="form-group">
                <label for="networkSelect">Select Network:</label>
                <select id="networkSelect" onchange="showNetworkActions()">
                    <option value="">Choose a network...</option>
                </select>
            </div>
        </div>

        <!-- Network Actions -->
        <div class="section hidden" id="actionsSection">
            <h3>⚡ Network Actions</h3>
            <button class="btn" onclick="launchTopologyVisualization()">🔍 Launch Topology Visualization</button>
            <button class="btn" onclick="getNetworkInfo()">📊 Get Network Information</button>
            <div id="actionResults"></div>
            
            <!-- Network Stats -->
            <div id="networkStats" class="hidden">
                <h4>Network Statistics</h4>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="deviceCount">-</div>
                        <div class="stat-label">Devices</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="clientCount">-</div>
                        <div class="stat-label">Clients</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="nodeCount">-</div>
                        <div class="stat-label">Topology Nodes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="edgeCount">-</div>
                        <div class="stat-label">Connections</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentOrgId = null;
        let currentNetworkId = null;

        function showMessage(message, type = 'success') {
            const div = document.createElement('div');
            div.className = type;
            div.textContent = message;
            return div;
        }

        async function setApiKey() {
            const apiKey = document.getElementById('apiKey').value;
            const statusDiv = document.getElementById('apiKeyStatus');
            
            if (!apiKey) {
                statusDiv.innerHTML = '';
                statusDiv.appendChild(showMessage('Please enter an API key', 'error'));
                return;
            }

            try {
                const response = await fetch('/api/set-key', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: apiKey})
                });

                const result = await response.json();
                statusDiv.innerHTML = '';

                if (response.ok) {
                    statusDiv.appendChild(showMessage('API key set successfully!', 'success'));
                    loadOrganizations();
                } else {
                    statusDiv.appendChild(showMessage(result.error || 'Failed to set API key', 'error'));
                }
            } catch (error) {
                statusDiv.innerHTML = '';
                statusDiv.appendChild(showMessage('Error: ' + error.message, 'error'));
            }
        }

        async function loadOrganizations() {
            try {
                const response = await fetch('/api/organizations');
                const result = await response.json();

                if (response.ok && result.organizations) {
                    const select = document.getElementById('orgSelect');
                    select.innerHTML = '<option value="">Choose an organization...</option>';
                    
                    result.organizations.forEach(org => {
                        const option = document.createElement('option');
                        option.value = org.id;
                        option.textContent = org.name;
                        select.appendChild(option);
                    });

                    document.getElementById('orgSection').classList.remove('hidden');
                } else {
                    console.error('Failed to load organizations:', result.error);
                }
            } catch (error) {
                console.error('Error loading organizations:', error);
            }
        }

        async function loadNetworks() {
            const orgId = document.getElementById('orgSelect').value;
            if (!orgId) return;

            currentOrgId = orgId;

            try {
                const response = await fetch(`/api/networks/${orgId}`);
                const result = await response.json();

                if (response.ok && result.networks) {
                    const select = document.getElementById('networkSelect');
                    select.innerHTML = '<option value="">Choose a network...</option>';
                    
                    result.networks.forEach(network => {
                        const option = document.createElement('option');
                        option.value = network.id;
                        option.textContent = network.name;
                        select.appendChild(option);
                    });

                    document.getElementById('networkSection').classList.remove('hidden');
                } else {
                    console.error('Failed to load networks:', result.error);
                }
            } catch (error) {
                console.error('Error loading networks:', error);
            }
        }

        function showNetworkActions() {
            const networkId = document.getElementById('networkSelect').value;
            if (!networkId) return;

            currentNetworkId = networkId;
            document.getElementById('actionsSection').classList.remove('hidden');
        }

        async function launchTopologyVisualization() {
            if (!currentNetworkId) return;

            const resultsDiv = document.getElementById('actionResults');
            resultsDiv.innerHTML = '<p>Launching topology visualization...</p>';

            try {
                const response = await fetch(`/api/launch-topology/${currentNetworkId}`);
                const result = await response.json();

                resultsDiv.innerHTML = '';

                if (response.ok) {
                    resultsDiv.appendChild(showMessage(result.message, 'success'));
                    
                    // Show stats
                    if (result.stats) {
                        document.getElementById('deviceCount').textContent = result.stats.devices;
                        document.getElementById('clientCount').textContent = result.stats.clients;
                        document.getElementById('nodeCount').textContent = result.stats.nodes;
                        document.getElementById('edgeCount').textContent = result.stats.edges;
                        document.getElementById('networkStats').classList.remove('hidden');
                    }

                    // Add link to visualization
                    const link = document.createElement('p');
                    link.innerHTML = `<a href="${result.url}" target="_blank">🌐 Open Topology Visualization</a>`;
                    resultsDiv.appendChild(link);
                } else {
                    resultsDiv.appendChild(showMessage(result.error || 'Failed to launch visualization', 'error'));
                }
            } catch (error) {
                resultsDiv.innerHTML = '';
                resultsDiv.appendChild(showMessage('Error: ' + error.message, 'error'));
            }
        }

        async function getNetworkInfo() {
            if (!currentNetworkId) return;

            const resultsDiv = document.getElementById('actionResults');
            resultsDiv.innerHTML = '<p>Getting network information...</p>';

            try {
                const response = await fetch(`/api/topology/${currentNetworkId}`);
                const result = await response.json();

                resultsDiv.innerHTML = '';

                if (response.ok) {
                    resultsDiv.appendChild(showMessage('Network information retrieved successfully!', 'success'));
                    
                    // Show stats
                    if (result.stats) {
                        document.getElementById('deviceCount').textContent = result.stats.devices;
                        document.getElementById('clientCount').textContent = result.stats.clients;
                        document.getElementById('nodeCount').textContent = result.stats.nodes;
                        document.getElementById('edgeCount').textContent = result.stats.edges;
                        document.getElementById('networkStats').classList.remove('hidden');
                    }
                } else {
                    resultsDiv.appendChild(showMessage(result.error || 'Failed to get network info', 'error'));
                }
            } catch (error) {
                resultsDiv.innerHTML = '';
                resultsDiv.appendChild(showMessage('Error: ' + error.message, 'error'));
            }
        }
    </script>
</body>
</html>
    '''
    
    with open('templates/web_cli.html', 'w') as f:
        f.write(html_template)
    
    print("🌐 Starting Web CLI Interface...")
    print("📍 Access at: http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
