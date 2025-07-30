#!/usr/bin/env python3
"""
Debug script to inspect topology data format and API responses
"""

import json
import logging
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced visualizer
from enhanced_visualizer import create_enhanced_visualization, build_topology_from_api_data

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_topology_data(dashboard, network_id, network_name):
    """Debug the topology data generation process"""
    
    print(f"\n🔍 DEBUGGING TOPOLOGY DATA FOR: {network_name}")
    print("=" * 60)
    
    try:
        # Step 1: Fetch raw API data
        print("\n📡 Step 1: Fetching devices from API...")
        devices = dashboard.networks.getNetworkDevices(network_id)
        print(f"   Raw devices response type: {type(devices)}")
        print(f"   Number of devices: {len(devices) if isinstance(devices, list) else 'N/A'}")
        
        if isinstance(devices, list) and devices:
            print(f"   First device keys: {list(devices[0].keys())}")
            print(f"   Device types: {[d.get('type', 'unknown') for d in devices]}")
        else:
            print(f"   Devices data: {devices}")
        
        print("\n📱 Step 2: Fetching clients from API...")
        clients = dashboard.networks.getNetworkClients(network_id, timespan=86400)
        print(f"   Raw clients response type: {type(clients)}")
        print(f"   Number of clients: {len(clients) if isinstance(clients, list) else 'N/A'}")
        
        if isinstance(clients, list) and clients:
            print(f"   First client keys: {list(clients[0].keys())}")
            print(f"   Client types: {[c.get('deviceType', 'unknown') for c in clients[:5]]}")
        else:
            print(f"   Clients data: {clients}")
        
        # Step 2: Build topology data
        print("\n🏗️  Step 3: Building topology data...")
        topology_data = build_topology_from_api_data(devices, clients, links=None)
        
        print(f"   Topology data keys: {list(topology_data.keys())}")
        print(f"   Number of nodes: {len(topology_data.get('nodes', []))}")
        print(f"   Number of links: {len(topology_data.get('links', []))}")
        
        # Step 3: Analyze nodes
        if topology_data.get('nodes'):
            print("\n📊 Node Analysis:")
            node_types = {}
            for node in topology_data['nodes']:
                node_type = node.get('type', 'unknown')
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            for node_type, count in node_types.items():
                print(f"   {node_type}: {count}")
            
            print(f"\n   Sample node: {json.dumps(topology_data['nodes'][0], indent=2)}")
        
        # Step 4: Analyze links
        if topology_data.get('links'):
            print("\n🔗 Link Analysis:")
            link_types = {}
            for link in topology_data['links']:
                link_type = link.get('type', 'unknown')
                link_types[link_type] = link_types.get(link_type, 0) + 1
            
            for link_type, count in link_types.items():
                print(f"   {link_type}: {count}")
            
            print(f"\n   Sample link: {json.dumps(topology_data['links'][0], indent=2)}")
        else:
            print("\n🔗 No links found in topology data")
        
        # Step 5: Save debug data to file
        debug_file = Path("topology_debug_data.json")
        debug_data = {
            'network_name': network_name,
            'network_id': network_id,
            'raw_devices': devices if isinstance(devices, list) else str(devices),
            'raw_clients': clients if isinstance(clients, list) else str(clients),
            'topology_data': topology_data
        }
        
        with open(debug_file, 'w') as f:
            json.dump(debug_data, f, indent=2, default=str)
        
        print(f"\n💾 Debug data saved to: {debug_file}")
        
        return topology_data
        
    except Exception as e:
        print(f"\n❌ Error during debugging: {str(e)}")
        logging.exception("Debug error")
        return None

if __name__ == "__main__":
    print("This is a debug module. Import and call debug_topology_data() function.")
