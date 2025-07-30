#!/usr/bin/env python3
"""
Quick Launch Script for Cisco Meraki CLI
Provides easy access to topology visualization without complex menus
"""

import os
import sys
import webbrowser
import time
import threading

def launch_topology_visualization():
    """Launch topology visualization with minimal user input"""
    print("🌐 Cisco Meraki CLI - Quick Launch")
    print("=" * 50)
    
    # Get API key
    api_key = input("Enter your Meraki API key: ").strip()
    if not api_key:
        print("❌ API key is required")
        return
    
    try:
        # Import required modules
        import meraki
        from utilities.submenu import create_web_visualization
        from enhanced_visualizer import build_topology_from_api_data, create_vis_network_data
        
        # Create dashboard
        print("🔍 Connecting to Meraki API...")
        dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
        
        # Get organizations
        print("🏢 Getting organizations...")
        organizations = dashboard.organizations.getOrganizations()
        
        if not organizations:
            print("❌ No organizations found")
            return
        
        # Show organizations
        print("\nAvailable Organizations:")
        for i, org in enumerate(organizations, 1):
            print(f"{i}. {org['name']}")
        
        # Select organization
        while True:
            try:
                choice = int(input(f"\nSelect organization (1-{len(organizations)}): "))
                if 1 <= choice <= len(organizations):
                    selected_org = organizations[choice - 1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        org_id = selected_org['id']
        print(f"✅ Selected: {selected_org['name']}")
        
        # Get networks
        print("🌐 Getting networks...")
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        
        if not networks:
            print("❌ No networks found")
            return
        
        # Show networks (first 20)
        print("\nAvailable Networks:")
        display_networks = networks[:20]  # Limit to first 20 for simplicity
        for i, network in enumerate(display_networks, 1):
            print(f"{i}. {network['name']}")
        
        if len(networks) > 20:
            print(f"... and {len(networks) - 20} more networks")
        
        # Select network
        while True:
            try:
                choice = int(input(f"\nSelect network (1-{len(display_networks)}): "))
                if 1 <= choice <= len(display_networks):
                    selected_network = display_networks[choice - 1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        network_id = selected_network['id']
        network_name = selected_network['name']
        print(f"✅ Selected: {network_name}")
        
        # Fetch data and create visualization
        print("\n🔍 Fetching network devices and clients...")
        devices = dashboard.networks.getNetworkDevices(network_id)
        clients = dashboard.networks.getNetworkClients(network_id, timespan=86400)
        
        print(f"📊 Found {len(devices) if isinstance(devices, list) else 0} devices")
        print(f"👥 Found {len(clients) if isinstance(clients, list) else 0} clients")
        
        # Build topology
        print("🏗️ Building network topology...")
        topology_data = build_topology_from_api_data(devices, clients, links=None)
        topology_data['network_name'] = network_name
        
        # Convert to visualization format
        vis_data = create_vis_network_data(topology_data)
        vis_data['network_name'] = network_name
        
        print(f"🌐 Topology: {len(vis_data.get('nodes', []))} nodes, {len(vis_data.get('edges', []))} connections")
        
        if vis_data.get('nodes'):
            print("\n🚀 Launching topology visualization...")
            
            # Launch visualization in a separate thread
            def launch_viz():
                create_web_visualization(vis_data)
            
            viz_thread = threading.Thread(target=launch_viz, daemon=True)
            viz_thread.start()
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            # Open browser
            print("🌐 Opening browser...")
            webbrowser.open('http://localhost:5001')
            
            print("\n✅ Topology visualization launched successfully!")
            print("📍 URL: http://localhost:5001")
            print("\n📝 Press Enter to exit (visualization will continue running)...")
            input()
            
        else:
            print("⚠️ No topology data available for visualization")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the correct directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    launch_topology_visualization()
