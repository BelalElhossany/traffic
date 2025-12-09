"""
Graph-based traffic simulation with nodes (intersections) and edges (segments)
Supports intersection, merge, split road types with connected flow calculations
"""
import math
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

class NodeType(Enum):
    INTERSECTION = "intersection"
    MERGE = "merge"
    SPLIT = "split"

class SegmentType(Enum):
    ROAD = "road"
    HIGHWAY = "highway"
    ARTERIAL = "arterial"

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

@dataclass
class TrafficLight:
    """Traffic light with directional green times"""
    north_green: int = 30
    south_green: int = 30
    east_green: int = 30
    west_green: int = 30
    cycle_time: int = 120
    
    def get_green_time(self, direction: Direction) -> int:
        return getattr(self, f"{direction.value}_green")
    
    def set_green_time(self, direction: Direction, green_time: int):
        setattr(self, f"{direction.value}_green", green_time)
        # Ensure total doesn't exceed cycle time
        total = self.north_green + self.south_green + self.east_green + self.west_green
        if total > self.cycle_time:
            # Proportionally reduce other directions
            excess = total - self.cycle_time
            other_directions = [d for d in Direction if d != direction]
            for other_dir in other_directions:
                current = getattr(self, f"{other_dir.value}_green")
                reduction = min(current, excess // len(other_directions))
                setattr(self, f"{other_dir.value}_green", current - reduction)
                excess -= reduction

@dataclass
class FlowDirection:
    """Bidirectional flow for a segment"""
    forward_flow: float = 0.0  # vehicles/hour
    backward_flow: float = 0.0  # vehicles/hour
    forward_capacity: float = 1000.0
    backward_capacity: float = 1000.0
    forward_queue: float = 0.0
    backward_queue: float = 0.0
    
    def get_total_flow(self) -> float:
        return self.forward_flow + self.backward_flow
    
    def get_total_capacity(self) -> float:
        return self.forward_capacity + self.backward_capacity
    
    def get_utilization(self) -> float:
        total_capacity = self.get_total_capacity()
        if total_capacity == 0:
            return 0.0
        return min(100.0, (self.get_total_flow() / total_capacity) * 100)
    
    def get_congestion_level(self) -> str:
        utilization = self.get_utilization()
        if utilization < 60:
            return "green"
        elif utilization < 80:
            return "yellow"
        else:
            return "red"

@dataclass
class Node:
    """Graph node representing an intersection, merge, or split"""
    id: str
    name: str
    node_type: NodeType
    x: float  # Position for visualization
    y: float
    traffic_light: Optional[TrafficLight] = None
    connected_segments: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.node_type == NodeType.INTERSECTION and self.traffic_light is None:
            self.traffic_light = TrafficLight()

@dataclass
class Segment:
    """Graph edge representing a road segment"""
    id: str
    name: str
    segment_type: SegmentType
    from_node: str
    to_node: str
    flow: FlowDirection = field(default_factory=FlowDirection)
    length: float = 1000.0  # meters
    speed_limit: float = 50.0  # km/h
    police_control: bool = False
    police_reduction: float = 0.3  # 30% flow reduction when police present
    traffic_light: Optional[TrafficLight] = None  # Mid-segment traffic light
    
    def get_travel_time(self) -> float:
        """Get travel time in minutes"""
        return (self.length / 1000.0) / (self.speed_limit / 60.0)
    
    def apply_police_effect(self, base_flow: float) -> float:
        """Apply police control effect to flow"""
        if self.police_control:
            return base_flow * (1.0 - self.police_reduction)
        return base_flow

class GraphTrafficSimulation:
    """Graph-based traffic simulation engine"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.segments: Dict[str, Segment] = {}
        self.simulation_running = False
        self.simulation_time = "08:00"
        self.time_minutes = 480  # 8 AM
        self.last_update = time.time()
        
    def add_node(self, node: Node):
        """Add a node to the graph"""
        self.nodes[node.id] = node
        
    def add_segment(self, segment: Segment):
        """Add a segment to the graph"""
        self.segments[segment.id] = segment
        
        # Update connected nodes
        if segment.from_node in self.nodes:
            if segment.id not in self.nodes[segment.from_node].connected_segments:
                self.nodes[segment.from_node].connected_segments.append(segment.id)
        
        if segment.to_node in self.nodes:
            if segment.id not in self.nodes[segment.to_node].connected_segments:
                self.nodes[segment.to_node].connected_segments.append(segment.id)
    
    def get_time_demand_factor(self) -> float:
        """Get demand multiplier based on time of day"""
        hour = self.time_minutes // 60
        
        # Time-based demand patterns
        if 6 <= hour <= 9:  # Morning rush
            return 1.8
        elif 11 <= hour <= 13:  # Lunch
            return 1.3
        elif 17 <= hour <= 19:  # Evening rush
            return 2.0
        elif 22 <= hour or hour <= 5:  # Night
            return 0.3
        else:  # Regular hours
            return 1.0
    
    def calculate_intersection_flow(self, node_id: str) -> Dict[str, float]:
        """Calculate flow distribution at an intersection"""
        if node_id not in self.nodes:
            return {}
        
        node = self.nodes[node_id]
        if node.node_type != NodeType.INTERSECTION or not node.traffic_light:
            return {}
        
        # Get connected segments
        connected_segments = [self.segments[seg_id] for seg_id in node.connected_segments 
                            if seg_id in self.segments]
        
        flow_distribution = {}
        demand_factor = self.get_time_demand_factor()
        
        for segment in connected_segments:
            # Determine direction based on segment connection to node
            if segment.from_node == node_id:
                # Outgoing segment - flow affected by traffic light
                direction = self._get_segment_direction(segment, node)
                green_time = node.traffic_light.get_green_time(direction)
                
                # Base flow calculation
                base_flow = (segment.flow.forward_capacity * 0.7 * demand_factor * 
                           (green_time / node.traffic_light.cycle_time))
                
                # Apply police effect
                actual_flow = segment.apply_police_effect(base_flow)
                flow_distribution[segment.id] = actual_flow
                
            elif segment.to_node == node_id:
                # Incoming segment - contributes to intersection demand
                base_flow = segment.flow.forward_capacity * 0.6 * demand_factor
                actual_flow = segment.apply_police_effect(base_flow)
                flow_distribution[segment.id] = actual_flow
        
        return flow_distribution
    
    def calculate_merge_flow(self, node_id: str) -> Dict[str, float]:
        """Calculate flow at a merge point"""
        if node_id not in self.nodes:
            return {}
        
        node = self.nodes[node_id]
        if node.node_type != NodeType.MERGE:
            return {}
        
        connected_segments = [self.segments[seg_id] for seg_id in node.connected_segments 
                            if seg_id in self.segments]
        
        # Find incoming and outgoing segments
        incoming_segments = [s for s in connected_segments if s.to_node == node_id]
        outgoing_segments = [s for s in connected_segments if s.from_node == node_id]
        
        flow_distribution = {}
        demand_factor = self.get_time_demand_factor()
        
        # Calculate total incoming flow
        total_incoming = sum(s.flow.forward_capacity * 0.6 * demand_factor 
                           for s in incoming_segments)
        
        # Distribute to outgoing segments based on capacity
        total_outgoing_capacity = sum(s.flow.forward_capacity for s in outgoing_segments)
        
        for segment in outgoing_segments:
            if total_outgoing_capacity > 0:
                flow_ratio = segment.flow.forward_capacity / total_outgoing_capacity
                base_flow = min(total_incoming * flow_ratio, 
                              segment.flow.forward_capacity * 0.8)
                actual_flow = segment.apply_police_effect(base_flow)
                flow_distribution[segment.id] = actual_flow
        
        # Update incoming segments
        for segment in incoming_segments:
            base_flow = segment.flow.forward_capacity * 0.6 * demand_factor
            actual_flow = segment.apply_police_effect(base_flow)
            flow_distribution[segment.id] = actual_flow
        
        return flow_distribution
    
    def calculate_split_flow(self, node_id: str) -> Dict[str, float]:
        """Calculate flow at a split point"""
        if node_id not in self.nodes:
            return {}
        
        node = self.nodes[node_id]
        if node.node_type != NodeType.SPLIT:
            return {}
        
        connected_segments = [self.segments[seg_id] for seg_id in node.connected_segments 
                            if seg_id in self.segments]
        
        # Find incoming and outgoing segments
        incoming_segments = [s for s in connected_segments if s.to_node == node_id]
        outgoing_segments = [s for s in connected_segments if s.from_node == node_id]
        
        flow_distribution = {}
        demand_factor = self.get_time_demand_factor()
        
        # Calculate total incoming flow
        total_incoming = sum(s.flow.forward_capacity * 0.7 * demand_factor 
                           for s in incoming_segments)
        
        # Split flow among outgoing segments (equal distribution for simplicity)
        if outgoing_segments:
            flow_per_branch = total_incoming / len(outgoing_segments)
            
            for segment in outgoing_segments:
                base_flow = min(flow_per_branch, segment.flow.forward_capacity * 0.8)
                actual_flow = segment.apply_police_effect(base_flow)
                flow_distribution[segment.id] = actual_flow
        
        # Update incoming segments
        for segment in incoming_segments:
            base_flow = segment.flow.forward_capacity * 0.7 * demand_factor
            actual_flow = segment.apply_police_effect(base_flow)
            flow_distribution[segment.id] = actual_flow
        
        return flow_distribution
    
    def _get_segment_direction(self, segment: Segment, node: Node) -> Direction:
        """Determine the direction of a segment relative to a node"""
        # Simple heuristic based on segment name or position
        # In a real implementation, this would use actual coordinates
        segment_name = segment.name.lower()
        
        if 'north' in segment_name or 'n-s' in segment_name:
            return Direction.NORTH
        elif 'south' in segment_name:
            return Direction.SOUTH
        elif 'east' in segment_name or 'e-w' in segment_name:
            return Direction.EAST
        elif 'west' in segment_name:
            return Direction.WEST
        else:
            # Default based on segment ID hash
            return list(Direction)[hash(segment.id) % 4]
    
    def update_flows(self):
        """Update all segment flows based on connected calculations"""
        # Calculate flows for each node type
        all_flows = {}
        
        for node_id, node in self.nodes.items():
            if node.node_type == NodeType.INTERSECTION:
                flows = self.calculate_intersection_flow(node_id)
            elif node.node_type == NodeType.MERGE:
                flows = self.calculate_merge_flow(node_id)
            elif node.node_type == NodeType.SPLIT:
                flows = self.calculate_split_flow(node_id)
            else:
                continue
            
            all_flows.update(flows)
        
        # Apply calculated flows to segments
        for segment_id, flow_value in all_flows.items():
            if segment_id in self.segments:
                segment = self.segments[segment_id]
                segment.flow.forward_flow = flow_value
                
                # Calculate backward flow (typically lower)
                segment.flow.backward_flow = flow_value * 0.6
                
                # Update queues based on capacity constraints
                if segment.flow.forward_flow > segment.flow.forward_capacity:
                    segment.flow.forward_queue += (segment.flow.forward_flow - 
                                                 segment.flow.forward_capacity) * 0.1
                else:
                    segment.flow.forward_queue = max(0, segment.flow.forward_queue - 10)
                
                if segment.flow.backward_flow > segment.flow.backward_capacity:
                    segment.flow.backward_queue += (segment.flow.backward_flow - 
                                                  segment.flow.backward_capacity) * 0.1
                else:
                    segment.flow.backward_queue = max(0, segment.flow.backward_queue - 10)
    
    def adjust_intersection_green_time(self, node_id: str, direction: Direction, 
                                     green_time: int) -> bool:
        """Adjust green time for a specific direction at an intersection"""
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        if node.node_type != NodeType.INTERSECTION or not node.traffic_light:
            return False
        
        node.traffic_light.set_green_time(direction, green_time)
        self.update_flows()
        return True
    
    def toggle_police_control(self, segment_id: str, enabled: bool, 
                            reduction: float = 0.3) -> bool:
        """Toggle police control on a segment"""
        if segment_id not in self.segments:
            return False
        
        segment = self.segments[segment_id]
        segment.police_control = enabled
        segment.police_reduction = reduction
        self.update_flows()
        return True
    
    def add_segment_traffic_light(self, segment_id: str, 
                                traffic_light: TrafficLight) -> bool:
        """Add traffic light to a segment"""
        if segment_id not in self.segments:
            return False
        
        self.segments[segment_id].traffic_light = traffic_light
        self.update_flows()
        return True
    
    def set_time(self, time_minutes: int):
        """Set simulation time"""
        self.time_minutes = time_minutes
        hours = time_minutes // 60
        minutes = time_minutes % 60
        self.simulation_time = f"{hours:02d}:{minutes:02d}"
        self.update_flows()
    
    def start_simulation(self):
        """Start the simulation"""
        self.simulation_running = True
        self.last_update = time.time()
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status"""
        # Update flows if simulation is running
        if self.simulation_running:
            current_time = time.time()
            if current_time - self.last_update > 2:  # Update every 2 seconds
                self.time_minutes += 1
                if self.time_minutes >= 1440:  # Reset at midnight
                    self.time_minutes = 0
                
                hours = self.time_minutes // 60
                minutes = self.time_minutes % 60
                self.simulation_time = f"{hours:02d}:{minutes:02d}"
                
                self.update_flows()
                self.last_update = current_time
        
        # Count congestion levels
        high_congestion = sum(1 for s in self.segments.values() 
                            if s.flow.get_congestion_level() == "red")
        medium_congestion = sum(1 for s in self.segments.values() 
                              if s.flow.get_congestion_level() == "yellow")
        
        # Prepare segment data
        segments_data = {}
        for seg_id, segment in self.segments.items():
            segments_data[seg_id] = {
                "id": seg_id,
                "name": segment.name,
                "segment_type": segment.segment_type.value,
                "from_node": segment.from_node,
                "to_node": segment.to_node,
                "forward_flow": round(segment.flow.forward_flow, 1),
                "backward_flow": round(segment.flow.backward_flow, 1),
                "total_flow": round(segment.flow.get_total_flow(), 1),
                "forward_capacity": segment.flow.forward_capacity,
                "backward_capacity": segment.flow.backward_capacity,
                "total_capacity": segment.flow.get_total_capacity(),
                "utilization_percent": round(segment.flow.get_utilization(), 1),
                "congestion_level": segment.flow.get_congestion_level(),
                "forward_queue": round(segment.flow.forward_queue, 1),
                "backward_queue": round(segment.flow.backward_queue, 1),
                "police_control": segment.police_control,
                "has_traffic_light": segment.traffic_light is not None,
                "length": segment.length,
                "speed_limit": segment.speed_limit
            }
        
        # Prepare node data
        nodes_data = {}
        for node_id, node in self.nodes.items():
            node_data = {
                "id": node_id,
                "name": node.name,
                "node_type": node.node_type.value,
                "x": node.x,
                "y": node.y,
                "connected_segments": node.connected_segments
            }
            
            if node.traffic_light:
                node_data["traffic_light"] = {
                    "north_green": node.traffic_light.north_green,
                    "south_green": node.traffic_light.south_green,
                    "east_green": node.traffic_light.east_green,
                    "west_green": node.traffic_light.west_green,
                    "cycle_time": node.traffic_light.cycle_time
                }
            
            nodes_data[node_id] = node_data
        
        return {
            "simulation_running": self.simulation_running,
            "simulation_time": self.simulation_time,
            "time_minutes": self.time_minutes,
            "total_nodes": len(self.nodes),
            "total_segments": len(self.segments),
            "high_congestion": high_congestion,
            "medium_congestion": medium_congestion,
            "nodes": nodes_data,
            "segments": segments_data
        }