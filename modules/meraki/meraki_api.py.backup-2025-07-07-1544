#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.4                                                      *
#   Author:      Matia Zanella                                            *
#   Description: Cisco Meraki CLU (Command Line Utility) is an essential  *
#                tool crafted for Network Administrators managing Meraki  *
#   Github:      https://github.com/akamura/cisco-meraki-clu/             *
#                                                                         *
#   Icon Author:        Cisco Systems, Inc.                               *
#   Icon Author URL:    https://meraki.cisco.com/                         *
#                                                                         *
#   Copyright (C) 2024 Matia Zanella                                      *
#   https://www.matiazanella.com                                          *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU General Public License as published by  *
#   the Free Software Foundation; either version 2 of the License, or     *
#   (at your option) any later version.                                   *
#                                                                         *
#   This program is distributed in the hope that it will be useful,       *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU General Public License for more details.                          *
#                                                                         *
#   You should have received a copy of the GNU General Public License     *
#   along with this program; if not, write to the                         *
#   Free Software Foundation, Inc.,                                       *
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#**************************************************************************
import requests
import subprocess
import sys
import logging
import json

# Corporate SSL Configuration
import warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import logging
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

# Corporate SSL Configuration
import warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import logging
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

# Corporate SSL Configuration
import warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import logging
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
import csv
import os
try:
    from tabulate import tabulate
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
    from tabulate import tabulate
import ssl
import certifi
from datetime import datetime
try:
    from termcolor import colored
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "termcolor"])
import json
from pathlib import Path
try:
    from cryptography.fernet import Fernet
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Import our new device types module
from modules.meraki.device_types import get_device_type, supports_uplink, get_device_type_from_serial

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure requests to use system CA certificates and disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Base URL for Meraki API
BASE_URL = "https://api.meraki.com/api/v1"

def get_organizations(api_key):
    """Get a list of organizations accessible by the user"""
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(api_key, "/organizations", headers)

def get_organization_networks(api_key, org_id):
    """Get list of networks for an organization"""
    params = {"perPage": 5000}  # Get all networks in one request
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(api_key, f"/organizations/{org_id}/networks", headers, params)

def get_organization_summary(api_key, organization_id):
    """Get summary information about an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/summary")

def get_organization_inventory(api_key, organization_id):
    """Get inventory information for an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/inventory/devices")

def get_organization_licenses(api_key, organization_id):
    """Get license information for an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/licenses")

def get_organization_devices_statuses(api_key, organization_id):
    """Get device status information for an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/devices/statuses")

