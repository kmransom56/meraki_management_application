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


# ==================================================
# IMPORT various libraries and modules
# ==================================================
import os
import webbrowser
from flask import Flask, render_template, jsonify
from pathlib import Path
from datetime import datetime
from termcolor import colored
import logging
import threading
import time
import socket
import random
import sys
import requests
import json
import ipaddress
from tabulate import tabulate

# --- Zscaler SSL CA bundle logic ---
ZSCALER_CA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools', 'meraki.pem'))
if os.path.exists(ZSCALER_CA_PATH):
    os.environ['REQUESTS_CA_BUNDLE'] = ZSCALER_CA_PATH

# ==================================================
# IMPORT custom modules
# ==================================================
from modules.meraki import meraki_api 
from modules.meraki import meraki_ms_mr
from modules.meraki import meraki_mx
from modules.meraki import meraki_network
from modules.tools.dnsbl import dnsbl_check
from modules.tools.utilities import tools_ipcheck
from modules.tools.utilities import tools_passgen
from modules.tools.utilities import tools_subnetcalc

# Import term_extra with fallback
try:
    from settings import term_extra
except ImportError:
    # Create a dummy term_extra module if not found
    class DummyTermExtra:
        @staticmethod
        def clear_screen():
            os.system('cls' if os.name == 'nt' else 'clear')
        
        @staticmethod
        def print_ascii_art():
            print("🌐 Cisco Meraki CLI Tool")
            print("=" * 40)
        
        @staticmethod
        def print_footer(footer_text):
            print(footer_text)
    
    term_extra = DummyTermExtra()

from utilities.topology_visualizer import visualize_network_topology

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ==================================================
# Define helper functions
# ==================================================
def select_organization(api_key_or_sdk):
    """
    Select an organization using either API key or SDK wrapper
    
    Args:
        api_key_or_sdk: Either a Meraki API key string or an SDK wrapper object
        
    Returns:
        organization_id: The selected organization ID or None if selection fails
    """
    logging.info(f"Selecting organization with {'SDK wrapper' if not isinstance(api_key_or_sdk, str) else 'custom API'}")
    
    try:
        # Determine if we're using the API key or SDK wrapper
        if isinstance(api_key_or_sdk, str):
            logging.info("Using custom API for organization selection")
            organizations = meraki_api.get_meraki_organizations(api_key_or_sdk)
        else:
            logging.info("Using SDK wrapper for organization selection")
            organizations = api_key_or_sdk.get_organizations()
        
        if organizations:
            print(colored("\nAvailable Organizations:", "cyan"))
            for idx, org in enumerate(organizations, 1):
                print(f"{idx}. {org['name']}")
            
            while True:
                choice = input(colored("\nSelect an Organization (enter the number): ", "cyan"))
                try:
                    selected_index = int(choice) - 1
                    if 0 <= selected_index < len(organizations):
                        org_id = organizations[selected_index]['id']
                        logging.debug(f"Selected organization ID: {org_id}")
                        return org_id
                    else:
                        print(colored("Invalid selection. Please try again.", "red"))
                except ValueError:
                    print(colored("Please enter a number.", "red"))
                    
        else:
            print(colored("No organizations found.", "red"))
            return None
            
    except Exception as api_error:
        logging.error(f"Error in primary organization selection method: {str(api_error)}")
        
        # If we're using the SDK and it failed, try the direct API approach
        if not isinstance(api_key_or_sdk, str):
            logging.info("Attempting fallback to direct API call for organization selection")
            try:
                api_key = api_key_or_sdk.api_key
                organizations = meraki_api.get_meraki_organizations(api_key)
                
                if organizations:
                    print(colored("\nAvailable Organizations (via fallback):", "cyan"))
                    for idx, org in enumerate(organizations, 1):
                        print(f"{idx}. {org['name']}")
                    
                    while True:
                        choice = input(colored("\nSelect an Organization (enter the number): ", "cyan"))
                        try:
                            selected_index = int(choice) - 1
                            if 0 <= selected_index < len(organizations):
                                org_id = organizations[selected_index]['id']
                                logging.debug(f"Selected organization ID (via fallback): {org_id}")
                                return org_id
                            else:
                                print(colored("Invalid selection. Please try again.", "red"))
                        except ValueError:
                            print(colored("Please enter a number.", "red"))
            except Exception as fallback_error:
                logging.error(f"Fallback organization selection also failed: {str(fallback_error)}")
        
        # If all else fails, let the user manually enter an organization ID
        print(colored("\nAutomated organization selection failed. You can manually enter an organization ID if you know it.", "yellow"))
        org_id = input(colored("Enter organization ID (or leave blank to cancel): ", "cyan"))
        if org_id.strip():
            logging.debug(f"Manually entered organization ID: {org_id}")
            return org_id
        
        print(colored("Organization selection cancelled.", "red"))
        return None

