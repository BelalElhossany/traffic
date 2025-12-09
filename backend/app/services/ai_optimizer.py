import numpy as np
from typing import Dict, List, Tuple
from itertools import product
from ..models.traffic import (
    TrafficNetwork, TrafficAction, SimulationResult, AIRecommendation, SegmentType
)
from .simulation_engine import TrafficSimulationEngine

class AITrafficOptimizer:
    """
    AI module that evaluates multiple scenarios and recommends optimal actions
    to minimize total vehicle delay and congestion.
    """
    
    def __init__(self, network: TrafficNetwork):
        self.network = network
        self.simulation_engine = TrafficSimulationEngine(network)
    
    def generate_action_combinations(self) -> List[List[TrafficAction]]:
        """
        Generate different combinations of traffic control actions.
        """
        action_sets = []
        
        # Baseline scenario (no actions)
        action_sets.append([])
        
        # Single action scenarios
        for segment_id, segment in self.network.segments.items():
            if segment.segment_type == SegmentType.INTERSECTION:
                # Green time adjustments: +5s, +10s, +15s
                for green_adjustment in [5, 10, 15]:
                    action_sets.append([TrafficAction(
                        segment_id=segment_id,
                        action_type="green_time",
                        value=green_adjustment,
                        description=f"Increase green time at {segment.name} by {green_adjustment}s"
                    )])
            else:
                # Police control scenarios: 30%, 50%, 70% flow reduction
                for reduction in [0.3, 0.5, 0.7]:
                    action_sets.append([TrafficAction(
                        segment_id=segment_id,
                        action_type="police_control",
                        value=reduction,
                        description=f"Apply police control on {segment.name} ({int((1-reduction)*100)}% flow)"
                    )])
        
        # Combined scenarios (limited to avoid exponential explosion)
        intersections = [sid for sid, seg in self.network.segments.items() 
                        if seg.segment_type == SegmentType.INTERSECTION]
        roads = [sid for sid, seg in self.network.segments.items() 
                if seg.segment_type == SegmentType.ROAD]
        
        # Combine one intersection action with one road action
        if len(intersections) > 0 and len(roads) > 0:
            for intersection_id in intersections[:3]:  # Limit to first 3 intersections
                for road_id in roads[:3]:  # Limit to first 3 roads
                    action_sets.append([
                        TrafficAction(
                            segment_id=intersection_id,
                            action_type="green_time",
                            value=10,
                            description=f"Increase green time at {self.network.segments[intersection_id].name} by 10s"
                        ),
                        TrafficAction(
                            segment_id=road_id,
                            action_type="police_control",
                            value=0.5,
                            description=f"Apply police control on {self.network.segments[road_id].name} (50% flow)"
                        )
                    ])
        
        return action_sets
    
    def evaluate_scenario(self, actions: List[TrafficAction], 
                         scenario_name: str, duration_minutes: int = 60) -> SimulationResult:
        """
        Evaluate a specific scenario and return simulation results.
        """
        # Store initial state
        initial_state = self._save_network_state()
        
        # Run simulation
        result = self.simulation_engine.run_simulation(duration_minutes, actions)
        result.scenario_name = scenario_name
        
        # Restore initial state
        self._restore_network_state(initial_state)
        
        return result
    
    def calculate_improvement_score(self, baseline_result: SimulationResult, 
                                  scenario_result: SimulationResult) -> float:
        """
        Calculate improvement score compared to baseline.
        Higher score means better improvement.
        """
        if baseline_result.total_delay == 0:
            return 0.0
        
        # Primary metric: delay reduction
        delay_improvement = (baseline_result.total_delay - scenario_result.total_delay) / baseline_result.total_delay
        
        # Secondary metric: max queue reduction
        queue_improvement = 0.0
        if baseline_result.max_queue_length > 0:
            queue_improvement = (baseline_result.max_queue_length - scenario_result.max_queue_length) / baseline_result.max_queue_length
        
        # Combined score (weighted)
        improvement_score = 0.7 * delay_improvement + 0.3 * queue_improvement
        
        return improvement_score
    
    def calculate_confidence_score(self, improvement_score: float, 
                                 num_congested_segments: int) -> float:
        """
        Calculate confidence score for the recommendation.
        """
        # Base confidence on improvement magnitude
        base_confidence = min(abs(improvement_score) * 2, 1.0)
        
        # Reduce confidence if many segments are congested (complex situation)
        complexity_penalty = min(num_congested_segments * 0.1, 0.3)
        
        confidence = max(0.1, base_confidence - complexity_penalty)
        
        return confidence
    
    def optimize_traffic_actions(self, duration_minutes: int = 60) -> AIRecommendation:
        """
        Find optimal traffic control actions using multi-scenario evaluation.
        """
        # Generate all action combinations
        action_combinations = self.generate_action_combinations()
        
        # Evaluate all scenarios
        results = {}
        baseline_result = None
        
        for i, actions in enumerate(action_combinations):
            scenario_name = f"scenario_{i}" if actions else "baseline"
            result = self.evaluate_scenario(actions, scenario_name, duration_minutes)
            results[scenario_name] = result
            
            if not actions:  # Baseline scenario
                baseline_result = result
        
        # Find best scenario
        best_scenario = "baseline"
        best_improvement = 0.0
        best_actions = []
        
        if baseline_result:
            for scenario_name, result in results.items():
                if scenario_name != "baseline":
                    improvement = self.calculate_improvement_score(baseline_result, result)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_scenario = scenario_name
                        # Find corresponding actions
                        scenario_index = int(scenario_name.split('_')[1])
                        best_actions = action_combinations[scenario_index]
        
        # Calculate confidence score
        num_congested = len(baseline_result.congestion_segments) if baseline_result else 0
        confidence = self.calculate_confidence_score(best_improvement, num_congested)
        
        return AIRecommendation(
            best_scenario=best_scenario,
            expected_improvement=best_improvement,
            recommended_actions=best_actions,
            comparison_results=results,
            confidence_score=confidence
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