from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np

class SegmentType(str, Enum):
    ROAD = "road"
    INTERSECTION = "intersection"

class CongestionLevel(str, Enum):
    LOW = "low"      # Green
    MEDIUM = "medium"  # Yellow
    HIGH = "high"    # Red
    GRIDLOCK = "gridlock"  # Black

class TrafficSegment(BaseModel):
    id: str
    name: str
    segment_type: SegmentType
    capacity: float = Field(..., description="Base capacity (vehicles/hour)")
    length: float = Field(..., description="Segment length in meters")
    current_queue: float = Field(default=0.0, description="Current queue length (vehicles)")
    current_flow: float = Field(default=0.0, description="Current flow rate (vehicles/hour)")
    coordinates: List[Tuple[float, float]] = Field(..., description="Lat/lon coordinates for visualization")
    
    # Traffic light properties (for intersections)
    cycle_time: Optional[float] = Field(default=120.0, description="Traffic light cycle time in seconds")
    green_time: Optional[float] = Field(default=60.0, description="Green time in seconds")
    
    # Control modifications
    police_control: bool = Field(default=False, description="Police flow control active")
    police_reduction: float = Field(default=0.5, description="Flow reduction factor when police control active")
    weather_factor: float = Field(default=1.0, description="Weather impact on capacity (0.4-1.0)")
    green_time_adjustment: float = Field(default=0.0, description="Additional green time in seconds")

class TrafficNetwork(BaseModel):
    segments: Dict[str, TrafficSegment]
    connections: Dict[str, List[str]] = Field(default_factory=dict, description="Segment connectivity graph")
    
    def get_effective_capacity(self, segment_id: str) -> float:
        """Calculate effective capacity considering all modifications"""
        segment = self.segments[segment_id]
        base_capacity = segment.capacity
        
        # Apply weather factor
        capacity = base_capacity * segment.weather_factor
        
        # Apply police control
        if segment.police_control:
            capacity *= segment.police_reduction
        
        # Apply green time adjustment for intersections
        if segment.segment_type == SegmentType.INTERSECTION and segment.cycle_time:
            original_green_ratio = segment.green_time / segment.cycle_time
            new_green_time = segment.green_time + segment.green_time_adjustment
            new_green_ratio = min(new_green_time / segment.cycle_time, 0.95)  # Max 95% green
            capacity *= (new_green_ratio / original_green_ratio)
        
        return max(capacity, 0.1)  # Minimum capacity to avoid division by zero

class TrafficAction(BaseModel):
    segment_id: str
    action_type: str  # "green_time", "police_control", "weather"
    value: float
    description: str

class SimulationScenario(BaseModel):
    name: str
    actions: List[TrafficAction]
    duration_minutes: int = Field(default=60, description="Simulation duration in minutes")

class SimulationResult(BaseModel):
    scenario_name: str
    total_delay: float
    max_queue_length: float
    congestion_segments: List[str]
    queue_evolution: Dict[str, List[float]]  # segment_id -> queue lengths over time
    congestion_levels: Dict[str, CongestionLevel]
    
class PredictionResult(BaseModel):
    timestamp_minutes: List[int]
    predicted_queues: Dict[str, List[float]]
    congestion_warnings: List[Dict[str, str]]
    recommended_actions: List[TrafficAction]

class AIRecommendation(BaseModel):
    best_scenario: str
    expected_improvement: float
    recommended_actions: List[TrafficAction]
    comparison_results: Dict[str, SimulationResult]
    confidence_score: float