import React, { useState } from 'react';
import { TrafficNetwork, NetworkStatus, PredictionResult, AIRecommendation } from '../types';

interface ControlPanelProps {
  network: TrafficNetwork | null;
  networkStatus: NetworkStatus | null;
  selectedSegmentId: string | null;
  prediction: PredictionResult | null;
  aiRecommendation: AIRecommendation | null;
  loading: boolean;
  onRunPrediction: (durationMinutes: number) => void;
  onGetAIRecommendations: (durationMinutes: number) => void;
  onApplyGreenTimeAdjustment: (segmentId: string, adjustment: number) => void;
  onTogglePoliceControl: (segmentId: string, enable: boolean, reduction: number) => void;
  onResetActions: () => void;
  onRefreshStatus: () => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
  network,
  networkStatus,
  selectedSegmentId,
  prediction,
  aiRecommendation,
  loading,
  onRunPrediction,
  onGetAIRecommendations,
  onApplyGreenTimeAdjustment,
  onTogglePoliceControl,
  onResetActions,
  onRefreshStatus
}) => {
  const [predictionDuration, setPredictionDuration] = useState(60);
  const [greenTimeAdjustment, setGreenTimeAdjustment] = useState(10);
  const [policeReduction, setPoliceReduction] = useState(0.5);

  const selectedSegment = selectedSegmentId && network ? network.segments[selectedSegmentId] : null;
  const selectedStatus = selectedSegmentId && networkStatus ? networkStatus[selectedSegmentId] : null;

  const getCongestionStatusColor = (level: string) => {
    switch (level) {
      case 'low': return 'status-low';
      case 'medium': return 'status-medium';
      case 'high': return 'status-high';
      case 'gridlock': return 'status-gridlock';
      default: return 'status-low';
    }
  };

  return (
    <div>
      {/* Network Overview */}
      <div className="control-panel">
        <h3>Network Overview</h3>
        <div style={{ marginBottom: '10px' }}>
          <button className="btn btn-success" onClick={onRefreshStatus} disabled={loading}>
            Refresh Status
          </button>
          <button className="btn btn-warning" onClick={onResetActions} disabled={loading}>
            Reset All Actions
          </button>
        </div>
        
        {networkStatus && (
          <div>
            <p>Total Segments: {Object.keys(networkStatus).length}</p>
            <div style={{ fontSize: '12px' }}>
              {Object.entries(networkStatus).map(([segmentId, status]) => (
                <div key={segmentId} className="segment-info">
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                    <span className={`status-indicator ${getCongestionStatusColor(status.congestion_level)}`}></span>
                    <strong>{status.name}</strong>
                  </div>
                  <p>Queue: {status.current_queue.toFixed(1)} vehicles</p>
                  <p>Flow: {status.current_flow.toFixed(1)} veh/hr</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Selected Segment Controls */}
      {selectedSegment && (
        <div className="control-panel">
          <h3>Selected: {selectedSegment.name}</h3>
          
          {selectedStatus && (
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                <span className={`status-indicator ${getCongestionStatusColor(selectedStatus.congestion_level)}`}></span>
                <span>Congestion: {selectedStatus.congestion_level}</span>
              </div>
              <p>Queue: {selectedStatus.current_queue.toFixed(1)} vehicles</p>
              <p>Flow: {selectedStatus.current_flow.toFixed(1)} veh/hr</p>
              <p>Capacity: {selectedStatus.capacity.toFixed(1)} veh/hr</p>
            </div>
          )}

          {selectedSegment.segment_type === 'intersection' && (
            <div className="control-group">
              <label>Green Time Adjustment</label>
              <input
                type="range"
                min="0"
                max="30"
                value={greenTimeAdjustment}
                onChange={(e) => setGreenTimeAdjustment(Number(e.target.value))}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#ccc' }}>
                <span>0s</span>
                <span>{greenTimeAdjustment}s</span>
                <span>30s</span>
              </div>
              <button
                className="btn"
                onClick={() => onApplyGreenTimeAdjustment(selectedSegmentId, greenTimeAdjustment)}
                disabled={loading}
              >
                Apply Green Time +{greenTimeAdjustment}s
              </button>
              <p style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>
                Current: {(selectedSegment.green_time || 0) + selectedSegment.green_time_adjustment}s
                {selectedSegment.green_time_adjustment > 0 && ` (+${selectedSegment.green_time_adjustment}s)`}
              </p>
            </div>
          )}

          {selectedSegment.segment_type === 'road' && (
            <div className="control-group">
              <label>Police Flow Control</label>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.1"
                value={policeReduction}
                onChange={(e) => setPoliceReduction(Number(e.target.value))}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#ccc' }}>
                <span>10% flow</span>
                <span>{Math.round((1 - policeReduction) * 100)}% flow</span>
                <span>90% flow</span>
              </div>
              <div>
                <button
                  className={`btn ${selectedSegment.police_control ? 'btn-danger' : 'btn-warning'}`}
                  onClick={() => onTogglePoliceControl(selectedSegmentId, !selectedSegment.police_control, policeReduction)}
                  disabled={loading}
                >
                  {selectedSegment.police_control ? 'Remove Police Control' : 'Apply Police Control'}
                </button>
              </div>
              {selectedSegment.police_control && (
                <p style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>
                  Active: {Math.round((1 - selectedSegment.police_reduction) * 100)}% flow allowed
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Simulation Controls */}
      <div className="control-panel">
        <h3>Simulation & Prediction</h3>
        
        <div className="control-group">
          <label>Duration (minutes)</label>
          <input
            type="number"
            min="15"
            max="120"
            value={predictionDuration}
            onChange={(e) => setPredictionDuration(Number(e.target.value))}
          />
        </div>

        <div>
          <button
            className="btn"
            onClick={() => onRunPrediction(predictionDuration)}
            disabled={loading}
          >
            {loading ? 'Running...' : 'Run Prediction'}
          </button>
          <button
            className="btn btn-success"
            onClick={() => onGetAIRecommendations(predictionDuration)}
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Get AI Recommendations'}
          </button>
        </div>
      </div>

      {/* Prediction Results */}
      {prediction && (
        <div className="control-panel">
          <h3>Prediction Results</h3>
          
          {prediction.congestion_warnings.length > 0 ? (
            <div className="prediction-warnings">
              <h4 style={{ color: '#f44336', marginBottom: '10px' }}>⚠️ Congestion Warnings</h4>
              {prediction.congestion_warnings.map((warning, index) => (
                <div key={index} className="warning-item">
                  <strong>{warning.segment_name}</strong>
                  <p>{warning.message}</p>
                  <p style={{ fontSize: '11px', opacity: 0.8 }}>
                    Severity: {warning.severity} | Time: {warning.warning_time} min
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#4caf50' }}>✅ No congestion warnings for the next {predictionDuration} minutes</p>
          )}

          {prediction.recommended_actions.length > 0 && (
            <div style={{ marginTop: '15px' }}>
              <h4>Recommended Actions:</h4>
              {prediction.recommended_actions.map((action, index) => (
                <div key={index} style={{ fontSize: '12px', marginBottom: '5px', padding: '5px', backgroundColor: '#333', borderRadius: '3px' }}>
                  {action.description}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* AI Recommendations */}
      {aiRecommendation && (
        <div className="control-panel">
          <h3>AI Recommendations</h3>
          
          <div style={{ marginBottom: '15px' }}>
            <p><strong>Best Scenario:</strong> {aiRecommendation.best_scenario}</p>
            <p><strong>Expected Improvement:</strong> {(aiRecommendation.expected_improvement * 100).toFixed(1)}%</p>
            <p><strong>Confidence:</strong> {(aiRecommendation.confidence_score * 100).toFixed(1)}%</p>
          </div>

          {aiRecommendation.recommended_actions.length > 0 && (
            <div>
              <h4>Recommended Actions:</h4>
              {aiRecommendation.recommended_actions.map((action, index) => (
                <div key={index} style={{ fontSize: '12px', marginBottom: '8px', padding: '8px', backgroundColor: '#2a4a2a', borderRadius: '4px', borderLeft: '3px solid #4caf50' }}>
                  <strong>{action.description}</strong>
                  <p style={{ opacity: 0.8, marginTop: '3px' }}>
                    Segment: {network?.segments[action.segment_id]?.name || action.segment_id}
                  </p>
                </div>
              ))}
            </div>
          )}

          {Object.keys(aiRecommendation.comparison_results).length > 1 && (
            <div style={{ marginTop: '15px' }}>
              <h4>Scenario Comparison:</h4>
              {Object.entries(aiRecommendation.comparison_results).map(([scenario, result]) => (
                <div key={scenario} style={{ fontSize: '11px', marginBottom: '5px', padding: '5px', backgroundColor: scenario === aiRecommendation.best_scenario ? '#2a4a2a' : '#333', borderRadius: '3px' }}>
                  <strong>{scenario}:</strong> {result.total_delay.toFixed(1)} delay units
                  {scenario === aiRecommendation.best_scenario && ' ⭐'}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ControlPanel;