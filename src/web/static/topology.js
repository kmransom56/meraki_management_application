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

        // Process devices
        if (this.data.devices) {
            this.data.devices.forEach(device => {
                this.nodes.push({
                    id: device.serial || device.mac || `device_${Math.random()}`,
                    name: device.name || 'Unknown Device',
                    type: 'device',
                    subtype: device.productType || 'unknown',
                    status: device.status || 'unknown',
                    model: device.model,
                    address: device.address,
                    networkId: device.networkId,
                    data: device
                });
            });
        }

        // Process clients
        if (this.data.clients) {
            this.data.clients.forEach(client => {
                this.nodes.push({
                    id: client.mac || client.id || `client_${Math.random()}`,
                    name: client.description || client.dhcpHostname || client.ip || 'Unknown Client',
                    type: 'client',
                    status: client.status || 'unknown',
                    ip: client.ip,
                    vlan: client.vlan,
                    connectedDevice: client.recentDeviceSerial,
                    data: client
                });

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

        // Process topology links if available
        if (this.data.topology && this.data.topology.links) {
            this.data.topology.links.forEach(link => {
                this.links.push({
                    source: link.source,
                    target: link.target,
                    type: link.type || 'network_link'
                });
            });
        }

        console.log(`Processed ${this.nodes.length} nodes and ${this.links.length} links`);
    }

    renderTopology() {
        if (!this.nodes.length) {
            this.showError('No devices found in the network data');
            return;
        }

        // Clear existing elements
        this.svg.select('.main-group').selectAll('*').remove();

        const g = this.svg.select('.main-group');

        // Create simulation
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(30));

        // Create links
        const link = g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke-width', 2);

        // Create nodes
        const node = g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.nodes)
            .enter().append('g')
            .attr('class', 'node-group')
            .call(this.drag());

        // Add circles for nodes
        node.append('circle')
            .attr('class', d => `node ${d.type} ${d.subtype}`)
            .attr('r', d => d.type === 'device' ? 12 : 8)
            .on('click', (event, d) => this.selectNode(d))
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip());

        // Add labels
        node.append('text')
            .attr('class', 'node-label')
            .attr('dy', -15)
            .text(d => d.name.length > 15 ? d.name.substring(0, 15) + '...' : d.name);

        // Update simulation
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
        
        let html = `
            <div class="device-info">
                <h4>${node.name}</h4>
                <div class="device-property">
                    <span class="label">Type:</span>
                    <span class="value">${node.type}</span>
                </div>
                <div class="device-property">
                    <span class="label">Status:</span>
                    <span class="value">${node.status}</span>
                </div>
        `;

        if (node.type === 'device') {
            html += `
                <div class="device-property">
                    <span class="label">Model:</span>
                    <span class="value">${node.model || 'Unknown'}</span>
                </div>
                <div class="device-property">
                    <span class="label">Serial:</span>
                    <span class="value">${node.id}</span>
                </div>
                <div class="device-property">
                    <span class="label">Product Type:</span>
                    <span class="value">${node.subtype}</span>
                </div>
            `;
            if (node.address) {
                html += `
                    <div class="device-property">
                        <span class="label">Address:</span>
                        <span class="value">${node.address}</span>
                    </div>
                `;
            }
        } else if (node.type === 'client') {
            html += `
                <div class="device-property">
                    <span class="label">MAC:</span>
                    <span class="value">${node.id}</span>
                </div>
            `;
            if (node.ip) {
                html += `
                    <div class="device-property">
                        <span class="label">IP Address:</span>
                        <span class="value">${node.ip}</span>
                    </div>
                `;
            }
            if (node.vlan) {
                html += `
                    <div class="device-property">
                        <span class="label">VLAN:</span>
                        <span class="value">${node.vlan}</span>
                    </div>
                `;
            }
            if (node.connectedDevice) {
                html += `
                    <div class="device-property">
                        <span class="label">Connected to:</span>
                        <span class="value">${node.connectedDevice}</span>
                    </div>
                `;
            }
        }

        html += '</div>';
        detailsDiv.innerHTML = html;
    }

    showTooltip(event, node) {
        const tooltip = document.getElementById('tooltip');
        
        let content = `<h4>${node.name}</h4>`;
        content += `<p><strong>Type:</strong> ${node.type}</p>`;
        content += `<p><strong>Status:</strong> ${node.status}</p>`;
        
        if (node.type === 'device' && node.model) {
            content += `<p><strong>Model:</strong> ${node.model}</p>`;
        }
        if (node.ip) {
            content += `<p><strong>IP:</strong> ${node.ip}</p>`;
        }

        tooltip.innerHTML = content;
        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY - 10) + 'px';
        tooltip.classList.add('visible');
    }

    hideTooltip() {
        document.getElementById('tooltip').classList.remove('visible');
    }

    updateStatistics() {
        if (!this.data || !this.data.statistics) return;

        const stats = this.data.statistics;
        
        // Update device stats
        const deviceStatsDiv = document.getElementById('device-stats');
        let deviceStatsHTML = '';
        for (const [type, count] of Object.entries(stats.deviceTypes || {})) {
            deviceStatsHTML += `
                <div class="stat-item">
                    <span class="stat-label">${type}:</span>
                    <span class="stat-value">${count}</span>
                </div>
            `;
        }
        deviceStatsDiv.innerHTML = deviceStatsHTML;

        // Update connection stats
        const connectionStatsDiv = document.getElementById('connection-stats');
        let connectionStatsHTML = '';
        for (const [type, count] of Object.entries(stats.connectionTypes || {})) {
            connectionStatsHTML += `
                <div class="stat-item">
                    <span class="stat-label">${type}:</span>
                    <span class="stat-value">${count}</span>
                </div>
            `;
        }
        connectionStatsDiv.innerHTML = connectionStatsHTML;

        // Update performance stats
        document.getElementById('active-connections').textContent = stats.activeConnections || 0;
        document.getElementById('total-devices').textContent = stats.totalDevices || 0;
    }

    updateNetworkInfo() {
        if (!this.data) return;

        const networkName = this.data.network?.name || this.data.metadata?.networkName || 'Unknown Network';
        const lastUpdated = new Date().toLocaleTimeString();

        document.getElementById('network-name').textContent = networkName;
        document.getElementById('last-updated').textContent = `Updated: ${lastUpdated}`;
    }

    searchDevices() {
        const searchTerm = document.getElementById('device-search').value.toLowerCase();
        if (!searchTerm) {
            this.svg.selectAll('.node').style('opacity', 1);
            return;
        }

        this.svg.selectAll('.node')
            .style('opacity', d => {
                const nameMatch = d.name.toLowerCase().includes(searchTerm);
                const idMatch = d.id.toLowerCase().includes(searchTerm);
                return nameMatch || idMatch ? 1 : 0.2;
            });
    }

    filterNodes() {
        const filter = document.getElementById('device-filter').value;
        
        this.svg.selectAll('.node')
            .style('opacity', d => {
                if (filter === 'all') return 1;
                return (d.type === 'device' && d.subtype === filter) || 
                       (d.type === filter) ? 1 : 0.2;
            });
    }

    changeLayout() {
        const layout = document.getElementById('layout-select').value;
        
        if (!this.simulation) return;

        // Stop current simulation
        this.simulation.stop();

        switch (layout) {
            case 'hierarchical':
                this.applyHierarchicalLayout();
                break;
            case 'circular':
                this.applyCircularLayout();
                break;
            default:
                this.applyForceLayout();
        }
    }

    applyForceLayout() {
        this.simulation
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .alpha(1)
            .restart();
    }

    applyHierarchicalLayout() {
        // Simple hierarchical layout - devices at top, clients below
        const devices = this.nodes.filter(n => n.type === 'device');
        const clients = this.nodes.filter(n => n.type === 'client');

        devices.forEach((d, i) => {
            d.fx = (this.width / (devices.length + 1)) * (i + 1);
            d.fy = this.height * 0.3;
        });

        clients.forEach((d, i) => {
            d.fx = (this.width / (clients.length + 1)) * (i + 1);
            d.fy = this.height * 0.7;
        });

        this.simulation.alpha(1).restart();
    }

    applyCircularLayout() {
        const radius = Math.min(this.width, this.height) * 0.3;
        const centerX = this.width / 2;
        const centerY = this.height / 2;

        this.nodes.forEach((d, i) => {
            const angle = (2 * Math.PI * i) / this.nodes.length;
            d.fx = centerX + radius * Math.cos(angle);
            d.fy = centerY + radius * Math.sin(angle);
        });

        this.simulation.alpha(1).restart();
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
                .alpha(1)
                .restart();
        }
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-panel').style.display = 'flex';
    }

    hideError() {
        document.getElementById('error-panel').style.display = 'none';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NetworkTopology();
});