# ==================================================
# EXPORT device list in a beautiful table format
# ==================================================
def export_devices_to_csv(devices, network_name, device_type, base_folder_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{network_name}_{current_date}_{device_type}.csv"
    file_path = os.path.join(base_folder_path, filename)

    if devices:
        # Priority columns
        priority_columns = ['name', 'mac', 'lanIp', 'serial', 'model', 'firwmare', 'tags']

        # Gather all columns from the devices
        all_columns = set(key for device in devices for key in device.keys())
        
        # Reorder columns so that priority columns come first
        ordered_columns = priority_columns + [col for col in all_columns if col not in priority_columns]

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            # Convert fieldnames to uppercase
            fieldnames = [col.upper() for col in ordered_columns]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for device in devices:
                # Convert keys to uppercase to match fieldnames
                row = {col.upper(): device.get(col, '') for col in ordered_columns}
                writer.writerow(row)
            
        print(f"Data exported to {file_path}")
    else:
        print("No data to export.")

# ==================================================
# EXPORT firewall rules in a beautiful table format
# ==================================================
def export_firewall_rules_to_csv(firewall_rules, network_name, base_folder_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{network_name}_{current_date}_MX_Firewall_Rules.csv"
    file_path = os.path.join(base_folder_path, filename)

    if firewall_rules:
        # Priority columns, adjust these based on your data
        priority_columns = ['policy', 'protocol', 'srcport', 'srccidr', 'destport','destcidr','comments']

        # Gather all columns from the firewall rules
        all_columns = set(key for rule in firewall_rules for key in rule.keys())
        
        # Reorder columns so that priority columns come first
        ordered_columns = priority_columns + [col for col in all_columns if col not in priority_columns]

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            # Convert fieldnames to uppercase
            fieldnames = [col.upper() for col in ordered_columns]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for rule in firewall_rules:
                # Convert keys to uppercase to match fieldnames
                row = {col.upper(): rule.get(col, '') for col in ordered_columns}
                writer.writerow(row)
            
        print(f"Data exported to {file_path}")
    else:
        print("No data to export.")

# ==================================================
# GET a list of Organizations
# ==================================================
def get_meraki_organizations(api_key):
    """Get list of organizations accessible by the API key"""
    return make_meraki_request(api_key, "/organizations")

def select_organization(api_key):
    """Interactive selection of an organization"""
    organizations = get_meraki_organizations(api_key)
    if organizations:
        print(colored("\nAvailable Organizations:", "cyan"))
        for idx, org in enumerate(organizations, 1):
            print(f"{idx}. {org['name']}")

        choice = input(colored("\nSelect an Organization (enter the number): ", "cyan"))
        try:
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(organizations):
                # Return only the organization ID string, not the entire object
                return organizations[selected_index]['id']
            else:
                print(colored("Invalid selection.", "red"))
        except ValueError:
            print(colored("Please enter a number.", "red"))

    return None

# ==================================================
# GET a list of Networks in an Organization
# ==================================================
def get_meraki_networks(api_key, organization_id, per_page=5000):
    params = {"perPage": per_page}  # Get all networks in one request
    return make_meraki_request(api_key, f"/organizations/{organization_id}/networks", params=params)

# ==================================================
# SELECT a Network in an Organization
# ==================================================
def select_network(api_key, organization_id):
    """
    Enhanced network selection with pagination and search functionality
    
    Args:
        api_key (str): Meraki API key
        organization_id (str): Organization ID
        
    Returns:
        str: Selected network ID or None if selection is cancelled
    """
    networks = get_meraki_networks(api_key, organization_id)
    if not networks:
        print(colored("\nNo networks found for this organization.", "red"))
        return None
    
    # Sort networks alphabetically by name
    networks.sort(key=lambda x: x['name'])
    
    # Initialize variables for pagination and search
    page_size = 20
    current_page = 0
    search_term = ""
    filtered_networks = networks
    
    import os
    from settings import term_extra
    
    while True:
        # Clear screen for better UI
        term_extra.clear_screen()
        
        # Apply search filter if search term exists
        if search_term:
            filtered_networks = [n for n in networks if search_term.lower() in n['name'].lower()]
            if not filtered_networks:
                print(colored(f"\nNo networks found matching '{search_term}'", "yellow"))
                search_term = ""
                filtered_networks = networks
                continue
        
        # Calculate pagination
        total_pages = (len(filtered_networks) + page_size - 1) // page_size
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(filtered_networks))
        
        # Display header with pagination info
        print(colored("\nNetwork Selection", "cyan"))
        print(f"Showing {start_idx+1}-{end_idx} of {len(filtered_networks)} networks")
        if search_term:
            print(f"Search filter: '{search_term}'")
        print("-" * 50)
        
        # Display current page of networks
        for i in range(start_idx, end_idx):
            network = filtered_networks[i]
            print(f"{i+1}. {network['name']}")
        
        # Display navigation options
        print("\nOptions:")
        print("  Enter a number to select a network")
        if current_page > 0:
            print("  P - Previous page")
        if current_page < total_pages - 1:
            print("  N - Next page")
        print("  S - Search networks")
        if search_term:
            print("  C - Clear search")
        print("  Q - Cancel selection")
        
        choice = input(colored("\nEnter your choice: ", "cyan")).strip()
        
        # Handle navigation and search options
        if choice.lower() == 'p' and current_page > 0:
            current_page -= 1
        elif choice.lower() == 'n' and current_page < total_pages - 1:
            current_page += 1
        elif choice.lower() == 's':
            search_term = input(colored("Enter search term: ", "cyan")).strip()
            current_page = 0  # Reset to first page when searching
        elif choice.lower() == 'c' and search_term:
            search_term = ""
            filtered_networks = networks
            current_page = 0
        elif choice.lower() == 'q':
            print(colored("Network selection cancelled.", "yellow"))
            return None
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(filtered_networks):
                selected_network = filtered_networks[idx]
                network_id = selected_network['id']
                print(colored(f"\nSelected network: {selected_network['name']}", "green"))
                return network_id
            else:
                print(colored("Invalid network number. Please try again.", "red"))
                input("Press Enter to continue...")
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input("Press Enter to continue...")
    
    return None

# ==================================================
# GET a list of Switches in an Network
# ==================================================
def get_meraki_switches(api_key, network_id):
    return make_meraki_request(api_key, f"/networks/{network_id}/devices")

def display_switches(api_key, network_id):
    devices = get_meraki_switches(api_key, network_id)
    if devices:
        # Filter to include only switches
        switches = [device for device in devices if device['model'].startswith('MS')]
        for switch in switches:
            print(f"Name: {switch.get('name', 'N/A')}")
            print(f"Serial: {switch.get('serial', 'N/A')}")
            print(f"Model: {switch.get('model', 'N/A')}")
            print("------------------------")
        return switches
    return None

# ==================================================
# GET a list of Switch Ports and their Status
# ==================================================
def get_switch_ports(api_key, serial):
    return make_meraki_request(api_key, f"/devices/{serial}/switch/ports")

def get_switch_ports_statuses_with_timespan(api_key, serial, timespan=1800):
    params = {"timespan": timespan}
    return make_meraki_request(api_key, f"/devices/{serial}/switch/ports/statuses", params=params)

# ==================================================
# GET a list of Access Points in an Network
# ==================================================
def get_meraki_access_points(api_key, network_id):
    return make_meraki_request(api_key, f"/networks/{network_id}/devices")

# =======================================================================
# [UNDER DEVELOPMENT] GET a list of VLANs and Static Routes in an Network
# =======================================================================
def get_meraki_vlans(api_key, network_id):
    return make_meraki_request(api_key, f"/networks/{network_id}/appliance/vlans")

def get_meraki_static_routes(api_key, network_id):
    return make_meraki_request(api_key, f"/networks/{network_id}/appliance/staticRoutes")

# ==================================================
# SELECT a Network in an Organization
# ==================================================
def select_mx_network(api_key, organization_id):
    networks = get_meraki_networks(api_key, organization_id)
    if networks:
        mx_networks = []
        print("\nAvailable Networks with MX:")
        idx = 1
        for network in networks:
            if any(device['model'].startswith('MX') for device in get_meraki_switches(api_key, network['id'])):
                print(f"{idx}. {network['name']}")
                mx_networks.append(network)
                idx += 1
        
        while True:
            try:
                choice = input(colored("\nSelect a Network (enter the number): ", "cyan"))
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(mx_networks):
                    # Return only the network ID string, not the entire object
                    return mx_networks[selected_index]['id']
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            except IndexError:
                print("Invalid selection. Please try again.")
    return None

# ==================================================
# GET Layer 3 Firewall Rules for a Network
# ==================================================
def get_l3_firewall_rules(api_key, network_id):
    return make_meraki_request(api_key, f"/networks/{network_id}/appliance/firewall/l3FirewallRules")

# ==================================================
# DISPLAY Firewall Rules in a Table Format
# ==================================================
def display_firewall_rules(firewall_rules):
    if firewall_rules:
        print("\nLayer 3 Firewall Rules:")
        print(tabulate(firewall_rules, headers="keys", tablefmt="pretty"))
    else:
        print("No firewall rules found in the selected network.")

# ==============================================================
# FETCH Organization policy and group objects for Firewall Rules
# ==============================================================
def get_organization_policy_objects(api_key, organization_id):
    return make_meraki_request(api_key, f"/organizations/{organization_id}/policyObjects")

def get_organization_policy_objects_groups(api_key, organization_id):
    return make_meraki_request(api_key, f"/organizations/{organization_id}/policyObjects/groups")

# ==============================================================
# FETCH Organization Devices Statuses
# ==============================================================
def get_organization_devices_statuses(api_key, organization_id):
    return make_meraki_request(api_key, f"/organizations/{organization_id}/devices/statuses")

# ==================================================
# GET Environmental Sensor Data
# ==================================================
def get_network_sensor_alerts(api_key, network_id):
    return make_meraki_request(api_key, f"/networks/{network_id}/sensor/alerts/current/overview/byMetric")

def get_device_sensor_data(api_key, serial):
    return make_meraki_request(api_key, f"/devices/{serial}/sensor/readings/latest")

def get_device_sensor_relationships(api_key, serial):
    return make_meraki_request(api_key, f"/devices/{serial}/sensor/relationships")

# ==================================================
# GET Organization Details
# ==================================================
def get_meraki_organization_details(api_key, organization_id):
    """Get details for a specific organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}")

def get_meraki_organization_inventory(api_key, organization_id):
    """Get inventory for a specific organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/inventory/devices")

def get_meraki_organization_devices(api_key, organization_id):
    """Get all devices in an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/devices")

def get_meraki_organization_networks(api_key, organization_id):
    """Get all networks in an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/networks")

def get_meraki_organization_admins(api_key, organization_id):
    """Get all admins in an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/admins")

def get_meraki_organization_licenses(api_key, organization_id):
    """Get all licenses in an organization"""
    return make_meraki_request(api_key, f"/organizations/{organization_id}/licenses")

def get_organization_inventory(api_key, organization_id):
    return make_meraki_request(api_key, f"/organizations/{organization_id}/inventory/devices")

def get_organization_licenses(api_key, organization_id):
    return make_meraki_request(api_key, f"/organizations/{organization_id}/licenses")

def get_organization_summary(api_key, organization_id):
    return make_meraki_request(api_key, f"/organizations/{organization_id}/summary")

# ==================================================
# GET Network Health and Performance
# ==================================================
def get_network_health(api_key, network_id):
    return make_meraki_request(api_key, f"/networks/{network_id}/health")

def get_network_clients(api_key, network_id, timespan=3600):
    """
    Get clients connected to a network
    
    Args:
        api_key (str): Meraki API key
        network_id (str): Network ID
        timespan (int): Timespan in seconds for which clients are fetched (default: 3600 = 1 hour)
        
    Returns:
        list: List of client devices
    """
    params = {"perPage": 1000, "timespan": timespan}
    return make_meraki_request(api_key, f"/networks/{network_id}/clients", params=params)

# ==================================================
# GET Network Topology
# ==================================================
def get_network_devices(api_key, network_id):
    """Get all devices in a network"""
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    return make_meraki_request(api_key, f"/networks/{network_id}/devices", headers)

def get_network_name(api_key, network_id):
    """
    Get the name of a network by its ID using a direct API call
    
    Args:
        api_key (str): Meraki API key
        network_id (str): Network ID
        
    Returns:
        str: Network name or 'Unknown Network' if not found
    """
    try:
        # Direct API call to get network details by ID - much more efficient
        network = make_meraki_request(api_key, f"/networks/{network_id}")
        return network.get('name', "Unknown Network")
    except Exception as e:
        logging.error(f"Error getting network name: {str(e)}")
        return "Unknown Network"

def get_network_topology(api_key, network_id):
    """
    Get network topology data using the dedicated Meraki topology endpoint
    
    Args:
        api_key (str): Meraki API key
        network_id (str): Network ID
        
    Returns:
        dict: Network topology data with nodes and links
    """
    # Get network devices
    devices = get_network_devices(api_key, network_id)
    
    # Get network clients with a reasonable timespan (last 3 hours)
    clients = get_network_clients(api_key, network_id, timespan=10800)
    
    # Get topology links directly from Meraki API
    try:
        topology_links = make_meraki_request(api_key, f"/networks/{network_id}/topology/links")
    except Exception as e:
        logging.warning(f"Could not get topology links from API, building manually: {str(e)}")
        topology_links = []
    
    # Initialize topology data
    topology_data = {
        'network_name': get_network_name(api_key, network_id),
        'nodes': [],
        'links': []
    }
    
    # Add devices as nodes
    device_map = {}  # Map serial numbers to node indices
    for i, device in enumerate(devices):
        device_type = 'unknown'
        if 'model' in device and device['model'] is not None:
            model = device['model'].lower()
            if 'mx' in model:
                device_type = 'security_appliance'
            elif 'ms' in model:
                device_type = 'switch'
            elif 'mr' in model:
                device_type = 'wireless'
            elif 'mv' in model:
                device_type = 'camera'
        
        node = {
            'id': device.get('serial', f"device_{i}"),
            'label': device.get('name', 'Unknown Device'),
            'type': device_type,
            'model': device.get('model', 'Unknown'),
            'ip': device.get('lanIp', 'No IP'),
            'mac': device.get('mac', 'No MAC'),
            'serial': device.get('serial', 'No Serial'),
            'firmware': device.get('firmware', 'Unknown'),
            'status': device.get('status', 'unknown')
        }
        
        topology_data['nodes'].append(node)
        device_map[device.get('serial')] = len(topology_data['nodes']) - 1
    
    # Add clients as nodes
    for i, node in enumerate(topology_data['nodes']):
        if node['type'] == 'client':
            # Determine client type based on available information
            client_type = 'unknown'
            if 'deviceTypePrediction' in node and node['deviceTypePrediction'] is not None:
                client_type = node['deviceTypePrediction'].lower()
            elif 'manufacturer' in node and node['manufacturer'] is not None:
                manufacturer = node['manufacturer'].lower()
                if any(mobile in manufacturer for mobile in ['apple', 'samsung', 'lg', 'motorola', 'xiaomi']):
                    client_type = 'mobile'
                elif any(pc in manufacturer for pc in ['dell', 'hp', 'lenovo', 'microsoft', 'asus']):
                    client_type = 'desktop'
        
            # Get the connection details
            connection_details = {
                'type': node.get('recentDeviceConnection', 'Unknown'),
                'vlan': node.get('vlan', 'Unknown'),
                'port': node.get('switchport', 'Unknown'),
                'last_seen': node.get('lastSeen', 'Unknown')
            }
        
            node = {
                'id': node.get('id', f"client_{i}"),
                'label': node.get('description', node.get('mac', 'Unknown Client')),
                'type': 'client',
                'client_type': client_type,
                'ip': node.get('ip', 'No IP'),
                'mac': node.get('mac', 'No MAC'),
                'vlan': node.get('vlan', 'Unknown'),
                'connection': connection_details,
                'usage': node.get('usage', {})
            }
        
            topology_data['nodes'].append(node)
    
    # Add links from the topology endpoint if available
    if topology_links:
        for link in topology_links:
            source_serial = link.get('source', {}).get('serial')
            dest_serial = link.get('destination', {}).get('serial')
            
            if source_serial in device_map and dest_serial in device_map:
                topology_data['links'].append({
                    'source': device_map[source_serial],
                    'target': device_map[dest_serial],
                    'type': link.get('linkType', 'unknown'),
                    'status': link.get('status', 'unknown')
                })
    else:
        # Fallback: build links based on device relationships
        # Connect switches to security appliances
        security_appliances = [i for i, node in enumerate(topology_data['nodes']) 
                            if node['type'] == 'security_appliance']
        switches = [i for i, node in enumerate(topology_data['nodes']) 
                    if node['type'] == 'switch']
        
        # Connect all switches to the first security appliance if available
        if security_appliances and switches:
            for switch in switches:
                topology_data['links'].append({
                    'source': security_appliances[0],
                    'target': switch,
                    'type': 'wired',
                    'status': 'active'
                })
        
        # Connect switches to each other in a chain
        for i in range(len(switches) - 1):
            topology_data['links'].append({
                'source': switches[i],
                'target': switches[i + 1],
                'type': 'wired',
                'status': 'active'
            })
    
    # Connect clients to their parent devices
    for i, node in enumerate(topology_data['nodes']):
        if node['type'] == 'client':
            # Find the device this client is connected to
            connected_to = None
            
            # For wireless clients
            if node.get('connection', {}).get('type') == 'wireless':
                # Find wireless APs
                wireless_aps = [j for j, d in enumerate(topology_data['nodes']) 
                                if d['type'] == 'wireless']
                if wireless_aps:
                    # Connect to the first AP (could be improved with actual connection data)
                    connected_to = wireless_aps[0]
            
            # For wired clients
            elif node.get('connection', {}).get('type') == 'wired':
                # Try to find the switch with matching port
                client_port = node.get('connection', {}).get('port')
                client_vlan = node.get('connection', {}).get('vlan')
                
                for j, device in enumerate(topology_data['nodes']):
                    if device['type'] == 'switch':
                        # In a real implementation, you would check if this switch has the port
                        # the client is connected to. For now, connect to any switch.
                        connected_to = j
                        break
            
            # If we found a device to connect to
            if connected_to is not None:
                topology_data['links'].append({
                    'source': connected_to,
                    'target': i,
                    'type': node.get('connection', {}).get('type', 'unknown'),
                    'status': 'active'
                })
    
    return topology_data

def get_detailed_network_topology(api_key, network_id):
    """
    Get detailed network topology data from the Meraki topology endpoint
    
    Args:
        api_key (str): Meraki API key
        network_id (str): Network ID
        
    Returns:
        dict: Detailed topology data with nodes and links, or None if not available
    """
    try:
        return make_meraki_request(api_key, f"/networks/{network_id}/topology")
    except Exception as e:
        # It's normal for some networks not to support the topology endpoint
        logging.info(f"Could not get detailed topology for network {network_id}: {str(e)}")
        return None

def get_switch_ports(api_key, serial):
    """
    Get switch port information
    
    Args:
        api_key (str): Meraki API key
        serial (str): Switch serial number
        
    Returns:
        list: List of switch ports with status information
    """
    try:
        return make_meraki_request(api_key, f"/devices/{serial}/switch/ports/statuses")
    except Exception as e:
        logging.warning(f"Could not get switch port information for {serial}: {str(e)}")
        return []

# ==================================================
# GET Network Details
# ==================================================
def get_network(api_key, network_id):
    """
    Get details for a specific network
    
    Args:
        api_key (str): Meraki API key
        network_id (str): Network ID
        
    Returns:
        dict: Network details
    """
    endpoint = f"/networks/{network_id}"
    return make_meraki_request(api_key, endpoint)

# ==================================================
# GET Network Topology Links
# ==================================================
def get_network_topology_links(api_key, network_id):
    """
    Get topology links for a network
    
    Args:
        api_key (str): Meraki API key
        network_id (str): Network ID
        
    Returns:
        list: List of topology links
    """
    endpoint = f"/networks/{network_id}/topology/links"
    return make_meraki_request(api_key, endpoint)

# ==================================================
# Helper function for making Meraki API requests
# ==================================================

def make_meraki_request(api_key, endpoint, headers=None, params=None, max_retries=3, retry_delay=1, timeout=30):
    """
    ENHANCED: Make a request to the Meraki API with improved SSL handling for corporate environments
    
    Args:
        api_key (str): Meraki API key
        endpoint (str): The API endpoint URL
        headers (dict): Request headers including API key
        params (dict): Query parameters
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        timeout (int): Request timeout in seconds
        
    Returns:
        dict: JSON response from the API
    """
    import time
    import ssl
    import certifi
    import logging
    import urllib3
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    # Disable SSL warnings for corporate environments
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Ensure endpoint starts with a slash
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    
    # Create default headers if not provided
    if headers is None:
        headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "MerakiCLI-Enhanced/2.6"
        }
    
    # Special handling for known endpoints that might return 404 for some devices
    is_uplink_endpoint = '/uplink' in endpoint
    is_topology_endpoint = '/topology/links' in endpoint
    
    # Create session with enhanced SSL configuration
    session = requests.Session()
    
    # Set up retry strategy
    retry_strategy = Retry(
        total=1,  # Reduced retries to minimize SSL error noise
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    url = f"{BASE_URL}{endpoint}"
    
    # SSL Configuration Priority (try in order)
    ssl_configs = [
        # 1. Try with certifi bundle (most compatible)
        {'verify': certifi.where(), 'name': 'certifi bundle'},
        # 2. Try with system default
        {'verify': True, 'name': 'system default'},
        # 3. Fallback to no verification
        {'verify': False, 'name': 'no verification (corporate fallback)'}
    ]
    
    last_error = None
    
    for config in ssl_configs:
        try:
            session.verify = config['verify']
            
            # Suppress logging for SSL attempts to reduce noise
            if config['verify'] is False:
                logging.getLogger("urllib3").setLevel(logging.ERROR)
            
            response = session.get(
                url, 
                headers=headers, 
                params=params, 
                timeout=timeout
            )
            
            # If we get here, the request succeeded
            response.raise_for_status()
            
            # Log success only on first successful attempt per session
            if not hasattr(make_meraki_request, '_ssl_success_logged'):
                if config['verify']:
                    logging.info(f"✅ SSL verification successful using {config['name']}")
                else:
                    logging.info(f"⚠️ Using SSL bypass mode for corporate environment")
                make_meraki_request._ssl_success_logged = True
            
            return response.json()
            
        except requests.exceptions.SSLError as e:
            last_error = e
            # Don't log SSL errors, just continue to next config
            continue
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Handle specific 404 cases gracefully
                if is_uplink_endpoint:
                    device_serial = endpoint.split('/')[-2] if '/' in endpoint else 'unknown'
                    logging.warning(f"Device {device_serial} does not support uplink information")
                    return []
                elif is_topology_endpoint:
                    logging.warning(f"Topology links not available for this network")
                    return []
                else:
                    logging.error(f"API endpoint not found: {endpoint}")
                    raise
            else:
                logging.error(f"API request failed: {e}")
                raise
                
        except requests.exceptions.RequestException as e:
            last_error = e
            logging.error(f"Request failed: {e}")
            raise
    
    # If we get here, all SSL configs failed
    if last_error:
        logging.error(f"All SSL configurations failed. Last error: {last_error}")
        raise last_error
    else:
        raise Exception("Unknown SSL configuration error")

def store_api_key(api_key):
    """
    Securely store the Meraki API key
    
    Args:
        api_key (str): The Meraki API key to store
    """
    try:
        # Get encryption key
        encryption_key = get_encryption_key()
        f = Fernet(encryption_key)
        
        # Encrypt the API key
        encrypted_key = f.encrypt(api_key.encode())
        
        # Store the encrypted key
        key_path = get_key_path()
        with open(key_path, 'wb') as file:
            file.write(encrypted_key)
        
        print("API key stored securely")
        return True
    except Exception as e:
        print(f"Error storing API key: {str(e)}")
        return False

def load_api_key():
    """
    Load the stored Meraki API key
    
    Returns:
        str: The decrypted API key or None if not found
    """
    try:
        key_path = get_key_path()
        if not os.path.exists(key_path):
            return None
            
        # Get encryption key
        encryption_key = get_encryption_key()
        f = Fernet(encryption_key)
        
        # Read and decrypt the API key
        with open(key_path, 'rb') as file:
            encrypted_key = file.read()
        
        decrypted_key = f.decrypt(encrypted_key)
        return decrypted_key.decode()
    except Exception as e:
        print(f"Error loading API key: {str(e)}")
        return None

def initialize_api_key():
    """
    Initialize API key from environment variable or stored key
    
    Returns:
        str: The API key or None if not found
    """
    try:
        # First try environment variable
        api_key = os.getenv('MERAKI_DASHBOARD_API_KEY')
        if api_key:
            # Store it securely if found in environment
            store_api_key(api_key)
            return api_key
        
        # Try to load stored key
        api_key = load_api_key()
        if api_key:
            return api_key
        
        print("No API key found. Please set the MERAKI_DASHBOARD_API_KEY environment variable or use store_api_key() function.")
        return None
    except Exception as e:
        logging.error(f"Error initializing API key: {str(e)}")
        return None

# End of API implementation
