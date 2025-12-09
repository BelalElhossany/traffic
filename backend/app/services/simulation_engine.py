import numpy as np
from typing import Dict, List, Tuple
from ..models.traffic import (
    TrafficNetwork, TrafficSegment, TrafficAction, SimulationResult, 
    CongestionLevel, SegmentType
)

class TrafficSimulationEngine:
    """
    Macroscopic traffic simulation engine using queueing theory.
    Implements: Q(t+1) = Q(t) + Arrivals(t) - Departures(t)
    """
    
    def __init__(self, network: TrafficNetwork, time_step_minutes: float = 1.0):
        self.network = network
        self.time_step_minutes = time_step_minutes
        self.time_step_hours = time_step_minutes / 60.0
        
    def calculate_arrivals(self, segment_id: str, current_time: int) -> float:
        """
        Calculate arrival rate for a segment based on upstream flow and demand patterns.
        Enhanced with realistic time-based patterns and segment-specific factors.
        """
        segment = self.network.segments[segment_id]
        
        # Enhanced time-based demand patterns
        hour_of_day = (current_time // 60) % 24
        minute_of_hour = current_time % 60
        
        # More realistic demand patterns
        if 7 <= hour_of_day <= 9:  # Morning rush hour
            demand_factor = 1.8 + 0.3 * np.sin((hour_of_day - 7) * np.pi / 2)
        elif 17 <= hour_of_day <= 19:  # Evening rush hour
            demand_factor = 1.6 + 0.4 * np.sin((hour_of_day - 17) * np.pi / 2)
        elif 11 <= hour_of_day <= 14:  # Lunch time
            demand_factor = 1.2
        elif 6 <= hour_of_day <= 7 or 19 <= hour_of_day <= 21:  # Shoulder hours
            demand_factor = 1.0
        elif 21 <= hour_of_day <= 23:  # Evening
            demand_factor = 0.8
        elif 0 <= hour_of_day <= 6:  # Night/early morning
            demand_factor = 0.3 + 0.2 * np.sin(hour_of_day * np.pi / 6)
        else:  # Default
            demand_factor = 0.7
        
        # Segment-specific factors based on location type
        if "times_square" in segment_id or "herald_square" in segment_id:
            # Tourist areas have different patterns
            location_factor = 1.3 if 10 <= hour_of_day <= 22 else 0.8
        elif "lincoln_tunnel" in segment_id or "highway" in segment_id:
            # Commuter routes have stronger rush hour patterns
            location_factor = 1.5 if (7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19) else 0.9
        elif "broadway" in segment_id:
            # Broadway has consistent high traffic
            location_factor = 1.2
        else:
            location_factor = 1.0
        
        # Weekend vs weekday (simplified - assume weekday for now)
        weekday_factor = 1.0
        
        # Weather impact
        weather_impact = segment.weather_factor
        
        # Base arrival rate with all factors
        base_arrival_rate = segment.capacity * 0.75 * demand_factor * location_factor * weekday_factor * weather_impact
        
        # Add realistic variability with some correlation to previous values
        noise_amplitude = 0.15 * base_arrival_rate
        noise = np.random.normal(0, noise_amplitude)
        
        # Add some minute-level variation for realism
        minute_variation = 0.1 * np.sin(minute_of_hour * np.pi / 30) * base_arrival_rate
        
        arrival_rate = max(0, base_arrival_rate + noise + minute_variation)
        
        return arrival_rate * self.time_step_hours
    
    def calculate_departures(self, segment_id: str) -> float:
        """
        Calculate departure rate based on current queue and effective capacity.
        """
        segment = self.network.segments[segment_id]
        effective_capacity = self.network.get_effective_capacity(segment_id)
        
        # Departures are limited by both queue size and capacity
        max_departures = effective_capacity * self.time_step_hours
        available_vehicles = segment.current_queue + segment.current_flow * self.time_step_hours
        
        return min(max_departures, available_vehicles)
    
    def update_queue(self, segment_id: str, arrivals: float, departures: float):
        """
        Update queue length using the fundamental equation:
        Q(t+1) = Q(t) + Arrivals(t) - Departures(t)
        """
        segment = self.network.segments[segment_id]
        new_queue = max(0, segment.current_queue + arrivals - departures)
        segment.current_queue = new_queue
        segment.current_flow = departures / self.time_step_hours if self.time_step_hours > 0 else 0
    
    def get_congestion_level(self, segment_id: str) -> CongestionLevel:
        """
        Determine congestion level based on queue length and capacity.
        """
        segment = self.network.segments[segment_id]
        capacity = self.network.get_effective_capacity(segment_id)
        
        # Queue-to-capacity ratio
        if capacity > 0:
            queue_ratio = segment.current_queue / (capacity * self.time_step_hours)
        else:
            queue_ratio = float('inf')
        
        if queue_ratio < 0.3:
            return CongestionLevel.LOW
        elif queue_ratio < 0.7:
            return CongestionLevel.MEDIUM
        elif queue_ratio < 1.5:
            return CongestionLevel.HIGH
        else:
            return CongestionLevel.GRIDLOCK
    
    def apply_actions(self, actions: List[TrafficAction]):
        """
        Apply traffic control actions to the network.
        """
        for action in actions:
            if action.segment_id not in self.network.segments:
                continue
                
            segment = self.network.segments[action.segment_id]
            
            if action.action_type == "green_time":
                segment.green_time_adjustment = action.value
            elif action.action_type == "police_control":
                segment.police_control = True
                segment.police_reduction = action.value
            elif action.action_type == "weather":
                segment.weather_factor = action.value
            elif action.action_type == "remove_police":
                segment.police_control = False
                segment.police_reduction = 0.5
    
    def reset_actions(self):
        """
        Reset all traffic control actions to default state.
        """
        for segment in self.network.segments.values():
            segment.green_time_adjustment = 0.0
            segment.police_control = False
            segment.police_reduction = 0.5
            segment.weather_factor = 1.0
    
    def simulate_step(self, current_time: int) -> Dict[str, float]:
        """
        Simulate one time step for all segments.
        Returns queue lengths for this step.
        """
        step_queues = {}
        
        # Calculate arrivals and departures for all segments
        arrivals_departures = {}
        for segment_id in self.network.segments:
            arrivals = self.calculate_arrivals(segment_id, current_time)
            departures = self.calculate_departures(segment_id)
            arrivals_departures[segment_id] = (arrivals, departures)
        
        # Update all queues simultaneously
        for segment_id, (arrivals, departures) in arrivals_departures.items():
            self.update_queue(segment_id, arrivals, departures)
            step_queues[segment_id] = self.network.segments[segment_id].current_queue
        
        return step_queues
    
    def run_simulation(self, duration_minutes: int, actions: List[TrafficAction] = None) -> SimulationResult:
        """
        Run complete simulation for specified duration.
        """
        if actions:
            self.apply_actions(actions)
        
        # Store initial state
        initial_queues = {sid: segment.current_queue for sid, segment in self.network.segments.items()}
        
        # Run simulation
        queue_evolution = {sid: [segment.current_queue] for sid, segment in self.network.segments.items()}
        total_delay = 0.0
        max_queue = 0.0
        
        num_steps = int(duration_minutes / self.time_step_minutes)
        
        for step in range(num_steps):
            current_time = step * self.time_step_minutes
            step_queues = self.simulate_step(int(current_time))
            
            # Record queue evolution
            for segment_id, queue_length in step_queues.items():
                queue_evolution[segment_id].append(queue_length)
                max_queue = max(max_queue, queue_length)
                total_delay += queue_length * self.time_step_minutes
        
        # Determine final congestion levels and congested segments
        congestion_levels = {}
        congestion_segments = []
        
        for segment_id in self.network.segments:
            level = self.get_congestion_level(segment_id)
            congestion_levels[segment_id] = level
            if level in [CongestionLevel.HIGH, CongestionLevel.GRIDLOCK]:
                congestion_segments.append(segment_id)
        
        # Reset actions after simulation
        if actions:
            self.reset_actions()
            # Restore initial state
            for sid, initial_queue in initial_queues.items():
                self.network.segments[sid].current_queue = initial_queue
        
        return SimulationResult(
            scenario_name="simulation",
            total_delay=total_delay,
            max_queue_length=max_queue,
            congestion_segments=congestion_segments,
            queue_evolution=queue_evolution,
            congestion_levels=congestion_levels
        )