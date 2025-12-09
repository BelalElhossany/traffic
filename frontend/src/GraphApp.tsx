import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './GraphApp.css';

interface Node {
  id: string;
  name: string;
  type: 'intersection' | 'merge' | 'split';
  x: number;
  y: number;
  connected_segments: number;
  has_traffic_light?: boolean;
  traffic_light?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
}

interface Edge {
  id: string;
  name: string;
  type: 'road' | 'highway' | 'arterial';
  source: string;
  target: string;
  forward_flow: number;
  backward_flow: number;
  total_flow: number;
  capacity: number;
  utilization: number;
  congestion_level: 'green' | 'yellow' | 'red';
  police_control: boolean;
  has_traffic_light: boolean;
  length: number;
  speed_limit: number;
}

interface NetworkTopology {
  nodes: Node[];
  edges: Edge[];
  simulation_time: string;
  simulation_running: boolean;
}

interface SimulationStatus {
  simulation_running: boolean;
  simulation_time: string;
  total_nodes: number;
  total_segments: number;
  high_congestion: number;
  medium_congestion: number;
}

const GraphApp: React.FC = () => {
  const [topology, setTopology] = useState<NetworkTopology | null>(null);
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const svgRef = useRef<SVGSVGElement>(null);

  const API_BASE = 'https://work-1-prrnhxygajyxxmlp.prod-runtime.all-hands.dev/api/graph';

  const showMessage = (text: string) => {
    setMessage(text);
    setTimeout(() => setMessage(''), 3000);
  };

  const initializeNetwork = async () => {
    setLoading(true);
    try {
      const networkData = {
        nodes: [
          { id: 'intersection_1', name: 'Times Square', node_type: 'intersection', x: 300, y: 200 },
          { id: 'intersection_2', name: 'Herald Square', node_type: 'intersection', x: 500, y: 300 },
          { id: 'merge_1', name: 'Highway Merge', node_type: 'merge', x: 200, y: 400 },
          { id: 'split_1', name: 'Highway Split', node_type: 'split', x: 600, y: 150 },
          { id: 'intersection_3', name: 'Union Square', node_type: 'intersection', x: 400, y: 450 }
        ],
        segments: [
          {
            id: 'seg_1', name: 'Broadway N-S', segment_type: 'arterial',
            from_node: 'intersection_1', to_node: 'intersection_2',
            forward_capacity: 1800, backward_capacity: 1600, length: 800, speed_limit: 40
          },
          {
            id: 'seg_2', name: '7th Ave E-W', segment_type: 'road',
            from_node: 'intersection_1', to_node: 'split_1',
            forward_capacity: 1400, backward_capacity: 1200, length: 1200, speed_limit: 50
          },
          {
            id: 'seg_3', name: 'Highway Approach', segment_type: 'highway',
            from_node: 'merge_1', to_node: 'intersection_2',
            forward_capacity: 2200, backward_capacity: 2000, length: 1500, speed_limit: 80
          },
          {
            id: 'seg_4', name: 'Park Ave', segment_type: 'arterial',
            from_node: 'split_1', to_node: 'intersection_2',
            forward_capacity: 1600, backward_capacity: 1400, length: 900, speed_limit: 45
          },
          {
            id: 'seg_5', name: '14th Street', segment_type: 'road',
            from_node: 'intersection_2', to_node: 'intersection_3',
            forward_capacity: 1300, backward_capacity: 1100, length: 700, speed_limit: 35
          },
          {
            id: 'seg_6', name: 'FDR Drive', segment_type: 'highway',
            from_node: 'merge_1', to_node: 'intersection_3',
            forward_capacity: 2400, backward_capacity: 2200, length: 2000, speed_limit: 90
          }
        ]
      };

      const response = await fetch(`${API_BASE}/initialize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(networkData)
      });

      if (response.ok) {
        showMessage('Network initialized successfully!');
        await fetchTopology();
        await fetchStatus();
      } else {
        showMessage('Failed to initialize network');
      }
    } catch (error) {
      showMessage('Error initializing network');
      console.error(error);
    }
    setLoading(false);
  };

  const fetchTopology = async () => {
    try {
      const response = await fetch(`${API_BASE}/network-topology`);
      if (response.ok) {
        const data = await response.json();
        setTopology(data);
      }
    } catch (error) {
      console.error('Error fetching topology:', error);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const startSimulation = async () => {
    try {
      const response = await fetch(`${API_BASE}/start`, { method: 'POST' });
      if (response.ok) {
        showMessage('Simulation started!');
        await fetchStatus();
      }
    } catch (error) {
      showMessage('Error starting simulation');
    }
  };

  const stopSimulation = async () => {
    try {
      const response = await fetch(`${API_BASE}/stop`, { method: 'POST' });
      if (response.ok) {
        showMessage('Simulation stopped!');
        await fetchStatus();
      }
    } catch (error) {
      showMessage('Error stopping simulation');
    }
  };

  const adjustIntersectionGreenTime = async (nodeId: string, direction: string, greenTime: number) => {
    try {
      const response = await fetch(
        `${API_BASE}/adjust-intersection-green-time?node_id=${nodeId}&direction=${direction}&green_time=${greenTime}`,
        { method: 'POST' }
      );
      if (response.ok) {
        showMessage(`Green time adjusted for ${direction} at ${nodeId}`);
        await fetchTopology();
      }
    } catch (error) {
      showMessage('Error adjusting green time');
    }
  };

  const togglePoliceControl = async (segmentId: string, enabled: boolean) => {
    try {
      const response = await fetch(
        `${API_BASE}/toggle-police-control?segment_id=${segmentId}&enabled=${enabled}&reduction=0.3`,
        { method: 'POST' }
      );
      if (response.ok) {
        showMessage(`Police control ${enabled ? 'enabled' : 'disabled'} for ${segmentId}`);
        await fetchTopology();
      }
    } catch (error) {
      showMessage('Error toggling police control');
    }
  };

  const setTime = async (hour: number) => {
    const timeMinutes = hour * 60;
    try {
      const response = await fetch(`${API_BASE}/set-time?time_minutes=${timeMinutes}`, {
        method: 'POST'
      });
      if (response.ok) {
        showMessage(`Time set to ${hour}:00`);
        await fetchTopology();
        await fetchStatus();
      }
    } catch (error) {
      showMessage('Error setting time');
    }
  };

  // D3.js visualization
  useEffect(() => {
    if (!topology || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;
    
    svg.attr('width', width).attr('height', height);

    // Create arrow markers for directed edges
    const defs = svg.append('defs');
    
    ['green', 'yellow', 'red'].forEach(color => {
      defs.append('marker')
        .attr('id', `arrow-${color}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', color === 'green' ? '#28a745' : color === 'yellow' ? '#ffc107' : '#dc3545');
    });

    // Draw edges (segments)
    const edges = svg.selectAll('.edge')
      .data(topology.edges)
      .enter()
      .append('g')
      .attr('class', 'edge');

    edges.append('line')
      .attr('x1', d => {
        const sourceNode = topology.nodes.find(n => n.id === d.source);
        return sourceNode ? sourceNode.x : 0;
      })
      .attr('y1', d => {
        const sourceNode = topology.nodes.find(n => n.id === d.source);
        return sourceNode ? sourceNode.y : 0;
      })
      .attr('x2', d => {
        const targetNode = topology.nodes.find(n => n.id === d.target);
        return targetNode ? targetNode.x : 0;
      })
      .attr('y2', d => {
        const targetNode = topology.nodes.find(n => n.id === d.target);
        return targetNode ? targetNode.y : 0;
      })
      .attr('stroke', d => {
        switch (d.congestion_level) {
          case 'green': return '#28a745';
          case 'yellow': return '#ffc107';
          case 'red': return '#dc3545';
          default: return '#6c757d';
        }
      })
      .attr('stroke-width', d => Math.max(2, Math.min(8, d.utilization / 20)))
      .attr('marker-end', d => `url(#arrow-${d.congestion_level})`)
      .style('cursor', 'pointer')
      .on('click', (_, d) => {
        setSelectedEdge(d);
        setSelectedNode(null);
      });

    // Add edge labels
    edges.append('text')
      .attr('x', d => {
        const sourceNode = topology.nodes.find(n => n.id === d.source);
        const targetNode = topology.nodes.find(n => n.id === d.target);
        return sourceNode && targetNode ? (sourceNode.x + targetNode.x) / 2 : 0;
      })
      .attr('y', d => {
        const sourceNode = topology.nodes.find(n => n.id === d.source);
        const targetNode = topology.nodes.find(n => n.id === d.target);
        return sourceNode && targetNode ? (sourceNode.y + targetNode.y) / 2 - 10 : 0;
      })
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('fill', '#333')
      .text(d => `${Math.round(d.total_flow)} veh/hr`);

    // Draw nodes (intersections)
    const nodes = svg.selectAll('.node')
      .data(topology.nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.x}, ${d.y})`);

    nodes.append('circle')
      .attr('r', d => {
        switch (d.type) {
          case 'intersection': return 20;
          case 'merge': return 15;
          case 'split': return 15;
          default: return 12;
        }
      })
      .attr('fill', d => {
        switch (d.type) {
          case 'intersection': return '#007bff';
          case 'merge': return '#28a745';
          case 'split': return '#ffc107';
          default: return '#6c757d';
        }
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (_, d) => {
        setSelectedNode(d);
        setSelectedEdge(null);
      });

    // Add node labels
    nodes.append('text')
      .attr('y', -25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .text(d => d.name);

    // Add node type indicators
    nodes.append('text')
      .attr('y', 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('fill', '#666')
      .text(d => d.type.toUpperCase());

  }, [topology]);

  // Auto-refresh when simulation is running
  useEffect(() => {
    if (!status?.simulation_running) return;

    const interval = setInterval(() => {
      fetchTopology();
      fetchStatus();
    }, 3000);

    return () => clearInterval(interval);
  }, [status?.simulation_running]);

  return (
    <div className="graph-app">
      <div className="header">
        <h1>🚦 Graph-Based Traffic Network</h1>
        <p>Interactive traffic simulation with nodes and edges</p>
      </div>

      {message && <div className="message">{message}</div>}

      <div className="controls">
        <button onClick={initializeNetwork} disabled={loading}>
          Initialize Network
        </button>
        <button onClick={startSimulation} disabled={loading}>
          Start Simulation
        </button>
        <button onClick={stopSimulation} disabled={loading}>
          Stop Simulation
        </button>
      </div>

      {status && (
        <div className="status-bar">
          <span className={`status-indicator ${status.simulation_running ? 'running' : 'stopped'}`}>
            {status.simulation_running ? '🟢 RUNNING' : '🔴 STOPPED'}
          </span>
          <span>Time: {status.simulation_time}</span>
          <span>Nodes: {status.total_nodes}</span>
          <span>Segments: {status.total_segments}</span>
          <span className="congestion-high">🔴 High: {status.high_congestion}</span>
          <span className="congestion-medium">🟡 Medium: {status.medium_congestion}</span>
        </div>
      )}

      <div className="time-controls">
        <h3>Test Different Times:</h3>
        <div className="time-buttons">
          <button onClick={() => setTime(3)}>3 AM</button>
          <button onClick={() => setTime(8)}>8 AM</button>
          <button onClick={() => setTime(12)}>12 PM</button>
          <button onClick={() => setTime(18)}>6 PM</button>
          <button onClick={() => setTime(22)}>10 PM</button>
        </div>
      </div>

      <div className="main-content">
        <div className="visualization">
          <svg ref={svgRef}></svg>
        </div>

        <div className="control-panel">
          {selectedNode && (
            <div className="node-controls">
              <h3>🔵 {selectedNode.name}</h3>
              <p>Type: {selectedNode.type}</p>
              <p>Connected segments: {selectedNode.connected_segments}</p>
              
              {selectedNode.type === 'intersection' && selectedNode.has_traffic_light && (
                <div className="traffic-light-controls">
                  <h4>Traffic Light Control</h4>
                  {['north', 'south', 'east', 'west'].map(direction => (
                    <div key={direction} className="direction-control">
                      <label>{direction.toUpperCase()}: {selectedNode.traffic_light?.[direction as keyof typeof selectedNode.traffic_light] || 30}s</label>
                      <input
                        type="range"
                        min="10"
                        max="80"
                        value={selectedNode.traffic_light?.[direction as keyof typeof selectedNode.traffic_light] || 30}
                        onChange={(e) => adjustIntersectionGreenTime(selectedNode.id, direction, parseInt(e.target.value))}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {selectedEdge && (
            <div className="edge-controls">
              <h3>🛣️ {selectedEdge.name}</h3>
              <p>Type: {selectedEdge.type}</p>
              <p>Length: {selectedEdge.length}m</p>
              <p>Speed limit: {selectedEdge.speed_limit} km/h</p>
              
              <div className="flow-info">
                <div className={`congestion-badge ${selectedEdge.congestion_level}`}>
                  {selectedEdge.congestion_level.toUpperCase()}
                </div>
                <p>Forward flow: {Math.round(selectedEdge.forward_flow)} veh/hr</p>
                <p>Backward flow: {Math.round(selectedEdge.backward_flow)} veh/hr</p>
                <p>Total flow: {Math.round(selectedEdge.total_flow)} veh/hr</p>
                <p>Capacity: {selectedEdge.capacity} veh/hr</p>
                <p>Utilization: {selectedEdge.utilization.toFixed(1)}%</p>
              </div>

              <div className="segment-controls">
                <h4>Controls</h4>
                <div className="control-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedEdge.police_control}
                      onChange={(e) => togglePoliceControl(selectedEdge.id, e.target.checked)}
                    />
                    Police Control (30% reduction)
                  </label>
                </div>
                
                <button 
                  className="add-traffic-light-btn"
                  onClick={() => {
                    // Add traffic light functionality
                    showMessage('Traffic light functionality coming soon!');
                  }}
                >
                  {selectedEdge.has_traffic_light ? 'Adjust Traffic Light' : 'Add Traffic Light'}
                </button>
              </div>
            </div>
          )}

          {!selectedNode && !selectedEdge && (
            <div className="instructions">
              <h3>Instructions</h3>
              <p>🔵 Click on nodes (intersections, merges, splits) to control traffic lights</p>
              <p>🛣️ Click on edges (road segments) to add police control or traffic lights</p>
              <p>🎨 Colors indicate congestion: Green (smooth), Yellow (moderate), Red (heavy)</p>
              <p>⏰ Use time controls to see traffic patterns throughout the day</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GraphApp;