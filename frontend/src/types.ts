export interface TrafficSegment {
  id: string;
  name: string;
  segment_type: 'road' | 'intersection';
  capacity: number;
  length: number;
  current_queue: number;
  current_flow: number;
  coordinates: [number, number][];
  cycle_time?: number;
  green_time?: number;
  police_control: boolean;
  police_reduction: number;
  weather_factor: number;
  green_time_adjustment: number;
}

export interface TrafficNetwork {
  segments: Record<string, TrafficSegment>;
  connections: Record<string, string[]>;
}

export interface TrafficAction {
  segment_id: string;
  action_type: string;
  value: number;
  description: string;
}

export interface SimulationResult {
  scenario_name: string;
  total_delay: number;
  max_queue_length: number;
  congestion_segments: string[];
  queue_evolution: Record<string, number[]>;
  congestion_levels: Record<string, CongestionLevel>;
}

export interface PredictionResult {
  timestamp_minutes: number[];
  predicted_queues: Record<string, number[]>;
  congestion_warnings: Array<{
    segment_id: string;
    segment_name: string;
    warning_time: string;
    severity: string;
    message: string;
  }>;
  recommended_actions: TrafficAction[];
}

export interface AIRecommendation {
  best_scenario: string;
  expected_improvement: number;
  recommended_actions: TrafficAction[];
  comparison_results: Record<string, SimulationResult>;
  confidence_score: number;
}

export type CongestionLevel = 'low' | 'medium' | 'high' | 'gridlock';

export interface NetworkStatus {
  [segmentId: string]: {
    name: string;
    current_queue: number;
    current_flow: number;
    capacity: number;
    congestion_level: CongestionLevel;
  };
}