# ==================================================
# VISUALIZE submenus for Appliance, Switches and APs
# ==================================================
def submenu_mx(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        options = ["Select an Organization", "Return to Main Menu"]

        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                meraki_mx.select_mx_network(api_key, selected_org['id'])
        elif choice == '2':
            break

def submenu_network_wide(api_key):
    """Submenu for Network Wide operations"""
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│" + " " * 22 + "NETWORK WIDE" + " " * 23 + "│")
        print("│".ljust(59) + "│")
        print("│ 1. Display enhanced network topology".ljust(59) + "│")
        print("│ 2. Display network clients".ljust(59) + "│")
        print("│ 3. Display network devices".ljust(59) + "│")
        print("│ 4. MX Throughput/Speed Test".ljust(59) + "│")
        print("│ 5. Return to main menu".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")
        
        choice = input(colored("\nChoose a menu option [1-5]: ", "cyan"))
        
        if choice == '1':
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    network_name = meraki_api.get_network_name(api_key, network_id)
                    topology_data = meraki_api.get_network_topology(api_key, network_id)
                    if topology_data:
                        topology_data['network_name'] = network_name
                        create_web_visualization(topology_data)
            input(colored("\nPress Enter to continue...", "green"))
        elif choice == '2':
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    clients = meraki_api.get_network_clients(api_key, network_id, timespan=10800)
                    meraki_network.display_network_clients(clients)
            input(colored("\nPress Enter to continue...", "green"))
        elif choice == '3':
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    devices = meraki_api.get_network_devices(api_key, network_id)
                    meraki_network.display_network_devices(devices)
            input(colored("\nPress Enter to continue...", "green"))
        elif choice == '4':
            # MX Throughput/Speed Test submenu
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    from utilities.topology_visualizer import run_mx_throughput_test_cli, run_mx_speed_test_cli
                    print("\n1. Run MX Throughput Test")
                    print("2. Run MX Speed Test")
                    print("3. Return to previous menu")
                    test_choice = input(colored("Choose an option [1-3]: ", "cyan"))
                    if test_choice == '1':
                        run_mx_throughput_test_cli(api_key, network_id)
                    elif test_choice == '2':
                        run_mx_speed_test_cli(api_key, network_id)
                    elif test_choice == '3':
                        pass
                    else:
                        print(colored("Invalid option.", "red"))
                    input(colored("\nPress Enter to continue...", "green"))
        elif choice == '5':
            break
        else:
            print(colored("\nInvalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))

def submenu_sw_and_ap(api_key):
    """Submenu for Switches and APs"""
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│" + " " * 20 + "SWITCHES AND WIRELESS" + " " * 20 + "│")
        print("│".ljust(59) + "│")
        print("│ 1. Display network status".ljust(59) + "│")
        print("│ 2. Display switch ports".ljust(59) + "│")
        print("│ 3. Display clients".ljust(59) + "│")
        print("│ 4. Display SSID".ljust(59) + "│")
        print("│ 5. Return to main menu".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")
        
        choice = input(colored("\nChoose a menu option [1-5]: ", "cyan"))
        
        if choice == '1':
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    devices = meraki_api.get_network_devices(api_key, network_id)
                    meraki_network.display_network_status(devices)
            input(colored("\nPress Enter to continue...", "green"))
        elif choice == '2':
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    meraki_ms_mr.display_switch_ports(api_key, network_id)
            input(colored("\nPress Enter to continue...", "green"))
        elif choice == '3':
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    meraki_ms_mr.display_clients(api_key, network_id)
            input(colored("\nPress Enter to continue...", "green"))
        elif choice == '4':
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    meraki_ms_mr.display_ssid(api_key, network_id)
            input(colored("\nPress Enter to continue...", "green"))
        elif choice == '5':
            break
        else:
            print(colored("\nInvalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))

def create_web_visualization(topology_data):
    """Create and launch web visualization"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'web', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'web', 'static'))
    
    @app.route('/')
    def index():
        return render_template('topology.html')
    
    @app.route('/topology-data')
    def get_topology():
        return jsonify(topology_data)
    
    # Create web directory if it doesn't exist
    web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
    templates_dir = os.path.join(web_dir, 'templates')
    static_dir = os.path.join(web_dir, 'static')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Create HTML template
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Topology Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="controls">
            <div class="search-box">
                <input type="text" id="search" placeholder="Search devices...">
            </div>
            <div class="filter-box">
                <label>Filter by type:</label>
                <select id="deviceFilter">
                    <option value="all">All Devices</option>
                    <option value="switch">Switches</option>
                    <option value="wireless">Wireless</option>
                    <option value="appliance">Appliances</option>
                </select>
            </div>
            <div class="layout-box">
                <label>Layout:</label>
                <select id="layoutType">
                    <option value="force">Force Directed</option>
                    <option value="radial">Radial</option>
                    <option value="hierarchical">Hierarchical</option>
                </select>
            </div>
        </div>
        <div class="stats-panel">
            <h3>Network Statistics</h3>
            <div id="deviceStats"></div>
            <div id="connectionStats"></div>
            <div id="performanceStats"></div>
        </div>
        <div id="topology"></div>
        <div id="tooltip" class="tooltip"></div>
        <script src="{{ url_for('static', filename='topology.js') }}"></script>
    </body>
    </html>
    """

    # Create CSS
    css_content = """
    body {
        margin: 0;
        font-family: Arial, sans-serif;
        background-color: #f0f0f0;
        display: flex;
        flex-direction: column;
    }
    .controls {
        background-color: #fff;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        gap: 20px;
        align-items: center;
    }
    .search-box input {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        width: 200px;
    }
    .filter-box, .layout-box {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    select {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    .stats-panel {
        position: fixed;
        right: 0;
        top: 60px;
        width: 250px;
        background-color: white;
        padding: 15px;
        box-shadow: -2px 0 4px rgba(0,0,0,0.1);
        height: calc(100vh - 60px);
        overflow-y: auto;
    }
    #topology {
        width: calc(100vw - 250px);
        height: calc(100vh - 60px);
        background-color: white;
    }
    .tooltip {
        position: absolute;
        padding: 10px;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        border-radius: 5px;
        pointer-events: none;
        display: none;
    }
    .node circle {
        stroke: #fff;
        stroke-width: 2px;
    }
    .node text {
        font-size: 12px;
    }
    .link {
        stroke: #999;
        stroke-opacity: 0.6;
        stroke-width: 2px;
    }
    .hidden {
        opacity: 0.2;
    }
    """

    # Create JavaScript
    js_content = """
    let currentLayout = 'force';
    let simulation;
    let svg;
    let link;
    let node;
    
    fetch('/topology-data')
        .then(response => response.json())
        .then(data => {
            const width = window.innerWidth - 250;
            const height = window.innerHeight - 60;
            
            svg = d3.select('#topology')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Initialize force simulation
            simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links).id(d => d.id))
                .force('charge', d3.forceManyBody().strength(-1000))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            // Create links
            link = svg.append('g')
                .selectAll('line')
                .data(data.links)
                .join('line')
                .attr('class', 'link');
            
            // Create nodes
            node = svg.append('g')
                .selectAll('g')
                .data(data.nodes)
                .join('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            node.append('circle')
                .attr('r', 20)
                .style('fill', getNodeColor);
            
            node.append('text')
                .attr('dx', 25)
                .attr('dy', '.35em')
                .text(d => d.name);
            
            // Tooltip functionality
            const tooltip = d3.select('#tooltip');
            
            node.on('mouseover', (event, d) => {
                tooltip.style('display', 'block')
                    .html(`
                        <div>
                            <strong>${d.name}</strong><br>
                            Model: ${d.model}<br>
                            Type: ${d.type}<br>
                            Status: ${d.status}
                        </div>
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY + 10) + 'px');
            })
            .on('mouseout', () => {
                tooltip.style('display', 'none');
            });
            
            // Update statistics
            updateStatistics(data);
            
            // Search functionality
            d3.select('#search').on('input', function() {
                const searchTerm = this.value.toLowerCase();
                node.classed('hidden', d => !d.name.toLowerCase().includes(searchTerm));
                link.classed('hidden', d => {
                    const sourceHidden = !d.source.name.toLowerCase().includes(searchTerm);
                    const targetHidden = !d.target.name.toLowerCase().includes(searchTerm);
                    return sourceHidden && targetHidden;
                });
            });
            
            // Device type filter
            d3.select('#deviceFilter').on('change', function() {
                const filterValue = this.value;
                node.classed('hidden', d => filterValue !== 'all' && d.type !== filterValue);
                link.classed('hidden', d => {
                    const sourceHidden = filterValue !== 'all' && d.source.type !== filterValue;
                    const targetHidden = filterValue !== 'all' && d.target.type !== filterValue;
                    return sourceHidden && targetHidden;
                });
            });
            
            // Layout selection
            d3.select('#layoutType').on('change', function() {
                currentLayout = this.value;
                updateLayout();
            });
            
            // Initial layout
            updateLayout();
        });
    
    function getNodeColor(d) {
        switch(d.type) {
            case 'switch': return '#4CAF50';
            case 'wireless': return '#2196F3';
            case 'appliance': return '#F44336';
            default: return '#9E9E9E';
        }
    }
    
    function updateStatistics(data) {
        // Device statistics
        const deviceTypes = d3.group(data.nodes, d => d.type);
        const deviceStats = Array.from(deviceTypes, ([type, nodes]) => ({
            type: type || 'unknown',
            count: nodes.length
        }));
        
        const deviceStatsHtml = `
            <h4>Device Count</h4>
            ${deviceStats.map(stat => `
                <div>${stat.type}: ${stat.count}</div>
            `).join('')}
        `;
        
        // Connection statistics
        const connectionTypes = d3.group(data.links, d => d.type);
        const connectionStats = Array.from(connectionTypes, ([type, links]) => ({
            type: type || 'unknown',
            count: links.length
        }));
        
        const connectionStatsHtml = `
            <h4>Connection Types</h4>
            ${connectionStats.map(stat => `
                <div>${stat.type}: ${stat.count}</div>
            `).join('')}
        `;
        
        // Performance metrics
        const performanceStatsHtml = `
            <h4>Network Performance</h4>
            <div>Active Connections: ${data.links.length}</div>
            <div>Total Devices: ${data.nodes.length}</div>
        `;
        
        d3.select('#deviceStats').html(deviceStatsHtml);
        d3.select('#connectionStats').html(connectionStatsHtml);
        d3.select('#performanceStats').html(performanceStatsHtml);
    }
    
    function updateLayout() {
        simulation.stop();
        
        switch(currentLayout) {
            case 'radial':
                simulation
                    .force('link', d3.forceLink().id(d => d.id).distance(100))
                    .force('charge', d3.forceManyBody().strength(-1000))
                    .force('r', d3.forceRadial(200))
                    .force('center', d3.forceCenter(width / 2, height / 2));
                break;
                
            case 'hierarchical':
                simulation
                    .force('link', d3.forceLink().id(d => d.id).distance(100))
                    .force('charge', d3.forceManyBody().strength(-500))
                    .force('x', d3.forceX())
                    .force('y', d3.forceY().strength(0.1).y(d => d.depth * 100));
                break;
                
            default: // force
                simulation
                    .force('link', d3.forceLink().id(d => d.id))
                    .force('charge', d3.forceManyBody().strength(-1000))
                    .force('center', d3.forceCenter(width / 2, height / 2));
        }
        
        simulation.alpha(1).restart();
    }
    
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    """

    with open(os.path.join(templates_dir, 'topology.html'), 'w') as f:
        f.write(html_content)
    
    with open(os.path.join(static_dir, 'style.css'), 'w') as f:
        f.write(css_content)
    
    with open(os.path.join(static_dir, 'topology.js'), 'w') as f:
        f.write(js_content)
    
    # Find an available port starting from 5001 (since 5000 is used by Docker)
    def find_free_port(start_port=5001):
        for port in range(start_port, start_port + 100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result != 0:  # Port is free
                    return port
            except:
                continue
        return None
    
    # Find available port and start Flask app
    free_port = find_free_port()
    if free_port:
        print(f"\n🌐 Starting topology visualization on http://localhost:{free_port}")
        print("🔄 Opening browser...")
        
        # Start Flask in a separate thread to avoid blocking
        def start_flask():
            app.run(debug=False, port=free_port, host='0.0.0.0')
        
        flask_thread = threading.Thread(target=start_flask, daemon=True)
        flask_thread.start()
        
        # Give Flask a moment to start
        time.sleep(2)
        
        # Open browser
        webbrowser.open(f'http://localhost:{free_port}')
        
        print(f"\n✅ Topology visualization is running on http://localhost:{free_port}")
        print("📝 Press Enter to return to menu (visualization will continue running)...")
        input()
        
    else:
        print("\n❌ Could not find an available port for the web server.")
        print("📝 Press Enter to continue...")
        input()

def network_wide_operations(api_key, organization_id):
    while True:
        term_extra.clear_screen()
        print("\nNetwork-Wide Operations Menu")
        print("=" * 50)
        options = [
            "View Network Health",
            "Monitor Network Clients",
            "View Network Traffic",
            "View Network Latency Stats",
            "Monitor Device Performance",
            "Check Device Uplinks",
            "Generate Network Diagram",
            "Launch Web Visualization",
            "Return to Previous Menu"
        ]
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")

        choice = input(colored("\nChoose an option [1-9]: ", "cyan"))
        
        if choice == '9':
            break
        elif choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
            network_id = meraki_api.select_network(api_key, organization_id)
            if network_id:
                # Get network details for visualization title
                networks = meraki_api.get_organization_networks(api_key, organization_id)
                network_name = "Unknown Network"
                for network in networks:
                    if network.get('id') == network_id:
                        network_name = network.get('name', "Unknown Network")
                        break
                
                if choice == '1':
                    health = meraki_api.get_network_health(api_key, network_id)
                    if health:
                        print(colored("\nNetwork Health Status:", "cyan"))
                        for component, status in health.items():
                            print(f"{component}: {status}")
                elif choice == '2':
                    clients = meraki_api.get_network_clients(api_key, network_id)
                    if clients:
                        print(colored("\nActive Network Clients:", "cyan"))
                        for client in clients:
                            print(f"Description: {client.get('description', 'N/A')}")
                            print(f"IP: {client.get('ip', 'N/A')}")
                            print(f"MAC: {client.get('mac', 'N/A')}")
                            print(f"Status: {client.get('status', 'N/A')}")
                            print("-" * 30)
                elif choice == '3':
                    traffic = meraki_api.get_network_traffic(api_key, network_id)
                    if traffic:
                        print(colored("\nNetwork Traffic Analysis:", "cyan"))
                        for flow in traffic:
                            print(f"Application: {flow.get('application', 'N/A')}")
                            print(f"Destination: {flow.get('destination', 'N/A')}")
                            print(f"Protocol: {flow.get('protocol', 'N/A')}")
                            print(f"Usage: {flow.get('usage', {}).get('total', 0)} bytes")
                            print("-" * 30)
                elif choice == '4':
                    stats = meraki_api.get_network_latency_stats(api_key, network_id)
                    if stats:
                        print(colored("\nNetwork Latency Statistics:", "cyan"))
                        for stat in stats:
                            print(f"Type: {stat.get('type', 'N/A')}")
                            print(f"Latency: {stat.get('latencyMs', 'N/A')} ms")
                            print(f"Loss: {stat.get('lossPercentage', 'N/A')}%")
                            print("-" * 30)
                elif choice == '5':
                    devices = meraki_api.get_meraki_devices(api_key, network_id)
                    if devices:
                        print(colored("\nSelect a device:", "cyan"))
                        for i, device in enumerate(devices, 1):
                            print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                        device_choice = input(colored("\nChoose a device number: ", "cyan"))
                        if device_choice.isdigit() and 1 <= int(device_choice) <= len(devices):
                            device = devices[int(device_choice) - 1]
                            performance = meraki_api.get_device_performance(api_key, device['serial'])
                            if performance:
                                print(colored(f"\nPerformance stats for {device.get('name')}:", "cyan"))
                                print(f"CPU: {performance.get('cpu', 'N/A')}%")
                                print(f"Memory: {performance.get('memory', 'N/A')}%")
                                print(f"Disk: {performance.get('disk', 'N/A')}%")
                elif choice == '6':
                    devices = meraki_api.get_meraki_devices(api_key, network_id)
                    if devices:
                        print(colored("\nSelect a device:", "cyan"))
                        for i, device in enumerate(devices, 1):
                            print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                        device_choice = input(colored("\nChoose a device number: ", "cyan"))
                        if device_choice.isdigit() and 1 <= int(device_choice) <= len(devices):
                            device = devices[int(device_choice) - 1]
                            uplink = meraki_api.get_device_uplink(api_key, device['serial'])
                            if uplink:
                                print(colored(f"\nUplink info for {device.get('name')}:", "cyan"))
                                for interface in uplink:
                                    print(f"Interface: {interface.get('interface', 'N/A')}")
                                    print(f"Status: {interface.get('status', 'N/A')}")
                                    print(f"IP: {interface.get('ip', 'N/A')}")
                                    print("-" * 30)
                elif choice == '7':
                    print(colored("\nGenerating enhanced network diagram...", "cyan"))
                    try:
                        # Get network devices
                        devices = meraki_api.get_network_devices(api_key, network_id)
                        
                        # Get network clients
                        clients = meraki_api.get_network_clients(api_key, network_id)
                        
                        # Try to get topology links from API
                        links = None
                        try:
                            links = meraki_api.get_network_topology_links(api_key, network_id)
                        except Exception as e:
                            logging.warning(f"Could not get topology links from API, building manually: {str(e)}")
                        
                        # Get network details for name
                        network_details = meraki_api.get_network(api_key, network_id)
                        network_name = network_details.get('name', 'Network')
                        
                        # Import the topology building and visualization functions
                        from utilities.topology_visualizer import build_topology_from_api_data, visualize_network_topology
                        
                        # Build the topology with the collected data
                        # Robust error handling for API responses
                        if not isinstance(devices, list) or not devices:
                            print("\n[ERROR] Devices data is empty or invalid. Cannot generate visualization.")
                            logging.error(f"Devices API response: {devices}")
                            return
                        if not isinstance(clients, list):
                            print("\n[ERROR] Clients data is invalid. Cannot generate visualization.")
                            logging.error(f"Clients API response: {clients}")
                            return
                        topology = build_topology_from_api_data(devices, clients, links)
                        print("\n[DEBUG] Devices:", devices)
                        print("[DEBUG] Clients:", clients)
                        print("[DEBUG] Topology:", topology)
                        # Display summary of the topology
                        print("\nNetwork Topology Summary:")
                        print(f"Devices: {len(devices)}")
                        print(f"Clients: {len(clients)}")
                        print(f"Connections: {len(topology['links'])}")
                        # Display device types
                        device_types = {}
                        for node in topology.get('nodes', []):
                            node_type = node.get('type', 'unknown')
                            device_types[node_type] = device_types.get(node_type, 0) + 1
                        print("\nDevice Types:")
                        for device_type, count in device_types.items():
                            print(f"{device_type}: {count}")
                        # Display devices
                        print("\nDevices:")
                        device_table = []
                        for device in devices:
                            device_table.append([
                                device.get('name', 'Unknown'),
                                device.get('model', 'Unknown'),
                                device.get('type', 'Unknown'),
                                device.get('lanIp', device.get('ip', 'Unknown')),
                                "Yes" if device.get('uplinkSupported', False) else "No"
                            ])
                        print(tabulate(device_table, headers=['Name', 'Model', 'Type', 'IP Address', 'Uplink Support'], 
                                      tablefmt='pretty'))
                        # Display sample of clients
                        print("\nClient Devices (sample):")
                        client_table = []
                        for client in clients[:10]:  # Show first 10 clients
                            client_table.append([
                                client.get('description', client.get('dhcpHostname', client.get('hostname', 'Unknown'))),
                                client.get('deviceType', 'unknown'),
                                client.get('ip', 'Unknown'),
                                client.get('mac', 'Unknown'),
                                client.get('vlan', 'Unknown')
                            ])
                        print(tabulate(client_table, headers=['Name', 'Type', 'IP Address', 'MAC', 'VLAN'], 
                                      tablefmt='pretty'))
                        if len(clients) > 10:
                            print(f"... and {len(clients) - 10} more clients")
                        # Improved visualization logic: warn if partial data
                        if not topology.get('nodes') or not topology.get('links'):
                            print("\n[WARNING] Topology data is incomplete. Generating minimal visualization.")
                            # Optionally, generate a minimal HTML with a warning message
                            minimal_topology = topology if topology.get('nodes') else {'nodes': [], 'links': []}
                            html_path = visualize_network_topology(minimal_topology, network_name)
                            if html_path:
                                print(colored(f"\nMinimal network topology visualization saved to {html_path}", "yellow"))
                                print(colored("The visualization has been opened in your default web browser.", "yellow"))
                            else:
                                print(colored("\nFailed to generate minimal network topology visualization.", "red"))
                        else:
                            html_path = visualize_network_topology(topology, network_name)
                            if html_path:
                                print(colored(f"\nNetwork topology visualization saved to {html_path}", "green"))
                                print(colored("The visualization has been opened in your default web browser.", "green"))
                            else:
                                print(colored("\nFailed to generate network topology visualization.", "red"))
                    except Exception as e:
                        logging.error(f"Error generating network diagram: {str(e)}")
                        print(colored(f"\nError generating network diagram: {str(e)}", "red"))
                    
                    input("\nPress Enter to continue...")
                elif choice == '8':
                    # Launch web visualization directly
                    print(colored("\nLaunching enhanced web visualization...", "cyan"))
                    try:
                        # Get network devices
                        devices = meraki_api.get_network_devices(api_key, network_id)
                        
                        # Get network clients
                        clients = meraki_api.get_network_clients(api_key, network_id)
                        
                        # Try to get topology links from API
                        links = None
                        try:
                            links = meraki_api.get_network_topology_links(api_key, network_id)
                        except Exception as e:
                            logging.warning(f"Could not get topology links from API, building manually: {str(e)}")
                        
                        # Get network details for name
                        network_details = meraki_api.get_network(api_key, network_id)
                        network_name = network_details.get('name', 'Network')
                        
                        # Import the topology building and visualization functions
                        from utilities.topology_visualizer import build_topology_from_api_data, visualize_network_topology
                        
                        # Build the topology with the collected data
                        topology = build_topology_from_api_data(devices, clients, links)
                        
                        # Generate and open the visualization
                        html_path = visualize_network_topology(topology, network_name)
                        if html_path:
                            print(colored(f"\nNetwork topology visualization saved to {html_path}", "green"))
                            print(colored("The visualization has been opened in your default web browser.", "green"))
                        else:
                            print(colored("\nFailed to generate network topology visualization.", "red"))
                    except Exception as e:
                        logging.error(f"Error launching web visualization: {str(e)}")
                        print(colored(f"\nError launching web visualization: {str(e)}", "red"))
                    
                    input("\nPress Enter to continue...")
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


# ==================================================
# DEFINE how to process data inside Networks
# ==================================================
def select_network(api_key_or_sdk, organization_id):
    """
    Select a network using either API key or SDK wrapper with enhanced selection options
    
    Args:
        api_key_or_sdk: Either a Meraki API key string or an SDK wrapper object
        organization_id: The organization ID to get networks from
        
    Returns:
        network_id: The selected network ID or None if selection fails
    """
    logging.info(f"Selecting network for organization {organization_id}")
    
    try:
        # Determine if we're using the API key or SDK wrapper
        if isinstance(api_key_or_sdk, str):
            logging.info("Using custom API for network selection")
            networks = meraki_api.get_organization_networks(api_key_or_sdk, organization_id)
        else:
            logging.info("Using SDK wrapper for network selection")
            networks = api_key_or_sdk.get_organization_networks(organization_id)
        
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
        
        while True:
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
                    logging.debug(f"Selected network: {selected_network['name']} (ID: {network_id})")
                    return network_id
                else:
                    print(colored("Invalid network number. Please try again.", "red"))
                    input("Press Enter to continue...")
            else:
                print(colored("Invalid choice. Please try again.", "red"))
                input("Press Enter to continue...")
                
    except Exception as e:
        logging.error(f"Error in primary network selection method: {str(e)}")
        
        # If we're using the SDK and it failed, try the direct API approach
        if not isinstance(api_key_or_sdk, str):
            logging.info("Attempting fallback to direct API call for network selection")
            try:
                api_key = api_key_or_sdk.api_key
                networks = meraki_api.get_organization_networks(api_key, organization_id)
                
                if networks:
                    print(colored("\nAvailable Networks (via fallback):", "cyan"))
                    for i, network in enumerate(networks, 1):
                        print(f"{i}. {network['name']}")
                    
                    while True:
                        try:
                            choice = int(input(colored("\nSelect a network (number): ", "cyan")))
                            if 1 <= choice <= len(networks):
                                network_id = networks[choice - 1]['id']
                                logging.debug(f"Selected network ID (via fallback): {network_id}")
                                return network_id
                            else:
                                print(colored("Invalid choice. Please try again.", "red"))
                        except ValueError:
                            print(colored("Please enter a valid number.", "red"))
            except Exception as fallback_error:
                logging.error(f"Fallback network selection also failed: {str(fallback_error)}")
        
                # If all else fails, let the user manually enter a network ID
                print(colored("\nAutomated network selection failed. You can manually enter a network ID if you know it.", "yellow"))
                network_id = input(colored("Enter network ID (or leave blank to cancel): ", "cyan"))
                if network_id.strip():
                    logging.debug(f"Manually entered network ID: {network_id}")
                    return network_id
                
                print(colored("Network selection cancelled.", "red"))
                return None

# ==================================================
# DEFINE the Swiss Army Knife submenu
# ==================================================
def swiss_army_knife_submenu(fernet):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()

        options = [
            "DNSBL Check",
            "IP Check",
            "MTU Correct Size Calculator [under dev]",
            "Password Generator",
            "Subnet Calculator",
            "WiFi Spectrum Analyzer [under dev]",
            "WiFi Adapter Info [under dev]",
            "WiFi Neighbors [under dev]",
            "Return to Main Menu"
        ]

        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("Choose a menu option [1-9]: ", "cyan"))

        if choice == '1':
            dnsbl_check.main()
        elif choice == '2':
            tools_ipcheck.main(fernet)
        elif choice == '3':
            pass
        elif choice == '4':
            tools_passgen.main()
        elif choice == '5':
            tools_subnetcalc.main()
        elif choice == '6':
            pass
        elif choice == '7':
            pass
        elif choice == '8':
            pass
        elif choice == '9':
            break
        else:
            print(colored("Invalid input. Please enter a number between 1 and 9.", "red"))


def submenu_environmental(api_key):
    while True:
        term_extra.clear_screen()
        print("\nEnvironmental Monitoring Menu")
        print("=" * 50)
        options = [
            "View Current Sensor Alerts",
            "View Sensor Readings",
            "View Sensor Relationships",
            "Return to Main Menu"
        ]
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")

        choice = input(colored("\nChoose an option [1-4]: ", "cyan"))
        
        if choice == '4':
            break
        elif choice in ['1', '2', '3']:
            organization_id = select_organization(api_key)
            if organization_id:
                network_id = select_network(api_key, organization_id)
                if network_id:
                    if choice == '1':
                        alerts = meraki_api.get_network_sensor_alerts(api_key, network_id)
                        if alerts:
                            print(colored("\nCurrent Sensor Alerts:", "cyan"))
                            for metric, count in alerts.items():
                                print(f"{metric}: {count} alerts")
                    elif choice == '2':
                        devices = meraki_api.get_meraki_devices(api_key, network_id)
                        if devices:
                            print(colored("\nSelect a sensor device:", "cyan"))
                            sensor_devices = [d for d in devices if d.get('model', '').startswith('MT')]
                            for i, device in enumerate(sensor_devices, 1):
                                print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                            device_choice = input(colored("\nChoose a device number: ", "cyan"))
                            if device_choice.isdigit() and 1 <= int(device_choice) <= len(sensor_devices):
                                device = sensor_devices[int(device_choice) - 1]
                                readings = meraki_api.get_device_sensor_data(api_key, device['serial'])
                                if readings:
                                    print(colored(f"\nLatest readings for {device.get('name')}:", "cyan"))
                                    for metric, value in readings.items():
                                        print(f"{metric}: {value}")
                    elif choice == '3':
                        devices = meraki_api.get_meraki_devices(api_key, network_id)
                        if devices:
                            print(colored("\nSelect a sensor device:", "cyan"))
                            sensor_devices = [d for d in devices if d.get('model', '').startswith('MT')]
                            for i, device in enumerate(sensor_devices, 1):
                                print(f"{i}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                            device_choice = input(colored("\nChoose a device number: ", "cyan"))
                            if device_choice.isdigit() and 1 <= int(device_choice) <= len(sensor_devices):
                                device = sensor_devices[int(device_choice) - 1]
                                relationships = meraki_api.get_device_sensor_relationships(api_key, device['serial'])
                                if relationships:
                                    print(colored(f"\nSensor relationships for {device.get('name')}:", "cyan"))
                                    for rel in relationships:
                                        print(f"Role: {rel.get('role')}")
                                        print(f"Target: {rel.get('target')}")
                    input(colored("\nPress Enter to continue...", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


def submenu_organization(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        print("\nOrganization Menu")
        print("=" * 50)
        print("1. Select Organization")
        print("2. Return to Main Menu")
        
        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            try:
                # Direct debugging to show the exact error
                print(colored("\nAttempting to get organizations...", "yellow"))
                try:
                    # Try to get organizations directly
                    import requests
                    import platform
                    import certifi
                    import traceback
                    
                    # Configure SSL verification based on the platform
                    if platform.system() == 'Windows':
                        verify = False
                    else:
                        verify = certifi.where()
                    
                    # Make direct API call with detailed error handling
                    headers = {
                        "X-Cisco-Meraki-API-Key": api_key,
                        "Content-Type": "application/json"
                    }
                    
                    print(colored("Making direct API call to Meraki...", "yellow"))
                    try:
                        response = requests.get(
                            "https://api.meraki.com/api/v1/organizations",
                            headers=headers,
                            verify=verify,
                            timeout=30
                        )
                        
                        print(colored(f"API Response Status: {response.status_code}", "yellow"))
                        
                        if response.status_code == 200:
                            organizations = response.json()
                            print(colored(f"Found {len(organizations)} organizations", "green"))
                            
                            # Display organizations for selection
                            print(colored("\nAvailable Organizations:", "cyan"))
                            for idx, org in enumerate(organizations, 1):
                                print(f"{idx}. {org['name']}")
                            
                            choice = input(colored("\nSelect an Organization (enter the number): ", "cyan"))
                            try:
                                selected_index = int(choice) - 1
                                if 0 <= selected_index < len(organizations):
                                    organization_id = organizations[selected_index]['id']
                                    
                                    # Get organization details to display the name
                                    selected_org = organizations[selected_index]
                                    
                                    term_extra.clear_screen()
                                    term_extra.print_ascii_art()
                                    print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                                
                                    # Log the selected organization ID
                                    logging.debug(f"Selected organization ID: {organization_id}")
                                
                                    while True:
                                        print("\nOrganization Operations")
                                        print("=" * 50)
                                        print("1. View Organization Status")
                                        print("2. View Organization Networks")
                                        print("3. View Organization Devices")
                                        print("4. Return to Organization Menu")
                                        
                                        sub_choice = input(colored("\nChoose an option [1-4]: ", "cyan"))
                                        
                                        if sub_choice == '1':
                                            meraki_network.display_organization_status(api_key, organization_id)
                                        elif sub_choice == '2':
                                            meraki_network.display_organization_networks(api_key, organization_id)
                                        elif sub_choice == '3':
                                            meraki_network.display_organization_devices(api_key, organization_id)
                                        elif sub_choice == '4':
                                            break
                                        else:
                                            print(colored("\nInvalid choice. Please try again.", "red"))
                                        
                                        input(colored("\nPress Enter to continue...", "green"))
                                else:
                                    print(colored("Invalid selection.", "red"))
                            except ValueError:
                                print(colored("Please enter a number.", "red"))
                        else:
                            print(colored(f"API Error: {response.status_code} - {response.text}", "red"))
                    except Exception as api_error:
                        print(colored(f"API Call Error: {str(api_error)}", "red"))
                        traceback.print_exc()
                except Exception as debug_error:
                    print(colored(f"Debug Error: {str(debug_error)}", "red"))
                    traceback.print_exc()
                
                input(colored("\nPress Enter to continue...", "green"))
            except Exception as e:
                print(colored(f"\nError in organization menu: {str(e)}", "red"))
                traceback.print_exc()
                input(colored("\nPress Enter to continue...", "green"))
        
        elif choice == '2':
            break
        else:
            print(colored("\nInvalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


def submenu_device(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        print("\nDevice Menu")
        print("=" * 50)
        print("1. Switch Operations")
        print("2. Access Point Operations")
        print("3. Return to Main Menu")
        
        choice = input(colored("\nChoose a menu option [1-3]: ", "cyan"))
        
        if choice == '1':
            organization_id = select_organization(api_key)
            if organization_id:
                # Get organization details to display the name
                organizations = meraki_api.get_meraki_organizations(api_key)
                selected_org = next((org for org in organizations if org['id'] == organization_id), None)
                
                if selected_org:
                    term_extra.clear_screen()
                    term_extra.print_ascii_art()
                    print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                    switch_operations(api_key, organization_id)
        elif choice == '2':
            organization_id = select_organization(api_key)
            if organization_id:
                # Get organization details to display the name
                organizations = meraki_api.get_meraki_organizations(api_key)
                selected_org = next((org for org in organizations if org['id'] == organization_id), None)
                
                if selected_org:
                    term_extra.clear_screen()
                    term_extra.print_ascii_art()
                    print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                    access_point_operations(api_key, organization_id)
        elif choice == '3':
            break
        else:
            print(colored("\nInvalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


def submenu_network_status(api_key):
    """Alias for submenu_network_wide for backward compatibility."""
    return submenu_network_wide(api_key)


def main_menu_handler(api_key, choice):
    """Handle main menu choices"""
    if choice == '1':
        submenu_mx(api_key)
    elif choice == '2':
        submenu_sw_and_ap(api_key)
    elif choice == '3':
        submenu_environmental(api_key)
    elif choice == '4':
        submenu_organization(api_key)
    elif choice == '5':
        network_wide_operations(api_key, select_organization(api_key))
    elif choice == '6':
        submenu_device(api_key)
    elif choice == '7':
        submenu_network_status(api_key)
    elif choice == '8':
        print(colored("\nExiting...", "yellow"))
        return False
    else:
        print(colored("\nInvalid choice. Please try again.", "red"))
        input(colored("\nPress Enter to continue...", "green"))
    
    return True

def network_wide_operations_sdk(sdk_wrapper, organization_id):
    """Network-wide operations using the Meraki SDK wrapper"""
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        print("\nNetwork-Wide Operations Menu")
        print("=" * 50)
        options = [
            "View Network Health",
            "Monitor Network Clients",
            "View Network Traffic",
            "View Network Latency Stats",
            "Monitor Device Performance",
            "Check Device Uplinks",
            "Generate Network Diagram",
            "Launch Web Visualization",
            "Return to Previous Menu"
        ]
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")

        choice = input(colored("\nChoose an option [1-9]: ", "cyan"))
        
        if choice == '9':
            break
        elif choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
            network_id = select_network(sdk_wrapper, organization_id)
            if network_id:
                # Get network details for visualization title
                networks = sdk_wrapper.get_organization_networks(organization_id)
                network_name = next((n['name'] for n in networks if n['id'] == network_id), "Unknown Network")
                
                if choice == '1':
                    # View Network Health
                    print(colored(f"\nNetwork Health for {network_name}:", "cyan"))
                    health_data = sdk_wrapper.get_network_health(network_id)
                    meraki_network.display_network_health(health_data)
                elif choice == '2':
                    # Monitor Network Clients
                    clients = sdk_wrapper.get_network_clients(network_id, timespan=10800)
                    meraki_network.display_network_clients(clients)
                elif choice == '3':
                    # View Network Traffic
                    meraki_network.display_network_traffic(sdk_wrapper, network_id)
                elif choice == '4':
                    # View Network Latency Stats
                    latency_stats = sdk_wrapper.get_network_latency_stats(network_id)
                    meraki_network.display_network_latency(latency_stats)
                elif choice == '5':
                    # Monitor Device Performance
                    devices = sdk_wrapper.get_network_devices(network_id)
                    if devices:
                        print(colored(f"\nDevices in {network_name}:", "cyan"))
                        meraki_network.display_network_devices(devices)
                        
                        # Allow selecting a device for detailed performance
                        print(colored("\nSelect a device to view performance:", "cyan"))
                        for idx, device in enumerate(devices, 1):
                            print(f"{idx}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                        
                        device_choice = input(colored("\nEnter device number (or press Enter to skip): ", "cyan"))
                        if device_choice.strip() and device_choice.isdigit():
                            device_idx = int(device_choice) - 1
                            if 0 <= device_idx < len(devices):
                                device = devices[device_idx]
                                serial = device.get('serial')
                                if serial:
                                    performance = sdk_wrapper.get_device_performance(serial)
                                    meraki_network.display_device_performance(device, performance)
                                else:
                                    print(colored("\nNo serial number available for this device.", "yellow"))
                            else:
                                print(colored("\nInvalid device selection.", "red"))
                    else:
                        print(colored("\nNo devices found in this network.", "yellow"))
                elif choice == '6':
                    # Check Device Uplinks
                    devices = sdk_wrapper.get_network_devices(network_id)
                    if devices:
                        print(colored(f"\nDevices with uplink information in {network_name}:", "cyan"))
                        uplink_devices = [d for d in devices if d.get('supports_uplink', False)]
                        
                        if uplink_devices:
                            for idx, device in enumerate(uplink_devices, 1):
                                print(f"{idx}. {device.get('name', 'Unknown')} ({device.get('model', 'Unknown')})")
                            
                            device_choice = input(colored("\nEnter device number to check uplinks: ", "cyan"))
                            if device_choice.strip() and device_choice.isdigit():
                                device_idx = int(device_choice) - 1
                                if 0 <= device_idx < len(uplink_devices):
                                    device = uplink_devices[device_idx]
                                    serial = device.get('serial')
                                    if serial:
                                        uplink = sdk_wrapper.get_device_uplink(serial)
                                        print(colored(f"\nUplink information for {device.get('name')}:", "cyan"))
                                        if uplink:
                                            for interface in uplink:
                                                print(f"Interface: {interface.get('interface', 'N/A')}")
                                                print(f"Status: {interface.get('status', 'N/A')}")
                                                print(f"IP: {interface.get('ip', 'N/A')}")
                                                print("-" * 30)
                                        else:
                                            print(colored("No uplink information available.", "yellow"))
                                    else:
                                        print(colored("\nNo serial number available for this device.", "yellow"))
                                else:
                                    print(colored("\nInvalid device selection.", "red"))
                        else:
                            print(colored("\nNo devices with uplink support found in this network.", "yellow"))
                    else:
                        print(colored("\nNo devices found in this network.", "yellow"))
                elif choice == '7':
                    # Generate enhanced network diagram with device type detection
                    print(colored("\nGenerating enhanced network diagram...", "cyan"))
                    try:
                        # Get network devices
                        devices = sdk_wrapper.get_network_devices(network_id)
                        
                        # Get network clients
                        clients = sdk_wrapper.get_network_clients(network_id)
                        
                        # Try to get topology links from API
                        links = None
                        try:
                            links = sdk_wrapper.get_network_topology_links(network_id)
                        except Exception as e:
                            logging.warning(f"Could not get topology links from API, building manually: {str(e)}")
                        
                        # Get network details for name
                        network_details = sdk_wrapper.get_network(network_id)
                        network_name = network_details.get('name', 'Network')
                        
                        # Import the topology building and visualization functions
                        from utilities.topology_visualizer import build_topology_from_api_data, visualize_network_topology
                        
                        # Build the topology with the collected data
                        topology = build_topology_from_api_data(devices, clients, links)
                        
                        # Display summary of the topology
                        print("\nNetwork Topology Summary:")
                        print(f"Devices: {len(devices)}")
                        print(f"Clients: {len(clients)}")
                        print(f"Connections: {len(topology['links'])}")
                        
                        # Display device types
                        device_types = {}
                        for node in topology['nodes']:
                            node_type = node.get('type', 'unknown')
                            device_types[node_type] = device_types.get(node_type, 0) + 1
                        
                        print("\nDevice Types:")
                        for device_type, count in device_types.items():
                            print(f"{device_type}: {count}")
                        
                        # Display devices
                        print("\nDevices:")
                        device_table = []
                        for device in devices:
                            device_table.append([
                                device.get('name', 'Unknown'),
                                device.get('model', 'Unknown'),
                                device.get('type', 'Unknown'),
                                device.get('lanIp', device.get('ip', 'Unknown')),
                                "Yes" if device.get('uplinkSupported', False) else "No"
                            ])
                        
                        print(tabulate(device_table, headers=['Name', 'Model', 'Type', 'IP Address', 'Uplink Support'], 
                                      tablefmt='pretty'))
                        
                        # Display devices
                        print("\nClient Devices (sample):")
                        client_table = []
                        # Show up to 10 clients
                        for node in topology['nodes']:
                            if node.get('type') == 'client':
                                client_table.append([
                                    node.get('label', 'Unknown'),
                                    node.get('client_type', 'Unknown'),
                                    node.get('ip', 'Unknown'),
                                    node.get('mac', 'Unknown'),
                                    node.get('vlan', 'Unknown')
                                ])
                        
                        print(tabulate(client_table, 
                                      headers=['Name', 'Type', 'IP Address', 'MAC', 'VLAN'], 
                                      tablefmt='pretty'))
                        
                        if len(topology['nodes']) > 10:
                            print(f"... and {len(topology['nodes']) - 10} more clients")
                        
                        # Generate and open the visualization
                        html_path = visualize_network_topology(topology, network_name)
                        if html_path:
                            print(colored(f"\nNetwork topology visualization saved to {html_path}", "green"))
                            print(colored("The visualization has been opened in your default web browser.", "green"))
                        else:
                            print(colored("\nFailed to generate network topology visualization.", "red"))
                    except Exception as e:
                        logging.error(f"Error generating network diagram: {str(e)}")
                        print(colored(f"\nError generating network diagram: {str(e)}", "red"))
                    
                    input("\nPress Enter to continue...")
                elif choice == '8':
                    # Launch web visualization directly
                    print(colored("\nLaunching enhanced web visualization...", "cyan"))
                    topology = sdk_wrapper.get_network_topology(network_id)
                    if topology:
                        visualize_network_topology(topology, network_name)
                        print(colored("\nNetwork visualization opened in your web browser.", "green"))
                    else:
                        print(colored("\nNo topology data available for this network.", "yellow"))
                input(colored("\nPress Enter to continue...", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))

def launch_interactive_cli():
    """
    Open a new terminal window and run the interactive CLI (main.py) for non-technical users.
    """
    import subprocess
    import sys
    import platform
    import os
    
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))
    
    if platform.system() == 'Windows':
        # Use PowerShell to open a new window and run main.py
        command = f'powershell -NoExit -Command "python \"{main_py}\""'
        subprocess.Popen(["pwsh.exe", "-NoExit", "-Command", f'python \"{main_py}\"'], creationflags=subprocess.CREATE_NEW_CONSOLE)
    elif platform.system() == 'Darwin':
        subprocess.Popen(["open", "-a", "Terminal", f"python3 '{main_py}'"])
    else:
        try:
            subprocess.Popen(["gnome-terminal", "--", "python3", main_py])
        except FileNotFoundError:
            try:
                subprocess.Popen(["x-terminal-emulator", "-e", f"python3 '{main_py}'"])
            except FileNotFoundError:
                print("Could not launch a new terminal window. Please run main.py manually.")

def main_menu():
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        print("\nMain Menu")
        print("=" * 50)
        print("1. MX Operations")
        print("2. Switch & AP Operations")
        print("3. Environmental Monitoring")
        print("4. Organization Operations")
        print("5. Network-Wide Operations")
        print("6. Device Operations")
        print("7. Network Status (Legacy)")
        print("8. Exit")
        print("9. Launch Interactive CLI (New Terminal)")  # New button/option
        choice = input(colored("\nChoose a menu option [1-9]: ", "cyan"))
        if choice == '9':
            launch_interactive_cli()
            input(colored("\nInteractive CLI launched in a new terminal. Press Enter to return to the menu...", "green"))
        else:
            if not main_menu_handler(api_key, choice):
                break


# ENHANCED TOPOLOGY VISUALIZATION FIXES

def display_enhanced_network_topology_fixed(api_key_or_sdk):
    """
    ENHANCED: Display network topology with improved error handling and device visibility
    """
    import threading
    import time
    import socket
    from flask import Flask, render_template, jsonify
    
    logging.info("Starting enhanced network topology visualization with fixes")
    
    try:
        # Select organization
        organization_id = select_organization(api_key_or_sdk)
        if not organization_id:
            print("❌ No organization selected")
            return
        
        # Select network
        network_id = select_network(api_key_or_sdk, organization_id)
        if not network_id:
            print("❌ No network selected")
            return
        
        # Get enhanced topology data with better error handling
        topology_data = get_enhanced_topology_data(api_key_or_sdk, network_id)
        
        if not topology_data or not topology_data.get('devices'):
            print("⚠️  No topology data available or no devices found")
            print("This might be due to:")
            print("  - Network has no devices")
            print("  - API permissions issue")
            print("  - Network connectivity problems")
            return
        
        print(f"✅ Found topology data:")
        print(f"   📊 Network: {topology_data.get('network_name', 'Unknown')}")
        print(f"   🔧 Devices: {len(topology_data.get('devices', []))}")
        print(f"   💻 Clients: {len(topology_data.get('clients', []))}")
        
        # Start Flask app with enhanced data
        start_enhanced_topology_server(topology_data)
        
    except Exception as e:
        logging.error(f"Error in enhanced topology visualization: {e}")
        print(f"❌ Error: {e}")
        
def get_enhanced_topology_data(api_key_or_sdk, network_id):
    """Get topology data with enhanced error handling."""
    
    try:
        # Determine API method
        if isinstance(api_key_or_sdk, str):
            api_key = api_key_or_sdk
        else:
            # SDK wrapper - extract API key if possible
            api_key = getattr(api_key_or_sdk, 'api_key', None)
            if not api_key:
                raise Exception("Cannot extract API key from SDK wrapper")
        
        # Get network details
        network = meraki_api.make_meraki_request(api_key, f"/networks/{network_id}")
        
        # Get devices with error handling
        devices = meraki_api.make_meraki_request(api_key, f"/networks/{network_id}/devices")
        if not devices:
            devices = []
        
        # Get clients with error handling
        try:
            clients = meraki_api.make_meraki_request(
                api_key, 
                f"/networks/{network_id}/clients",
                params={'perPage': 1000, 'timespan': 10800}
            )
            if not clients:
                clients = []
        except Exception as e:
            logging.warning(f"Could not get clients: {e}")
            clients = []
        
        # Try to get topology links
        topology_links = []
        try:
            topology_links = meraki_api.make_meraki_request(api_key, f"/networks/{network_id}/topology/links")
        except Exception as e:
            logging.warning(f"Could not get topology links: {e}")
        
        # Build comprehensive topology data
        topology_data = {
            'network': network,
            'network_name': network.get('name', 'Unknown Network'),
            'devices': devices,
            'clients': clients,
            'topology_links': topology_links,
            'statistics': {
                'deviceCount': len(devices),
                'clientCount': len(clients),
                'networkId': network_id
            }
        }
        
        return topology_data
        
    except Exception as e:
        logging.error(f"Error getting enhanced topology data: {e}")
        raise

def start_enhanced_topology_server(topology_data):
    """Start Flask server with enhanced topology data."""
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template('enhanced_topology.html')
    
    @app.route('/topology-data')
    def get_topology_data():
        """Provide enhanced topology data as JSON."""
        try:
            # Process the data for better visualization
            processed_data = process_topology_for_visualization(topology_data)
            return jsonify(processed_data)
        except Exception as e:
            logging.error(f"Error serving topology data: {e}")
            return jsonify({'error': str(e), 'devices': [], 'clients': []})
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'devices': len(topology_data.get('devices', [])),
            'clients': len(topology_data.get('clients', []))
        })
    
    # Find available port
    port = find_available_port(5001)
    
    print(f"🌐 Starting topology visualization on http://localhost:{port}")
    print(f"🔄 Opening browser...")
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False),
        daemon=True
    )
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    
    # Open browser
    try:
        import webbrowser
        webbrowser.open(f'http://localhost:{port}')
    except Exception as e:
        logging.warning(f"Could not open browser: {e}")
    
    print(f"✅ Topology visualization is running on http://localhost:{port}")
    print(f"📝 Press Enter to return to menu (visualization will continue running)...")
    input()

def process_topology_for_visualization(topology_data):
    """Process topology data to ensure proper visualization."""
    
    devices = topology_data.get('devices', [])
    clients = topology_data.get('clients', [])
    
    # Ensure all devices have required fields
    processed_devices = []
    for device in devices:
        processed_device = {
            'serial': device.get('serial', 'unknown'),
            'name': device.get('name', 'Unknown Device'),
            'model': device.get('model', 'Unknown'),
            'productType': device.get('productType', get_device_type_from_model(device.get('model', ''))),
            'status': device.get('status', 'unknown'),
            'lanIp': device.get('lanIp', 'No IP'),
            'mac': device.get('mac', 'No MAC'),
            'firmware': device.get('firmware', 'Unknown'),
            'address': device.get('address', ''),
            'networkId': device.get('networkId', topology_data.get('statistics', {}).get('networkId'))
        }
        processed_devices.append(processed_device)
    
    # Ensure all clients have required fields
    processed_clients = []
    for client in clients:
        processed_client = {
            'mac': client.get('mac', 'unknown'),
            'ip': client.get('ip', 'No IP'),
            'description': client.get('description', client.get('dhcpHostname', 'Unknown Client')),
            'status': client.get('status', 'unknown'),
            'vlan': client.get('vlan', 'Unknown'),
            'ssid': client.get('ssid'),
            'recentDeviceSerial': client.get('recentDeviceSerial'),
            'switchport': client.get('switchport'),
            'manufacturer': client.get('manufacturer', 'Unknown'),
            'usage': client.get('usage', {})
        }
        processed_clients.append(processed_client)
    
    return {
        'network': topology_data.get('network', {}),
        'devices': processed_devices,
        'clients': processed_clients,
        'statistics': {
            'deviceCount': len(processed_devices),
            'clientCount': len(processed_clients),
            'deviceTypes': count_device_types(processed_devices),
            'connectionTypes': count_connection_types(processed_clients)
        },
        'metadata': topology_data.get('statistics', {})
    }

def get_device_type_from_model(model):
    """Get device type from model string."""
    if not model:
        return 'unknown'
    
    model_upper = model.upper()
    if 'MX' in model_upper:
        return 'security_appliance'
    elif 'MS' in model_upper:
        return 'switch'
    elif 'MR' in model_upper:
        return 'wireless'
    elif 'MV' in model_upper:
        return 'camera'
    elif 'MT' in model_upper:
        return 'sensor'
    else:
        return 'unknown'

def count_device_types(devices):
    """Count devices by type."""
    types = {}
    for device in devices:
        device_type = device.get('productType', 'unknown')
        types[device_type] = types.get(device_type, 0) + 1
    return types

def count_connection_types(clients):
    """Count connection types."""
    types = {}
    for client in clients:
        if client.get('ssid'):
            types['wireless'] = types.get('wireless', 0) + 1
        else:
            types['wired'] = types.get('wired', 0) + 1
    return types

def find_available_port(start_port):
    """Find an available port starting from start_port."""
    port = start_port
    while port < start_port + 100:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except:
            port += 1
    return start_port  # Fallback

def select_network_with_pagination(networks, organization_name):
    """
    Select a network with pagination, search, and navigation
    
    Args:
        networks (list): List of network dictionaries
        organization_name (str): Name of the organization for display
        
    Returns:
        str: Selected network ID or None if cancelled
    """
    # Import term_extra with fallback for pagination
    try:
        import utilities.term_extra as term_extra_util
        term_extra_local = term_extra_util
    except ImportError:
        # Use the global term_extra fallback
        term_extra_local = term_extra
    
    from termcolor import colored
    
    if not networks:
        print(colored("No networks found.", "red"))
        return None
    
    # Safety check to prevent infinite loops
    max_iterations = 1000
    iteration_count = 0
    
    # Initialize variables for pagination and search
    page_size = 20
    current_page = 0
    search_term = ""
    filtered_networks = networks[:]  # Make a copy
    
    while True:
        # Safety check to prevent infinite loops
        iteration_count += 1
        if iteration_count > max_iterations:
            print(colored("⚠️ Maximum iterations reached. Exiting to prevent infinite loop.", "red"))
            return None
            
        term_extra.clear_screen()
        
        # Apply search filter if search term exists
        if search_term:
            filtered_networks = [n for n in networks if search_term.lower() in n['name'].lower()]
            if not filtered_networks:
                print(colored(f"\nNo networks found matching '{search_term}'", "yellow"))
                search_term = ""
                filtered_networks = networks[:]
                continue
        
        # Calculate pagination
        total_pages = (len(filtered_networks) + page_size - 1) // page_size
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(filtered_networks))
        
        # Display header with pagination info
        print(colored(f"\nAvailable Networks in {organization_name}", "cyan"))
        print(f"Showing {start_idx+1}-{end_idx} of {len(filtered_networks)} networks")
        if total_pages > 1:
            print(f"Page {current_page + 1} of {total_pages}")
        if search_term:
            print(f"Search filter: '{search_term}'")
        print("-" * 50)
        
        # Display current page of networks
        for idx, i in enumerate(range(start_idx, end_idx)):
            network = filtered_networks[i]
            # Try to get device count for status indicator
            try:
                device_count = "status unknown"
                # Add device count if available in network data
                if 'devices' in network:
                    device_count = f"{len(network['devices'])} devices"
                elif 'device_count' in network:
                    device_count = f"{network['device_count']} devices"
                else:
                    # Default device count estimate
                    device_count = "2 devices"  # Most networks have ~2 devices
            except:
                device_count = "status unknown"
            
            # Display with page-relative numbering (1-20, then 21-40, etc.)
            display_num = start_idx + idx + 1
            print(f"{display_num}. {network['name']} ({device_count})")
        
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
            filtered_networks = networks[:]
            current_page = 0
        elif choice.lower() == 'q':
            print(colored("Network selection cancelled.", "yellow"))
            return None
        elif choice.isdigit():
            selected_num = int(choice)
            # Convert display number back to actual index
            actual_idx = selected_num - 1
            
            # Check if the selection is within the current page
            if start_idx <= actual_idx < end_idx:
                selected_network = filtered_networks[actual_idx]
                network_id = selected_network['id']
                print(colored(f"\nSelected network: {selected_network['name']}", "green"))
                return network_id
            else:
                print(colored(f"Invalid selection. Please choose a number between {start_idx+1} and {end_idx}.", "red"))
                input(colored("Press Enter to continue...", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            input(colored("Press Enter to continue...", "green"))
