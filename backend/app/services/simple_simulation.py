"""
Simple, realistic traffic simulation with intersection logic
"""
import threading
import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SimpleSegment:
    id: str
    name: str
    capacity: int
    current_flow: int
    current_queue: float
    green_time: int  # seconds of green light
    utilization_percent: float
    congestion_level: str  # "green", "yellow", "red"
    segment_type: str  # "intersection", "road"
    paired_segment: Optional[str] = None  # For intersections

class SimpleTrafficSimulation:
    def __init__(self):
        self.segments: Dict[str, SimpleSegment] = {}
        self.is_running = False
        self.simulation_thread = None
        self.simulation_time = 8 * 60  # Start at 8:00 AM
        self.stop_event = threading.Event()
        
    def initialize_network(self, segments_data: List[Dict]):
        """Initialize network with simple segment data"""
        self.segments = {}
        
        for seg_data in segments_data:
            segment = SimpleSegment(
                id=seg_data['id'],
                name=seg_data['name'],
                capacity=seg_data['capacity'],
                current_flow=seg_data.get('current_flow', 0),
                current_queue=seg_data.get('current_queue', 0.0),
                green_time=seg_data.get('green_time', 45),
                utilization_percent=0.0,
                congestion_level="green",
                segment_type=seg_data.get('segment_type', 'road'),
                paired_segment=seg_data.get('paired_segment')
            )
            self.segments[segment.id] = segment
            
        self._update_all_segments()
        return True
    
    def adjust_green_time(self, segment_id: str, new_green_time: int):
        """Adjust green time for a segment and its paired segment"""
        if segment_id not in self.segments:
            return False
            
        segment = self.segments[segment_id]
        old_green_time = segment.green_time
        segment.green_time = max(15, min(90, new_green_time))  # Limit between 15-90 seconds
        
        # If this is an intersection with a paired segment, adjust the paired segment
        if segment.paired_segment and segment.paired_segment in self.segments:
            paired = self.segments[segment.paired_segment]
            # Total cycle time is typically 120 seconds, split between the two directions
            total_cycle = 120
            paired.green_time = total_cycle - segment.green_time
            
            # Immediately update flows based on new timing
            self._update_segment_flow(segment)
            self._update_segment_flow(paired)
            
        else:
            self._update_segment_flow(segment)
            
        return True
    
    def _update_segment_flow(self, segment: SimpleSegment):
        """Update traffic flow based on green time and time of day"""
        hour = (self.simulation_time // 60) % 24
        
        # Base demand based on time of day
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            base_demand = 0.8
        elif 11 <= hour <= 14:  # Lunch time
            base_demand = 0.6
        elif 22 <= hour or hour <= 6:  # Night
            base_demand = 0.2
        else:  # Regular hours
            base_demand = 0.5
            
        # Green time efficiency (more green time = better flow)
        green_efficiency = min(1.0, segment.green_time / 60.0)  # Normalize to 60 seconds
        
        # Location-specific factors
        location_factor = 1.0
        if "times_square" in segment.id.lower():
            location_factor = 1.4  # High traffic area
        elif "broadway" in segment.id.lower():
            location_factor = 1.2
        elif "tunnel" in segment.id.lower():
            location_factor = 1.6  # Very high traffic
            
        # Calculate new flow with some randomness for realism
        base_flow = segment.capacity * base_demand * green_efficiency * location_factor
        random_factor = random.uniform(0.85, 1.15)  # ±15% variation
        segment.current_flow = int(base_flow * random_factor)
        
        # Update utilization and congestion
        segment.utilization_percent = (segment.current_flow / segment.capacity) * 100
        
        if segment.utilization_percent >= 80:
            segment.congestion_level = "red"
        elif segment.utilization_percent >= 60:
            segment.congestion_level = "yellow"
        else:
            segment.congestion_level = "green"
            
        # Update queue based on congestion
        if segment.congestion_level == "red":
            segment.current_queue = min(20.0, segment.current_queue + random.uniform(0.5, 1.5))
        elif segment.congestion_level == "yellow":
            segment.current_queue = max(0.0, segment.current_queue + random.uniform(-0.5, 0.5))
        else:
            segment.current_queue = max(0.0, segment.current_queue - random.uniform(0.2, 0.8))
    
    def _update_all_segments(self):
        """Update all segments"""
        for segment in self.segments.values():
            self._update_segment_flow(segment)
    
    def start_simulation(self):
        """Start the dynamic simulation"""
        if self.is_running:
            return False
            
        self.is_running = True
        self.stop_event.clear()
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.start()
        return True
    
    def stop_simulation(self):
        """Stop the dynamic simulation"""
        if not self.is_running:
            return False
            
        self.is_running = False
        self.stop_event.set()
        if self.simulation_thread:
            self.simulation_thread.join()
        return True
    
    def _simulation_loop(self):
        """Main simulation loop"""
        while self.is_running and not self.stop_event.is_set():
            try:
                # Update simulation time (advance by 1 minute every 5 seconds for demo)
                self.simulation_time += 1
                if self.simulation_time >= 24 * 60:  # Reset after 24 hours
                    self.simulation_time = 0
                    
                # Update all traffic flows
                self._update_all_segments()
                
                # Wait 5 seconds before next update (fast for demo purposes)
                if self.stop_event.wait(5):
                    break
                    
            except Exception as e:
                print(f"Simulation error: {e}")
                break
    
    def get_status(self):
        """Get current simulation status"""
        if not self.segments:
            return {"error": "No network initialized"}
            
        total_segments = len(self.segments)
        high_congestion = sum(1 for s in self.segments.values() if s.congestion_level == "red")
        medium_congestion = sum(1 for s in self.segments.values() if s.congestion_level == "yellow")
        
        return {
            "simulation_running": self.is_running,
            "simulation_time": f"{(self.simulation_time // 60):02d}:{(self.simulation_time % 60):02d}",
            "total_segments": total_segments,
            "high_congestion": high_congestion,
            "medium_congestion": medium_congestion,
            "segments": {
                seg_id: {
                    "name": seg.name,
                    "current_flow": seg.current_flow,
                    "capacity": seg.capacity,
                    "utilization_percent": round(seg.utilization_percent, 1),
                    "congestion_level": seg.congestion_level,
                    "current_queue": round(seg.current_queue, 1),
                    "green_time": seg.green_time,
                    "paired_segment": seg.paired_segment
                }
                for seg_id, seg in self.segments.items()
            }
        }
    
    def set_time(self, time_minutes: int):
        """Set simulation time for testing"""
        self.simulation_time = time_minutes % (24 * 60)
        self._update_all_segments()
        return True

# Global instance
simple_simulation = SimpleTrafficSimulation()