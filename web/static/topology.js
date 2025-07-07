
    let currentLayout = 'force';
    let simulation;
    let svg;
    let link;
    let node;
    let width, height; // Define globally
    
    fetch('/topology-data')
        .then(response => response.json())
        .then(data => {
            width = window.innerWidth - 250;
            height = window.innerHeight - 60;
            
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
            
            // Handle window resize
            window.addEventListener('resize', function() {
                width = window.innerWidth - 250;
                height = window.innerHeight - 60;
                svg.attr('width', width).attr('height', height);
                updateLayout();
            });
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
    