import React, { useState, useEffect } from 'react';
import TrafficMap from './components/TrafficMap';
import ControlPanel from './components/ControlPanel';
import { TrafficNetwork, NetworkStatus, PredictionResult, AIRecommendation } from './types';
import { trafficApi } from './api';
import { createSampleNetwork } from './sampleNetwork';
import './index.css';

function App() {
  const [network, setNetwork] = useState<TrafficNetwork | null>(null);
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus | null>(null);
  const [selectedSegmentId, setSelectedSegmentId] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [aiRecommendation, setAiRecommendation] = useState<AIRecommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize network on component mount
  useEffect(() => {
    initializeNetwork();
  }, []);

  // Refresh network status periodically
  useEffect(() => {
    if (network) {
      const interval = setInterval(refreshNetworkStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [network]);

  const initializeNetwork = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const sampleNetwork = createSampleNetwork();
      await trafficApi.initializeNetwork(sampleNetwork);
      
      setNetwork(sampleNetwork);
      await refreshNetworkStatus();
      
      console.log('Network initialized successfully');
    } catch (err) {
      setError(`Failed to initialize network: ${err}`);
      console.error('Network initialization error:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshNetworkStatus = async () => {
    try {
      const status = await trafficApi.getNetworkStatus();
      setNetworkStatus(status);
    } catch (err) {
      console.error('Failed to refresh network status:', err);
    }
  };

  const runPrediction = async (durationMinutes: number = 60) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await trafficApi.forecastCongestion(durationMinutes);
      setPrediction(result);
      
      console.log('Prediction completed:', result);
    } catch (err) {
      setError(`Prediction failed: ${err}`);
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getAIRecommendations = async (durationMinutes: number = 60) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await trafficApi.getAIRecommendations(durationMinutes);
      setAiRecommendation(result);
      
      console.log('AI recommendations:', result);
    } catch (err) {
      setError(`AI recommendation failed: ${err}`);
      console.error('AI recommendation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyGreenTimeAdjustment = async (segmentId: string, adjustment: number) => {
    try {
      await trafficApi.adjustGreenTime(segmentId, adjustment);
      await refreshNetworkStatus();
      console.log(`Green time adjusted for ${segmentId}: +${adjustment}s`);
    } catch (err) {
      setError(`Failed to adjust green time: ${err}`);
      console.error('Green time adjustment error:', err);
    }
  };

  const togglePoliceControl = async (segmentId: string, enable: boolean, reduction: number = 0.5) => {
    try {
      await trafficApi.togglePoliceControl(segmentId, enable, reduction);
      await refreshNetworkStatus();
      console.log(`Police control ${enable ? 'enabled' : 'disabled'} for ${segmentId}`);
    } catch (err) {
      setError(`Failed to toggle police control: ${err}`);
      console.error('Police control error:', err);
    }
  };

  const resetAllActions = async () => {
    try {
      await trafficApi.resetActions();
      await refreshNetworkStatus();
      console.log('All actions reset');
    } catch (err) {
      setError(`Failed to reset actions: ${err}`);
      console.error('Reset actions error:', err);
    }
  };

  if (loading && !network) {
    return (
      <div className="app-container">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#fff' }}>
          <div>
            <h2>Initializing Traffic Network...</h2>
            <p>Please wait while we set up the simulation environment.</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !network) {
    return (
      <div className="app-container">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#fff' }}>
          <div>
            <h2>Error</h2>
            <p className="error">{error}</p>
            <button className="btn" onClick={initializeNetwork}>
              Retry Initialization
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="sidebar">
        <h1 style={{ color: '#fff', marginBottom: '20px', fontSize: '18px' }}>
          AI Traffic Simulator
        </h1>
        
        {error && (
          <div className="error" style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#4a2c2a', borderRadius: '4px' }}>
            {error}
          </div>
        )}

        <ControlPanel
          network={network}
          networkStatus={networkStatus}
          selectedSegmentId={selectedSegmentId}
          prediction={prediction}
          aiRecommendation={aiRecommendation}
          loading={loading}
          onRunPrediction={runPrediction}
          onGetAIRecommendations={getAIRecommendations}
          onApplyGreenTimeAdjustment={applyGreenTimeAdjustment}
          onTogglePoliceControl={togglePoliceControl}
          onResetActions={resetAllActions}
          onRefreshStatus={refreshNetworkStatus}
        />
      </div>

      <div className="map-container">
        <TrafficMap
          network={network}
          networkStatus={networkStatus}
          selectedSegmentId={selectedSegmentId}
          onSegmentSelect={setSelectedSegmentId}
        />
      </div>
    </div>
  );
}

export default App;