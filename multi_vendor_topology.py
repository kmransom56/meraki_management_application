#!/usr/bin/env python3
"""
Multi-Vendor Network Topology Engine
Combines Cisco Meraki and Fortinet devices into unified topology visualization
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class MultiVendorTopologyEngine:
    """Unified topology engine for multi-vendor network visualization"""
    
    def __init__(self, meraki_manager=None, fortinet_manager=None):
        self.meraki_manager = meraki_manager
        self.fortinet_manager = fortinet_manager
        self.topology_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def build_unified_topology(self, network_id: str = None, network_name: str = None) -> Dict:
        """Build unified topology combining Meraki and Fortinet devices"""
        try:
            unified_topology = {
                'network_id': network_id,
                'network_name': network_name or 'Multi-Vendor Network',
                'timestamp': datetime.now().isoformat(),
                'devices': [],
                'clients': [],
                'connections': [],
                'vendor_stats': {
                    'meraki': {'devices': 0, 'clients': 0},
                    'fortinet': {'devices': 0, 'clients': 0}
                }
            }
            
            # Get Meraki topology data
            if self.meraki_manager and network_id:
                meraki_data = self._get_meraki_topology_data(network_id)
                if meraki_data:
                    self._merge_meraki_data(unified_topology, meraki_data)
            
            # Get Fortinet topology data
            if self.fortinet_manager:
                fortinet_data = self._get_fortinet_topology_data()
                if fortinet_data:
                    self._merge_fortinet_data(unified_topology, fortinet_data)
            
            # Build inter-vendor connections
            self._build_cross_vendor_connections(unified_topology)
            
            # Calculate statistics
            self._calculate_topology_stats(unified_topology)
            
            logger.info(f"Built unified topology with {len(unified_topology['devices'])} devices and {len(unified_topology['clients'])} clients")
            return unified_topology
            
        except Exception as e:
            logger.error(f"Error building unified topology: {e}")
            return self._get_empty_topology(network_name)
    
    def _get_meraki_topology_data(self, network_id: str) -> Optional[Dict]:
        """Get topology data from Meraki network"""
        try:
            if not self.meraki_manager or not hasattr(self.meraki_manager, 'dashboard'):
                return None
                
            # Get Meraki devices
            devices = self.meraki_manager.dashboard.networks.getNetworkDevices(network_id)
            
            # Get Meraki clients
            clients = self.meraki_manager.dashboard.networks.getNetworkClients(
                network_id, timespan=86400
            )
            
            # Try to get topology links
            links = None
            try:
                links = self.meraki_manager.dashboard.networks.getNetworkTopologyLinkLayer(network_id)
            except:
                logger.info("Meraki topology links not available, will use device-client associations")
            
            return {
                'devices': devices or [],
                'clients': clients or [],
                'links': links or []
            }
            
        except Exception as e:
            logger.error(f"Error getting Meraki topology data: {e}")
            return None
    
    def _get_fortinet_topology_data(self) -> Optional[Dict]:
        """Get topology data from Fortinet devices"""
        try:
            if not self.fortinet_manager:
                return None
                
            return self.fortinet_manager.get_network_topology_data()
            
        except Exception as e:
            logger.error(f"Error getting Fortinet topology data: {e}")
            return None
    
    def _merge_meraki_data(self, unified_topology: Dict, meraki_data: Dict):
        """Merge Meraki devices and clients into unified topology"""
        try:
            # Process Meraki devices
            for device in meraki_data.get('devices', []):
                unified_device = {
                    'id': device.get('serial', device.get('mac')),
                    'name': device.get('name', 'Unknown Meraki Device'),
                    'serial': device.get('serial'),
                    'mac': device.get('mac'),
                    'type': self._get_meraki_device_type(device),
                    'vendor': 'meraki',
                    'model': device.get('model'),
                    'firmware': device.get('firmware'),
                    'lan_ip': device.get('lanIp'),
                    'wan1_ip': device.get('wan1Ip'),
                    'wan2_ip': device.get('wan2Ip'),
                    'status': device.get('status', 'unknown'),
                    'network_id': device.get('networkId'),
                    'tags': device.get('tags', []),
                    'notes': device.get('notes'),
                    'lat': device.get('lat'),
                    'lng': device.get('lng'),
                    'address': device.get('address'),
                    'details': device
                }
                unified_topology['devices'].append(unified_device)
                unified_topology['vendor_stats']['meraki']['devices'] += 1
            
            # Process Meraki clients
            for client in meraki_data.get('clients', []):
                unified_client = {
                    'id': client.get('mac'),
                    'mac': client.get('mac'),
                    'ip': client.get('ip'),
                    'ip6': client.get('ip6'),
                    'hostname': client.get('description') or client.get('dhcpHostname'),
                    'type': 'client',
                    'vendor': 'meraki_managed',
                    'manufacturer': client.get('manufacturer'),
                    'os': client.get('os'),
                    'status': client.get('status'),
                    'last_seen': client.get('lastSeen'),
                    'ssid': client.get('ssid'),
                    'vlan': client.get('vlan'),
                    'switch_port': client.get('switchport'),
                    'ap_mac': client.get('recentDeviceMac'),
                    'usage_sent': client.get('usage', {}).get('sent', 0),
                    'usage_recv': client.get('usage', {}).get('recv', 0),
                    'details': client
                }
                unified_topology['clients'].append(unified_client)
                unified_topology['vendor_stats']['meraki']['clients'] += 1
                
                # Create client-device connection
                if client.get('recentDeviceMac'):
                    connection = {
                        'source': client.get('mac'),
                        'target': client.get('recentDeviceMac'),
                        'type': 'client_connection',
                        'vendor': 'meraki',
                        'ssid': client.get('ssid'),
                        'vlan': client.get('vlan')
                    }
                    unified_topology['connections'].append(connection)
            
            # Process Meraki topology links if available
            for link in meraki_data.get('links', []):
                if link.get('nodes'):
                    for i in range(len(link['nodes']) - 1):
                        connection = {
                            'source': link['nodes'][i].get('serial'),
                            'target': link['nodes'][i + 1].get('serial'),
                            'type': 'network_link',
                            'vendor': 'meraki'
                        }
                        unified_topology['connections'].append(connection)
                        
        except Exception as e:
            logger.error(f"Error merging Meraki data: {e}")
    
    def _merge_fortinet_data(self, unified_topology: Dict, fortinet_data: Dict):
        """Merge Fortinet devices and clients into unified topology"""
        try:
            # Process Fortigate firewalls
            for fortigate in fortinet_data.get('fortigates', []):
                unified_device = {
                    'id': fortigate.get('id'),
                    'name': fortigate.get('name'),
                    'host': fortigate.get('host'),
                    'serial': fortigate.get('serial'),
                    'type': 'firewall',
                    'vendor': 'fortinet',
                    'model': fortigate.get('model'),
                    'version': fortigate.get('version'),
                    'hostname': fortigate.get('hostname'),
                    'status': fortigate.get('status'),
                    'uptime': fortigate.get('uptime'),
                    'cpu_usage': fortigate.get('cpu_usage'),
                    'memory_usage': fortigate.get('memory_usage'),
                    'details': fortigate
                }
                unified_topology['devices'].append(unified_device)
                unified_topology['vendor_stats']['fortinet']['devices'] += 1
            
            # Process FortiAP access points
            for fortiap in fortinet_data.get('fortiaps', []):
                unified_device = {
                    'id': fortiap.get('id'),
                    'name': fortiap.get('name'),
                    'serial': fortiap.get('serial'),
                    'mac': fortiap.get('mac'),
                    'type': 'access_point',
                    'vendor': 'fortinet',
                    'model': fortiap.get('model'),
                    'ip': fortiap.get('ip'),
                    'status': fortiap.get('status'),
                    'location': fortiap.get('location'),
                    'clients': fortiap.get('clients'),
                    'uptime': fortiap.get('uptime'),
                    'channel_2g': fortiap.get('channel_2g'),
                    'channel_5g': fortiap.get('channel_5g'),
                    'fortigate_id': fortiap.get('fortigate_id'),
                    'details': fortiap
                }
                unified_topology['devices'].append(unified_device)
                unified_topology['vendor_stats']['fortinet']['devices'] += 1
            
            # Process WiFi clients
            for client in fortinet_data.get('wifi_clients', []):
                unified_client = {
                    'id': client.get('id'),
                    'mac': client.get('mac'),
                    'ip': client.get('ip'),
                    'hostname': client.get('hostname'),
                    'type': 'wifi_client',
                    'vendor': 'fortinet_managed',
                    'ap_serial': client.get('ap_serial'),
                    'ssid': client.get('ssid'),
                    'signal': client.get('signal'),
                    'details': client
                }
                unified_topology['clients'].append(unified_client)
                unified_topology['vendor_stats']['fortinet']['clients'] += 1
            
            # Add Fortinet connections
            for connection in fortinet_data.get('connections', []):
                unified_topology['connections'].append(connection)
                
        except Exception as e:
            logger.error(f"Error merging Fortinet data: {e}")
    
    def _build_cross_vendor_connections(self, unified_topology: Dict):
        """Build connections between different vendor devices"""
        try:
            # Find potential connections based on IP subnets, VLANs, etc.
            meraki_devices = [d for d in unified_topology['devices'] if d['vendor'] == 'meraki']
            fortinet_devices = [d for d in unified_topology['devices'] if d['vendor'] == 'fortinet']
            
            # Look for devices on same subnet (simplified logic)
            for meraki_device in meraki_devices:
                meraki_ip = meraki_device.get('lan_ip') or meraki_device.get('wan1_ip')
                if not meraki_ip:
                    continue
                    
                for fortinet_device in fortinet_devices:
                    fortinet_ip = fortinet_device.get('ip')
                    if not fortinet_ip:
                        continue
                    
                    # Simple same-subnet check (first 3 octets)
                    if self._same_subnet(meraki_ip, fortinet_ip):
                        connection = {
                            'source': meraki_device['id'],
                            'target': fortinet_device['id'],
                            'type': 'cross_vendor',
                            'vendor': 'multi_vendor',
                            'subnet': self._get_subnet(meraki_ip)
                        }
                        unified_topology['connections'].append(connection)
                        
        except Exception as e:
            logger.error(f"Error building cross-vendor connections: {e}")
    
    def _get_meraki_device_type(self, device: Dict) -> str:
        """Determine Meraki device type from model"""
        model = device.get('model', '').upper()
        if model.startswith('MX'):
            return 'security_appliance'
        elif model.startswith('MS'):
            return 'switch'
        elif model.startswith('MR'):
            return 'access_point'
        elif model.startswith('MV'):
            return 'camera'
        elif model.startswith('MT'):
            return 'sensor'
        else:
            return 'unknown'
    
    def _same_subnet(self, ip1: str, ip2: str) -> bool:
        """Check if two IPs are in the same /24 subnet"""
        try:
            octets1 = ip1.split('.')[:3]
            octets2 = ip2.split('.')[:3]
            return octets1 == octets2
        except:
            return False
    
    def _get_subnet(self, ip: str) -> str:
        """Get subnet from IP address"""
        try:
            octets = ip.split('.')[:3]
            return '.'.join(octets) + '.0/24'
        except:
            return 'unknown'
    
    def _calculate_topology_stats(self, unified_topology: Dict):
        """Calculate topology statistics"""
        try:
            total_devices = len(unified_topology['devices'])
            total_clients = len(unified_topology['clients'])
            total_connections = len(unified_topology['connections'])
            
            # Device type breakdown
            device_types = {}
            for device in unified_topology['devices']:
                device_type = device.get('type', 'unknown')
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            unified_topology['stats'] = {
                'total_devices': total_devices,
                'total_clients': total_clients,
                'total_connections': total_connections,
                'device_types': device_types,
                'vendors': unified_topology['vendor_stats']
            }
            
        except Exception as e:
            logger.error(f"Error calculating topology stats: {e}")
    
    def _get_empty_topology(self, network_name: str = None) -> Dict:
        """Return empty topology structure"""
        return {
            'network_id': None,
            'network_name': network_name or 'Multi-Vendor Network',
            'timestamp': datetime.now().isoformat(),
            'devices': [],
            'clients': [],
            'connections': [],
            'vendor_stats': {
                'meraki': {'devices': 0, 'clients': 0},
                'fortinet': {'devices': 0, 'clients': 0}
            },
            'stats': {
                'total_devices': 0,
                'total_clients': 0,
                'total_connections': 0,
                'device_types': {},
                'vendors': {'meraki': {'devices': 0, 'clients': 0}, 'fortinet': {'devices': 0, 'clients': 0}}
            }
        }
    
    def generate_multi_vendor_html(self, topology_data: Dict, output_dir: str = "static") -> str:
        """Generate HTML visualization for multi-vendor topology"""
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate enhanced D3.js visualization with multi-vendor support
            html_content = self._generate_enhanced_html_template(topology_data)
            
            # Write HTML file
            output_path = os.path.join(output_dir, f"multi_vendor_topology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated multi-vendor topology HTML: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating multi-vendor HTML: {e}")
            return None
    
    def _generate_enhanced_html_template(self, topology_data: Dict) -> str:
        """Generate enhanced HTML template with multi-vendor visualization"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Vendor Network Topology - {topology_data.get('network_name', 'Network')}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .stats-container {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-width: 150px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .meraki {{ color: #00bceb; }}
        .fortinet {{ color: #ee3124; }}
        .multi-vendor {{ color: #ff9500; }}
        .topology-container {{ 
            width: 100%; 
            height: 600px; 
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: relative;
        }}
        .legend {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .device-node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .device-node:hover {{
            stroke-width: 3px;
            stroke: #333;
        }}
        .connection-line {{
            stroke-width: 2px;
            opacity: 0.7;
        }}
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Multi-Vendor Network Topology</h1>
        <h2>{topology_data.get('network_name', 'Network')}</h2>
        <p>Generated: {topology_data.get('timestamp', 'Unknown')}</p>
    </div>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-value">{topology_data.get('stats', {}).get('total_devices', 0)}</div>
            <div>Total Devices</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{topology_data.get('stats', {}).get('total_clients', 0)}</div>
            <div>Total Clients</div>
        </div>
        <div class="stat-card">
            <div class="stat-value meraki">{topology_data.get('vendor_stats', {}).get('meraki', {}).get('devices', 0)}</div>
            <div>Meraki Devices</div>
        </div>
        <div class="stat-card">
            <div class="stat-value fortinet">{topology_data.get('vendor_stats', {}).get('fortinet', {}).get('devices', 0)}</div>
            <div>Fortinet Devices</div>
        </div>
    </div>
    
    <div class="topology-container">
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color meraki" style="background-color: #00bceb;"></div>
                <span>Meraki</span>
            </div>
            <div class="legend-item">
                <div class="legend-color fortinet" style="background-color: #ee3124;"></div>
                <span>Fortinet</span>
            </div>
            <div class="legend-item">
                <div class="legend-color multi-vendor" style="background-color: #ff9500;"></div>
                <span>Cross-Vendor</span>
            </div>
        </div>
        <svg id="topology-svg" width="100%" height="100%"></svg>
    </div>
    
    <div class="tooltip" id="tooltip" style="display: none;"></div>
    
    <script>
        // Multi-vendor topology data
        const topologyData = {json.dumps(topology_data, indent=2)};
        
        console.log('Multi-vendor topology data:', topologyData);
        
        // Initialize D3.js visualization
        const svg = d3.select("#topology-svg");
        const width = 800;
        const height = 600;
        const tooltip = d3.select("#tooltip");
        
        // Clear any existing content
        svg.selectAll("*").remove();
        
        // Create main group for zoom/pan
        const g = svg.append("g");
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", function(event) {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Process topology data for D3.js
        const nodes = [];
        const links = [];
        
        // Add devices as nodes
        if (topologyData.devices) {{
            topologyData.devices.forEach(device => {{
                const vendorColor = device.vendor === 'meraki' ? '#00bceb' : 
                                  device.vendor === 'fortinet' ? '#ee3124' : '#666';
                
                nodes.push({{
                    id: device.id,
                    name: device.name,
                    type: device.type,
                    vendor: device.vendor,
                    model: device.model,
                    status: device.status,
                    color: vendorColor,
                    size: device.type === 'firewall' ? 20 : 
                          device.type === 'access_point' ? 15 : 
                          device.type === 'switch' ? 18 : 12
                }});
            }});
        }}
        
        // Add clients as smaller nodes
        if (topologyData.clients) {{
            topologyData.clients.forEach(client => {{
                nodes.push({{
                    id: client.id,
                    name: client.hostname || client.mac,
                    type: 'client',
                    vendor: client.vendor,
                    color: '#999',
                    size: 8
                }});
            }});
        }}
        
        // Add connections as links
        if (topologyData.connections) {{
            topologyData.connections.forEach(connection => {{
                const linkColor = connection.vendor === 'meraki' ? '#00bceb' : 
                                connection.vendor === 'fortinet' ? '#ee3124' : 
                                connection.vendor === 'multi_vendor' ? '#ff9500' : '#999';
                
                links.push({{
                    source: connection.source,
                    target: connection.target,
                    type: connection.type,
                    vendor: connection.vendor,
                    color: linkColor
                }});
            }});
        }}
        
        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size + 5));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", "connection-line")
            .attr("stroke", d => d.color)
            .attr("stroke-width", 2);
        
        // Create nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("class", "device-node")
            .attr("r", d => d.size)
            .attr("fill", d => d.color)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .on("mouseover", function(event, d) {{
                tooltip.style("display", "block")
                    .html(`<strong>${{d.name}}</strong><br/>
                           Type: ${{d.type}}<br/>
                           Vendor: ${{d.vendor}}<br/>
                           ${{d.model ? 'Model: ' + d.model + '<br/>' : ''}}
                           ${{d.status ? 'Status: ' + d.status : ''}}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            }})
            .on("mouseout", function() {{
                tooltip.style("display", "none");
            }})
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Add labels
        const label = g.append("g")
            .selectAll("text")
            .data(nodes)
            .enter().append("text")
            .text(d => d.name)
            .attr("font-size", "10px")
            .attr("text-anchor", "middle")
            .attr("dy", d => d.size + 15)
            .attr("fill", "#333");
        
        // Update positions on simulation tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Add initial zoom to fit content
        setTimeout(() => {{
            const bounds = g.node().getBBox();
            const fullWidth = width;
            const fullHeight = height;
            const widthScale = fullWidth / bounds.width;
            const heightScale = fullHeight / bounds.height;
            const scale = Math.min(widthScale, heightScale) * 0.8;
            const translate = [fullWidth / 2 - scale * (bounds.x + bounds.width / 2),
                             fullHeight / 2 - scale * (bounds.y + bounds.height / 2)];
            
            svg.transition().duration(1000)
                .call(zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
        }}, 1000);
        
    </script>
</body>
</html>
        """

# Global multi-vendor topology engine instance
multi_vendor_engine = MultiVendorTopologyEngine()
