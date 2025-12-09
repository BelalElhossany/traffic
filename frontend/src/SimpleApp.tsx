import React, { useState, useEffect } from 'react';
import './SimpleApp.css';

interface Segment {
  name: string;
  current_flow: number;
  capacity: number;
  utilization_percent: number;
  congestion_level: string;
  current_queue: number;
  green_time: number;
  paired_segment?: string;
}

interface Status {
  simulation_running: boolean;
  simulation_time: string;
  total_segments: number;
  high_congestion: number;
  medium_congestion: number;
  segments: { [key: string]: Segment };
}

const API_BASE = 'https://work-1-prrnhxygajyxxmlp.prod-runtime.all-hands.dev/api/simple';

const SimpleApp: React.FC = () => {
  const [status, setStatus] = useState<Status | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Initialize network with realistic NYC intersections
  const initializeNetwork = async () => {
    setLoading(true);
    setMessage('Initializing traffic network...');
    
    const segments = [
      {
        id: 'times_square_ns',
        name: 'Times Square (N-S)',
        capacity: 1800,
        current_flow: 600,
        green_time: 45,
        segment_type: 'intersection',
        paired_segment: 'times_square_ew'
      },
      {
        id: 'times_square_ew',
        name: 'Times Square (E-W)',
        capacity: 1600,
        current_flow: 500,
        green_time: 75,
        segment_type: 'intersection',
        paired_segment: 'times_square_ns'
      },
      {
        id: 'herald_square_ns',
        name: 'Herald Square (N-S)',
        capacity: 1500,
        current_flow: 450,
        green_time: 50,
        segment_type: 'intersection',
        paired_segment: 'herald_square_ew'
      },
      {
        id: 'herald_square_ew',
        name: 'Herald Square (E-W)',
        capacity: 1400,
        current_flow: 400,
        green_time: 70,
        segment_type: 'intersection',
        paired_segment: 'herald_square_ns'
      },
      {
        id: 'broadway_main',
        name: 'Broadway Main',
        capacity: 1200,
        current_flow: 350,
        green_time: 60,
        segment_type: 'road'
      },
      {
        id: 'lincoln_tunnel',
        name: 'Lincoln Tunnel Approach',
        capacity: 2000,
        current_flow: 800,
        green_time: 45,
        segment_type: 'road'
      }
    ];

    try {
      const response = await fetch(`${API_BASE}/initialize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(segments)
      });
      
      if (response.ok) {
        setMessage('Network initialized successfully!');
        await fetchStatus();
      } else {
        setMessage('Failed to initialize network');
      }
    } catch (error) {
      setMessage('Error initializing network');
      console.error(error);
    }
    
    setLoading(false);
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
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/start`, { method: 'POST' });
      if (response.ok) {
        setMessage('Simulation started!');
        await fetchStatus();
      }
    } catch (error) {
      setMessage('Error starting simulation');
    }
    setLoading(false);
  };

  const stopSimulation = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/stop`, { method: 'POST' });
      if (response.ok) {
        setMessage('Simulation stopped!');
        await fetchStatus();
      }
    } catch (error) {
      setMessage('Error stopping simulation');
    }
    setLoading(false);
  };

  const adjustGreenTime = async (segmentId: string, newTime: number) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/adjust-green-time?segment_id=${segmentId}&green_time=${newTime}`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setStatus(data.new_status);
        setMessage(`Green time adjusted for ${segmentId}`);
      }
    } catch (error) {
      setMessage('Error adjusting green time');
    }
    setLoading(false);
  };

  const setTime = async (hour: number) => {
    const timeMinutes = hour * 60;
    try {
      const response = await fetch(`${API_BASE}/set-time?time_minutes=${timeMinutes}`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setStatus(data.new_status);
        setMessage(`Time set to ${hour}:00`);
      }
    } catch (error) {
      setMessage('Error setting time');
    }
  };

  // Auto-refresh status every 3 seconds when simulation is running
  useEffect(() => {
    const interval = setInterval(() => {
      if (status?.simulation_running) {
        fetchStatus();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [status?.simulation_running]);

  const getColorClass = (level: string) => {
    switch (level) {
      case 'red': return 'congestion-red';
      case 'yellow': return 'congestion-yellow';
      case 'green': return 'congestion-green';
      default: return 'congestion-gray';
    }
  };

  return (
    <div className="simple-app">
      <header className="app-header">
        <h1>🚦 NYC Traffic Simulation</h1>
        <p>Realistic intersection control with immediate consequences</p>
      </header>

      <div className="controls">
        <button onClick={initializeNetwork} disabled={loading}>
          Initialize Network
        </button>
        <button onClick={startSimulation} disabled={loading || !status}>
          Start Simulation
        </button>
        <button onClick={stopSimulation} disabled={loading || !status}>
          Stop Simulation
        </button>
      </div>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      {status && (
        <div className="status-panel">
          <div className="status-header">
            <h2>Traffic Status - {status.simulation_time}</h2>
            <div className="status-indicators">
              <span className={`status-dot ${status.simulation_running ? 'running' : 'stopped'}`}>
                {status.simulation_running ? '🟢 RUNNING' : '🔴 STOPPED'}
              </span>
              <span>🚗 {status.high_congestion} High Congestion</span>
              <span>⚠️ {status.medium_congestion} Medium Congestion</span>
            </div>
          </div>

          <div className="time-controls">
            <h3>Test Different Times:</h3>
            <div className="time-buttons">
              <button onClick={() => setTime(3)}>3 AM (Night)</button>
              <button onClick={() => setTime(8)}>8 AM (Rush)</button>
              <button onClick={() => setTime(12)}>12 PM (Lunch)</button>
              <button onClick={() => setTime(18)}>6 PM (Rush)</button>
              <button onClick={() => setTime(22)}>10 PM (Evening)</button>
            </div>
          </div>

          <div className="segments-grid">
            {Object.entries(status.segments).map(([id, segment]) => (
              <div key={id} className={`segment-card ${getColorClass(segment.congestion_level)}`}>
                <div className="segment-header">
                  <h3>{segment.name}</h3>
                  <div className={`congestion-badge ${segment.congestion_level}`}>
                    {segment.congestion_level.toUpperCase()}
                  </div>
                </div>
                
                <div className="segment-stats">
                  <div className="stat">
                    <span className="label">Flow:</span>
                    <span className="value">{segment.current_flow} veh/hr</span>
                  </div>
                  <div className="stat">
                    <span className="label">Capacity:</span>
                    <span className="value">{segment.capacity} veh/hr</span>
                  </div>
                  <div className="stat">
                    <span className="label">Utilization:</span>
                    <span className="value">{segment.utilization_percent}%</span>
                  </div>
                  <div className="stat">
                    <span className="label">Queue:</span>
                    <span className="value">{segment.current_queue} vehicles</span>
                  </div>
                </div>

                <div className="green-time-control">
                  <label>Green Time: {segment.green_time}s</label>
                  <input
                    type="range"
                    min="15"
                    max="90"
                    value={segment.green_time}
                    onChange={(e) => adjustGreenTime(id, parseInt(e.target.value))}
                    disabled={loading}
                  />
                  {segment.paired_segment && (
                    <small>Paired with: {status.segments[segment.paired_segment]?.name}</small>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleApp;