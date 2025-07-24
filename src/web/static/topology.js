// Enhanced JavaScript for Network Topology Visualization
class NetworkTopology {
    constructor() {
        this.data = null;
        this.svg = null;
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        this.width = 0;
        this.height = 0;
        this.selectedNode = null;
        this.deviceIcons = new DeviceIcons();
        
        this.init();
    }

    init() {
        this.setupSVG();
        this.setupEventListeners();
        this.loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(() => this.loadData(), 30000);
    }

    setupSVG() {
        const container = document.getElementById('topology-container');
        const rect = container.getBoundingClientRect();
        this.width = rect.width;
        this.height = rect.height;

        this.svg = d3.select('#topology-svg')
            .attr('width', this.width)
            .attr('height', this.height);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                this.svg.select('.main-group')
                    .attr('transform', event.transform);
            });

        this.svg.call(zoom);

        // Create main group for zooming
        this.svg.append('g').attr('class', 'main-group');
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('search-btn').addEventListener('click', () => {
            this.searchDevices();
        });

        document.getElementById('device-search').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchDevices();
            }
        });

        // Filter functionality
        document.getElementById('device-filter').addEventListener('change', () => {
            this.filterNodes();
        });

        // Layout change
        document.getElementById('layout-select').addEventListener('change', () => {
            this.changeLayout();
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadData();
        });

        // Error panel close
        document.getElementById('close-error').addEventListener('click', () => {
            this.hideError();
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.resize();
        });
    }

    async loadData() {
        try {
            this.showLoading();
            console.log('Loading topology data...');
            
            const response = await fetch('/topology-data');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.data = await response.json();
            console.log('Data loaded:', this.data);
            
            if (this.data.error) {
                throw new Error(this.data.error);
            }
            
            this.processData();
            this.updateStatistics();
            this.updateNetworkInfo();
            this.renderTopology();
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError(`Failed to load network data: ${error.message}`);
            this.hideLoading();
        }
    }

    processData() {
        if (!this.data) return;

        this.nodes = [];
        this.links = [];

        // Process devices with enhanced icons and information
        if (this.data.devices) {
            this.data.devices.forEach((device, index) => {
                const node = this.deviceIcons.createDeviceNode(
                    device,
                    this.width / 2 + Math.cos(index * 0.5) * 200,
                    this.height / 2 + Math.sin(index * 0.5) * 200
                );
                this.nodes.push(node);
            });
        }

        // Process clients with enhanced icons
        if (this.data.clients) {
            this.data.clients.forEach((client, index) => {
                const node = this.deviceIcons.createClientNode(
                    client,
                    this.width / 2 + Math.cos(index * 0.3) * 300,
                    this.height / 2 + Math.sin(index * 0.3) * 300
                );
                this.nodes.push(node);

                // Create link to connected device
                if (client.recentDeviceSerial) {
                    this.links.push({
                        source: client.mac || client.id,
                        target: client.recentDeviceSerial,
                        type: 'client_connection'
                    });
                }
            });
        }

        // Create automatic device-to-device links based on network topology
        this.createDeviceLinks();

        console.log(`Processed ${this.nodes.length} nodes and ${this.links.length} links`);
    }

    createDeviceLinks() {
        // Create logical connections between devices based on their types
        const devices = this.nodes.filter(n => n.type === 'device');
        const securityAppliances = devices.filter(d => d.productType === 'security_appliance');
        const switches = devices.filter(d => d.productType === 'switch');
        const accessPoints = devices.filter(d => d.productType === 'wireless');
        
        // Connect security appliances to switches
        securityAppliances.forEach(sa => {
            switches.forEach(sw => {
                this.links.push({
                    source: sa.id,
                    target: sw.id,
                    type: 'network_backbone'
                });
            });
        });
        
        // Connect switches to access points
        switches.forEach(sw => {
            accessPoints.forEach(ap => {
                this.links.push({
                    source: sw.id,
                    target: ap.id,
                    type: 'network_distribution'
                });
            });
        });
    }

    renderTopology() {
        if (!this.nodes.length) {
            this.showError('No devices found in the network data');
            return;
        }

        // Clear existing elements
        this.svg.select('.main-group').selectAll('*').remove();

        const g = this.svg.select('.main-group');

        // Create simulation with enhanced forces
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(d => {
                // Shorter distances for client connections, longer for backbone
                return d.type === 'client_connection' ? 80 : 150;
            }))
            .force('charge', d3.forceManyBody().strength(d => {
                // Different repulsion for different node types
                return d.type === 'device' ? -400 : -200;
            }))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(d => {
                return d.type === 'device' ? 40 : 25;
            }));

        // Create enhanced links with different styles
        const link = g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.links)
            .enter().append('line')
            .attr('class', d => `link ${d.type}`)
            .attr('stroke-width', d => {
                switch(d.type) {
                    case 'network_backbone': return 4;
                    case 'network_distribution': return 3;
                    case 'client_connection': return 2;
                    default: return 2;
                }
            })
            .attr('stroke', d => {
                switch(d.type) {
                    case 'network_backbone': return '#dc3545';
                    case 'network_distribution': return '#007bff';
                    case 'client_connection': return '#28a745';
                    default: return '#6c757d';
                }
            })
            .attr('stroke-dasharray', d => {
                return d.type === 'client_connection' ? '5,5' : 'none';
            });

        // Create enhanced nodes with icons
        const node = g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.nodes)
            .enter().append('g')
            .attr('class', 'node-group')
            .call(this.drag());

        // Add background circles for better visibility
        node.append('circle')
            .attr('class', 'node-background')
            .attr('r', d => d.type === 'device' ? 18 : 14)
            .attr('fill', '#ffffff')
            .attr('stroke', d => d.color)
            .attr('stroke-width', 3);

        // Add main node circles with colors
        node.append('circle')
            .attr('class', d => `node ${d.type} ${d.productType}`)
            .attr('r', d => d.type === 'device' ? 15 : 12)
            .attr('fill', d => d.color)
            .attr('opacity', 0.9)
            .on('click', (event, d) => this.selectNode(d))
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip());

        // Add device icons using text with emojis
        node.append('text')
            .attr('class', 'node-icon')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'central')
            .attr('font-size', d => d.type === 'device' ? '16px' : '14px')
            .text(d => d.icon)
            .style('user-select', 'none')
            .style('pointer-events', 'none');

        // Add status indicators
        node.append('circle')
            .attr('class', 'status-indicator')
            .attr('r', 4)
            .attr('cx', 12)
            .attr('cy', -12)
            .attr('fill', d => {
                switch(d.status?.toLowerCase()) {
                    case 'online': return '#28a745';
                    case 'offline': return '#dc3545';
                    case 'alerting': return '#ffc107';
                    default: return '#6c757d';
                }
            })
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 1);

        // Add labels with better positioning
        node.append('text')
            .attr('class', 'node-label')
            .attr('dy', d => d.type === 'device' ? 28 : 22)
            .attr('text-anchor', 'middle')
            .text(d => {
                const maxLength = 12;
                return d.name.length > maxLength ? d.name.substring(0, maxLength) + '...' : d.name;
            })
            .style('font-size', '10px')
            .style('font-weight', 'bold')
            .style('fill', '#333');

        // Update simulation with enhanced animations
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }

    drag() {
        return d3.drag()
            .on('start', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }

    selectNode(node) {
        // Clear previous selection
        this.svg.selectAll('.node').classed('selected', false);
        
        // Select new node
        this.svg.selectAll('.node')
            .filter(d => d.id === node.id)
            .classed('selected', true);

        this.selectedNode = node;
        this.showDeviceDetails(node);
    }

    showDeviceDetails(node) {
        const detailsDiv = document.getElementById('device-details');
        
        // Get detailed information using DeviceIcons helper
        const details = node.type === 'device' 
            ? this.deviceIcons.getDetailedDeviceInfo(node.data)
            : this.deviceIcons.getDetailedClientInfo(node.data);
        
        let html = `
            <div class="device-info">
                <div class="device-header">
                    <span class="device-icon">${node.icon}</span>
                    <h4>${node.name}</h4>
                    <span class="status-badge status-${node.status?.toLowerCase()}">${node.status}</span>
                </div>
                
                <div class="device-details-grid">
        `;
        
        // Add all detail properties
        Object.entries(details).forEach(([key, value]) => {
            html += `
                <div class="detail-row">
                    <span class="detail-label">${key}:</span>
                    <span class="detail-value">${value}</span>
                </div>
            `;
        });
        
        html += `
                </div>
                
                <div class="device-actions">
                    <button class="btn btn-sm" onclick="topology.pingDevice('${node.id}')">
                        📡 Ping
                    </button>
                    <button class="btn btn-sm" onclick="topology.getDeviceClients('${node.id}')">
                        👥 Clients
                    </button>
                    <button class="btn btn-sm" onclick="topology.refreshDevice('${node.id}')">
                        🔄 Refresh
                    </button>
                </div>
            </div>
        `;
        
        detailsDiv.innerHTML = html;
    }

    // Helper methods for device actions
    pingDevice(deviceId) {
        console.log(`Pinging device: ${deviceId}`);
        alert(`Ping functionality for device ${deviceId} - Coming soon!`);
    }
    
    getDeviceClients(deviceId) {
        const node = this.nodes.find(n => n.id === deviceId);
        if (node && node.data.connectedClients) {
            console.log(`Device ${deviceId} has ${node.data.connectedClients.length} connected clients`);
            this.highlightConnectedClients(deviceId);
        } else {
            console.log(`No client information available for device ${deviceId}`);
        }
    }
    
    highlightConnectedClients(deviceId) {
        // Reset all node highlights
        this.svg.selectAll('.node').classed('highlighted', false);
        
        // Highlight the device and its connected clients
        this.svg.selectAll('.node')
            .filter(d => d.id === deviceId || 
                (d.type === 'client' && d.data.recentDeviceSerial === deviceId))
            .classed('highlighted', true);
    }
    
    refreshDevice(deviceId) {
        console.log(`Refreshing device: ${deviceId}`);
        this.loadData(); // For now, just reload all data
    }

    showTooltip(event, node) {
        const tooltip = document.getElementById('tooltip');
        const statusColor = this.deviceIcons.getDeviceColor(node.data);
        
        tooltip.innerHTML = `
            <div class="tooltip-header">
                <span class="tooltip-icon">${node.icon}</span>
                <strong>${node.name}</strong>
            </div>
            <div class="tooltip-content">
                <div>Type: ${node.type === 'device' ? node.productType : 'Client'}</div>
                <div>Status: <span style="color: ${statusColor}">${node.status}</span></div>
                ${node.type === 'device' ? `<div>Model: ${node.model}</div>` : ''}
                ${node.type === 'client' ? `<div>IP: ${node.data.ip || 'N/A'}</div>` : ''}
            </div>
        `;
        
        tooltip.style.display = 'block';
        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY - 10) + 'px';
    }

    hideTooltip() {
        document.getElementById('tooltip').style.display = 'none';
    }

    searchDevices() {
        const searchTerm = document.getElementById('device-search').value.toLowerCase();
        
        if (!searchTerm) {
            this.svg.selectAll('.node').classed('search-highlight', false);
            return;
        }
        
        this.svg.selectAll('.node').classed('search-highlight', false);
        
        const matchingNodes = this.nodes.filter(node => 
            node.name.toLowerCase().includes(searchTerm) ||
            node.productType?.toLowerCase().includes(searchTerm) ||
            node.model?.toLowerCase().includes(searchTerm)
        );
        
        this.svg.selectAll('.node')
            .filter(d => matchingNodes.includes(d))
            .classed('search-highlight', true);
        
        console.log(`Found ${matchingNodes.length} matching devices`);
    }

    filterNodes() {
        const filterValue = document.getElementById('device-filter').value;
        
        if (filterValue === 'all') {
            this.svg.selectAll('.node-group').style('display', 'block');
            return;
        }
        
        this.svg.selectAll('.node-group')
            .style('display', d => {
                return d.productType === filterValue ? 'block' : 'none';
            });
    }

    changeLayout() {
        const layoutType = document.getElementById('layout-select').value;
        
        switch(layoutType) {
            case 'hierarchical':
                this.applyHierarchicalLayout();
                break;
            case 'circular':
                this.applyCircularLayout();
                break;
            case 'force':
            default:
                this.applyForceLayout();
                break;
        }
    }
    
    applyHierarchicalLayout() {
        const layers = {
            'security_appliance': 0,
            'switch': 1,
            'wireless': 2,
            'camera': 3,
            'client': 4
        };
        
        this.nodes.forEach((node, index) => {
            const layer = layers[node.productType] || layers[node.type] || 4;
            node.fx = (index % 3) * 200 + 200;
            node.fy = layer * 100 + 100;
        });
        
        this.simulation.alpha(0.3).restart();
    }
    
    applyCircularLayout() {
        const devices = this.nodes.filter(n => n.type === 'device');
        const clients = this.nodes.filter(n => n.type === 'client');
        
        devices.forEach((node, index) => {
            const angle = (index / devices.length) * 2 * Math.PI;
            node.fx = this.width / 2 + Math.cos(angle) * 150;
            node.fy = this.height / 2 + Math.sin(angle) * 150;
        });
        
        clients.forEach((node, index) => {
            const angle = (index / clients.length) * 2 * Math.PI;
            node.fx = this.width / 2 + Math.cos(angle) * 300;
            node.fy = this.height / 2 + Math.sin(angle) * 300;
        });
        
        this.simulation.alpha(0.3).restart();
    }
    
    applyForceLayout() {
        this.nodes.forEach(node => {
            node.fx = null;
            node.fy = null;
        });
        
        this.simulation.alpha(0.3).restart();
    }

    updateStatistics() {
        if (!this.data || !this.data.statistics) return;
        
        const stats = this.data.statistics;
        
        const deviceStatsDiv = document.getElementById('device-stats');
        let deviceStatsHtml = '';
        Object.entries(stats.deviceTypes).forEach(([type, count]) => {
            deviceStatsHtml += `
                <div class="stat-item">
                    <span class="stat-label">${type}:</span>
                    <span class="stat-value">${count}</span>
                </div>
            `;
        });
        deviceStatsDiv.innerHTML = deviceStatsHtml;
        
        const connectionStatsDiv = document.getElementById('connection-stats');
        let connectionStatsHtml = '';
        Object.entries(stats.connectionTypes).forEach(([type, count]) => {
            connectionStatsHtml += `
                <div class="stat-item">
                    <span class="stat-label">${type}:</span>
                    <span class="stat-value">${count}</span>
                </div>
            `;
        });
        connectionStatsDiv.innerHTML = connectionStatsHtml;
        
        document.getElementById('active-connections').textContent = stats.activeConnections;
        document.getElementById('total-devices').textContent = stats.totalDevices;
    }

    updateNetworkInfo() {
        if (!this.data || !this.data.metadata) return;
        
        const metadata = this.data.metadata;
        document.getElementById('network-name').textContent = 
            metadata.networkName || 'Unknown Network';
        
        if (metadata.lastUpdated) {
            document.getElementById('last-updated').textContent = 
                `Last updated: ${new Date(metadata.lastUpdated).toLocaleString()}`;
        }
    }

    showLoading() {
        document.getElementById('loading').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-panel').style.display = 'block';
    }

    hideError() {
        document.getElementById('error-panel').style.display = 'none';
    }

    resize() {
        const container = document.getElementById('topology-container');
        const rect = container.getBoundingClientRect();
        this.width = rect.width;
        this.height = rect.height;
        
        this.svg
            .attr('width', this.width)
            .attr('height', this.height);
        
        if (this.simulation) {
            this.simulation
                .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                .alpha(0.3)
                .restart();
        }
    }
}

// Initialize the topology when the page loads
let topology;
document.addEventListener('DOMContentLoaded', () => {
    topology = new NetworkTopology();
});
