import numpy as np
from typing import Dict, List
from ..models.traffic import (
    TrafficNetwork, TrafficAction, PredictionResult, CongestionLevel
)
from .simulation_engine import TrafficSimulationEngine

class TrafficPredictionEngine:
    """
    Predicts traffic congestion 30-60 minutes ahead using forward simulation.
    """
    
    def __init__(self, network: TrafficNetwork):
        self.network = network
        self.simulation_engine = TrafficSimulationEngine(network)
    
    def predict_congestion(self, duration_minutes: int = 60) -> PredictionResult:
        """
        Run forward simulation to predict congestion evolution.
        """
        # Store current state
        initial_state = self._save_network_state()
        
        # Run prediction simulation
        result = self.simulation_engine.run_simulation(duration_minutes)
        
        # Restore initial state
        self._restore_network_state(initial_state)
        
        # Generate timestamps
        time_step = self.simulation_engine.time_step_minutes
        num_steps = int(duration_minutes / time_step) + 1
        timestamps = [int(i * time_step) for i in range(num_steps)]
        
        # Identify congestion warnings
        warnings = self._generate_congestion_warnings(result.queue_evolution, timestamps)
        
        # Generate basic recommendations
        recommendations = self._generate_basic_recommendations(result.congestion_segments)
        
        return PredictionResult(
            timestamp_minutes=timestamps,
            predicted_queues=result.queue_evolution,
            congestion_warnings=warnings,
            recommended_actions=recommendations
        )
    
    def _save_network_state(self) -> Dict:
        """Save current network state for restoration."""
        state = {}
        for segment_id, segment in self.network.segments.items():
            state[segment_id] = {
                'current_queue': segment.current_queue,
                'current_flow': segment.current_flow,
                'green_time_adjustment': segment.green_time_adjustment,
                'police_control': segment.police_control,
                'police_reduction': segment.police_reduction,
                'weather_factor': segment.weather_factor
            }
        return state
    
    def _restore_network_state(self, state: Dict):
        """Restore network state from saved state."""
        for segment_id, segment_state in state.items():
            if segment_id in self.network.segments:
                segment = self.network.segments[segment_id]
                for attr, value in segment_state.items():
                    setattr(segment, attr, value)
    
    def _generate_congestion_warnings(self, queue_evolution: Dict[str, List[float]], 
                                    timestamps: List[int]) -> List[Dict[str, str]]:
        """
        Generate warnings for predicted congestion hotspots.
        """
        warnings = []
        
        for segment_id, queue_history in queue_evolution.items():
            segment = self.network.segments[segment_id]
            capacity = self.network.get_effective_capacity(segment_id)
            
            # Find when congestion starts building
            for i, queue_length in enumerate(queue_history[1:], 1):  # Skip initial state
                if i < len(timestamps):
                    queue_ratio = queue_length / (capacity * self.simulation_engine.time_step_hours) if capacity > 0 else 0
                    
                    # Warning threshold: queue ratio > 0.7
                    if queue_ratio > 0.7 and (i == 1 or queue_history[i-1] / (capacity * self.simulation_engine.time_step_hours) <= 0.7):
                        warnings.append({
                            'segment_id': segment_id,
                            'segment_name': segment.name,
                            'warning_time': str(timestamps[i]),
                            'severity': 'high' if queue_ratio > 1.2 else 'medium',
                            'message': f"Congestion predicted on {segment.name} in {timestamps[i]} minutes"
                        })
                        break
        
        return warnings
    
    def _generate_basic_recommendations(self, congested_segments: List[str]) -> List[TrafficAction]:
        """
        Generate basic recommendations for congested segments.
        """
        recommendations = []
        
        for segment_id in congested_segments:
            segment = self.network.segments[segment_id]
            
            if segment.segment_type.value == "intersection":
                # Recommend increasing green time for intersections
                recommendations.append(TrafficAction(
                    segment_id=segment_id,
                    action_type="green_time",
                    value=10.0,  # Add 10 seconds
                    description=f"Increase green time at {segment.name} by 10 seconds"
                ))
            else:
                # Recommend police control for road segments
                recommendations.append(TrafficAction(
                    segment_id=segment_id,
                    action_type="police_control",
                    value=0.5,  # 50% flow reduction
                    description=f"Apply police flow control on {segment.name} (50% reduction)"
                ))
        
        return recommendations
    
    def predict_with_actions(self, actions: List[TrafficAction], 
                           duration_minutes: int = 60) -> PredictionResult:
        """
        Predict congestion evolution with specific actions applied.
        """
        # Store current state
        initial_state = self._save_network_state()
        
        # Run prediction simulation with actions
        result = self.simulation_engine.run_simulation(duration_minutes, actions)
        
        # Restore initial state
        self._restore_network_state(initial_state)
        
        # Generate timestamps
        time_step = self.simulation_engine.time_step_minutes
        num_steps = int(duration_minutes / time_step) + 1
        timestamps = [int(i * time_step) for i in range(num_steps)]
        
        # Generate warnings and recommendations
        warnings = self._generate_congestion_warnings(result.queue_evolution, timestamps)
        recommendations = self._generate_basic_recommendations(result.congestion_segments)
        
        return PredictionResult(
            timestamp_minutes=timestamps,
            predicted_queues=result.queue_evolution,
            congestion_warnings=warnings,
            recommended_actions=recommendations
        )