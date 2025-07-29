"""
Flask web application for network topology visualization.
"""
import os
import json
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from typing import Dict, Any, List

# Global variables to store network data
network_data = {}

app = Flask(__name__)

# Route to serve visualization HTML files
@app.route('/view-viz/<filename>')
def view_viz(filename):
    # Check both Docker and Windows paths
    docker_viz_dir = '/home/merakiuser/meraki_visualizations'
    windows_viz_dir = os.path.expanduser(r'C:/Users/keith.ransom/meraki_visualizations')
    
    # Use Docker path if running in container, Windows path otherwise
    if os.path.exists(docker_viz_dir):
        viz_dir = docker_viz_dir
    else:
        viz_dir = windows_viz_dir
    
    # Security: Only allow .html files
    if not filename.endswith('.html'):
        return "Invalid file type", 400
    
    file_path = os.path.join(viz_dir, filename)
    if not os.path.exists(file_path):
        return f"File not found: {file_path}", 404
    
    return send_from_directory(viz_dir, filename)

def create_app(data: Dict[str, Any] = None) -> Flask:
    """Create and configure Flask app."""
    global network_data
    
    if data:
        network_data = data
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    return app


@app.route('/')
def index():
    """Render the main topology page."""
    return render_template('topology.html')


@app.route('/topology-data')
def get_topology_data():
    """Provide topology data as JSON for the frontend."""
    global network_data
    
    try:
        # Ensure we have valid data structure
        if not network_data:
            return jsonify({
                'nodes': [],
                'links': [],
                'metadata': {
                    'deviceCount': 0,
                    'clientCount': 0,
                    'error': 'No network data available'
                }
            })
        
        # Calculate statistics
        devices = network_data.get('devices', [])
        clients = network_data.get('clients', [])
        topology = network_data.get('topology', {})
        
        # Build comprehensive response
        response_data = {
            'network': network_data.get('network', {}),
            'devices': devices,
            'clients': clients,
            'topology': topology,
            'statistics': calculate_network_statistics(devices, clients),
            'metadata': {
                'deviceCount': len(devices),
                'clientCount': len(clients),
                'lastUpdated': network_data.get('lastUpdated'),
                'networkId': network_data.get('network', {}).get('id'),
                'networkName': network_data.get('network', {}).get('name')
            }
        }
        
        app.logger.info(f"Serving topology data: {len(devices)} devices, {len(clients)} clients")
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.error(f"Error serving topology data: {e}")
        return jsonify({
            'error': str(e),
            'nodes': [],
            'links': [],
            'metadata': {'error': 'Failed to load topology data'}
        }), 500


@app.route('/device/<device_id>')
def get_device_details(device_id: str):
    """Get detailed information about a specific device."""
    global network_data
    
    devices = network_data.get('devices', [])
    device = next((d for d in devices if d.get('serial') == device_id), None)
    
    if device:
        return jsonify(device)
    else:
        return jsonify({'error': 'Device not found'}), 404


@app.route('/client/<client_id>')
def get_client_details(client_id: str):
    """Get detailed information about a specific client."""
    global network_data
    
    clients = network_data.get('clients', [])
    client = next((c for c in clients if c.get('mac') == client_id), None)
    
    if client:
        return jsonify(client)
    else:
        return jsonify({'error': 'Client not found'}), 404


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'dataLoaded': bool(network_data),
        'deviceCount': len(network_data.get('devices', [])),
        'clientCount': len(network_data.get('clients', []))
    })


def calculate_network_statistics(devices: List[Dict], clients: List[Dict]) -> Dict[str, Any]:
    """Calculate network statistics for display."""
    stats = {
        'deviceTypes': {},
        'deviceStatuses': {},
        'clientStatuses': {},
        'connectionTypes': {},
        'totalDevices': len(devices),
        'totalClients': len(clients),
        'activeConnections': 0
    }
    
    # Analyze devices
    for device in devices:
        # Device types
        device_type = device.get('productType', 'unknown')
        stats['deviceTypes'][device_type] = stats['deviceTypes'].get(device_type, 0) + 1
        
        # Device statuses
        status = device.get('status', 'unknown')
        stats['deviceStatuses'][status] = stats['deviceStatuses'].get(status, 0) + 1
    
    # Analyze clients
    for client in clients:
        # Client statuses
        status = client.get('status', 'unknown')
        stats['clientStatuses'][status] = stats['clientStatuses'].get(status, 0) + 1
        
        # Count active connections
        if status in ['Online', 'online']:
            stats['activeConnections'] += 1
        
        # Connection types
        if client.get('ssid'):
            stats['connectionTypes']['wireless'] = stats['connectionTypes'].get('wireless', 0) + 1
        else:
            stats['connectionTypes']['wired'] = stats['connectionTypes'].get('wired', 0) + 1
    
    return stats


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
