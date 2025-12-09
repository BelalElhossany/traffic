import axios from 'axios';
import { TrafficNetwork, TrafficAction, SimulationResult, PredictionResult, AIRecommendation, NetworkStatus } from './types';

const API_BASE_URL = 'https://work-1-prrnhxygajyxxmlp.prod-runtime.all-hands.dev/api/traffic';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const trafficApi = {
  // Network management
  initializeNetwork: async (network: TrafficNetwork) => {
    const response = await api.post('/network/initialize', network);
    return response.data;
  },

  getNetworkStatus: async (): Promise<NetworkStatus> => {
    const response = await api.get('/network/status');
    return response.data;
  },

  // Simulation
  runSimulation: async (scenario: { name: string; actions: TrafficAction[]; duration_minutes: number }): Promise<SimulationResult> => {
    const response = await api.post('/simulation/run', scenario);
    return response.data;
  },

  // Prediction
  forecastCongestion: async (durationMinutes: number = 60): Promise<PredictionResult> => {
    const response = await api.post(`/prediction/forecast?duration_minutes=${durationMinutes}`);
    return response.data;
  },

  forecastWithActions: async (actions: TrafficAction[], durationMinutes: number = 60): Promise<PredictionResult> => {
    const response = await api.post(`/prediction/forecast-with-actions?duration_minutes=${durationMinutes}`, actions);
    return response.data;
  },

  // AI Recommendations
  getAIRecommendations: async (durationMinutes: number = 60): Promise<AIRecommendation> => {
    const response = await api.post(`/ai/recommend?duration_minutes=${durationMinutes}`);
    return response.data;
  },

  // Actions
  applyActions: async (actions: TrafficAction[]) => {
    const response = await api.post('/actions/apply', actions);
    return response.data;
  },

  resetActions: async () => {
    const response = await api.post('/actions/reset');
    return response.data;
  },

  // Segment controls
  adjustGreenTime: async (segmentId: string, adjustmentSeconds: number) => {
    const response = await api.post(`/segments/${segmentId}/green-time?adjustment_seconds=${adjustmentSeconds}`);
    return response.data;
  },

  togglePoliceControl: async (segmentId: string, enable: boolean, reductionFactor: number = 0.5) => {
    const response = await api.post(`/segments/${segmentId}/police-control?enable=${enable}&reduction_factor=${reductionFactor}`);
    return response.data;
  },

  getSegmentDetails: async (segmentId: string) => {
    const response = await api.get(`/segments/${segmentId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};