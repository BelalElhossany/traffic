"""
API endpoints for graph-based traffic simulation
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from ..services.graph_simulation import (
    GraphTrafficSimulation, Node, Segment, NodeType, SegmentType, 
    Direction, TrafficLight, FlowDirection
)

router = APIRouter()

# Global simulation instance
graph_simulation = GraphTrafficSimulation()

class NodeCreate(BaseModel):
    id: str
    name: str
    node_type: str  # "intersection", "merge", "split"
    x: float
    y: float

class SegmentCreate(BaseModel):
    id: str
    name: str
    segment_type: str  # "road", "highway", "arterial"
    from_node: str
    to_node: str
    forward_capacity: float = 1000.0
    backward_capacity: float = 1000.0
    length: float = 1000.0
    speed_limit: float = 50.0

class TrafficLightCreate(BaseModel):
    north_green: int = 30
    south_green: int = 30
    east_green: int = 30
    west_green: int = 30
    cycle_time: int = 120

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "simulation_running": graph_simulation.simulation_running,
        "nodes_count": len(graph_simulation.nodes),
        "segments_count": len(graph_simulation.segments)
    }

@router.post("/initialize")
async def initialize_network(network_data: Dict[str, Any]):
    """Initialize the traffic network with nodes and segments"""
    try:
        # Clear existing network
        graph_simulation.nodes.clear()
        graph_simulation.segments.clear()
        
        # Add nodes
        if "nodes" in network_data:
            for node_data in network_data["nodes"]:
                try:
                    node_type = NodeType(node_data["node_type"])
                except ValueError:
                    raise HTTPException(status_code=400, 
                                      detail=f"Invalid node type: {node_data['node_type']}")
                
                node = Node(
                    id=node_data["id"],
                    name=node_data["name"],
                    node_type=node_type,
                    x=node_data["x"],
                    y=node_data["y"]
                )
                graph_simulation.add_node(node)
        
        # Add segments
        if "segments" in network_data:
            for segment_data in network_data["segments"]:
                try:
                    segment_type = SegmentType(segment_data["segment_type"])
                except ValueError:
                    raise HTTPException(status_code=400, 
                                      detail=f"Invalid segment type: {segment_data['segment_type']}")
                
                flow = FlowDirection(
                    forward_capacity=segment_data.get("forward_capacity", 1000.0),
                    backward_capacity=segment_data.get("backward_capacity", 1000.0)
                )
                
                segment = Segment(
                    id=segment_data["id"],
                    name=segment_data["name"],
                    segment_type=segment_type,
                    from_node=segment_data["from_node"],
                    to_node=segment_data["to_node"],
                    flow=flow,
                    length=segment_data.get("length", 1000.0),
                    speed_limit=segment_data.get("speed_limit", 50.0)
                )
                graph_simulation.add_segment(segment)
        
        # Initial flow calculation
        graph_simulation.update_flows()
        
        return {"status": "success", "message": "Network initialized successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize network: {str(e)}")

@router.get("/status")
async def get_status():
    """Get current simulation status"""
    return graph_simulation.get_status()

@router.post("/start")
async def start_simulation():
    """Start the simulation"""
    graph_simulation.start_simulation()
    return {"status": "success", "message": "Simulation started"}

@router.post("/stop")
async def stop_simulation():
    """Stop the simulation"""
    graph_simulation.stop_simulation()
    return {"status": "success", "message": "Simulation stopped"}

@router.post("/set-time")
async def set_time(time_minutes: int = Query(..., description="Time in minutes from midnight")):
    """Set simulation time"""
    if not (0 <= time_minutes < 1440):
        raise HTTPException(status_code=400, detail="Time must be between 0 and 1439 minutes")
    
    graph_simulation.set_time(time_minutes)
    return {
        "status": "success",
        "message": f"Time set to {graph_simulation.simulation_time}",
        "new_status": graph_simulation.get_status()
    }

@router.post("/adjust-intersection-green-time")
async def adjust_intersection_green_time(
    node_id: str = Query(..., description="Node ID"),
    direction: str = Query(..., description="Direction: north, south, east, west"),
    green_time: int = Query(..., description="Green time in seconds")
):
    """Adjust green time for a specific direction at an intersection"""
    if green_time < 5 or green_time > 90:
        raise HTTPException(status_code=400, detail="Green time must be between 5 and 90 seconds")
    
    try:
        direction_enum = Direction(direction.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid direction. Use: north, south, east, west")
    
    success = graph_simulation.adjust_intersection_green_time(node_id, direction_enum, green_time)
    
    if not success:
        raise HTTPException(status_code=404, detail="Node not found or not an intersection")
    
    return {
        "status": "success",
        "message": f"Green time adjusted for {direction} direction at {node_id}",
        "new_status": graph_simulation.get_status()
    }

@router.post("/toggle-police-control")
async def toggle_police_control(
    segment_id: str = Query(..., description="Segment ID"),
    enabled: bool = Query(..., description="Enable or disable police control"),
    reduction: float = Query(0.3, description="Flow reduction factor (0.0-1.0)")
):
    """Toggle police control on a segment"""
    if not (0.0 <= reduction <= 1.0):
        raise HTTPException(status_code=400, detail="Reduction must be between 0.0 and 1.0")
    
    success = graph_simulation.toggle_police_control(segment_id, enabled, reduction)
    
    if not success:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    action = "enabled" if enabled else "disabled"
    return {
        "status": "success",
        "message": f"Police control {action} for segment {segment_id}",
        "new_status": graph_simulation.get_status()
    }

@router.post("/add-segment-traffic-light")
async def add_segment_traffic_light(
    traffic_light_data: TrafficLightCreate,
    segment_id: str = Query(..., description="Segment ID")
):
    """Add traffic light to a segment"""
    traffic_light = TrafficLight(
        north_green=traffic_light_data.north_green,
        south_green=traffic_light_data.south_green,
        east_green=traffic_light_data.east_green,
        west_green=traffic_light_data.west_green,
        cycle_time=traffic_light_data.cycle_time
    )
    
    success = graph_simulation.add_segment_traffic_light(segment_id, traffic_light)
    
    if not success:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    return {
        "status": "success",
        "message": f"Traffic light added to segment {segment_id}",
        "new_status": graph_simulation.get_status()
    }

@router.post("/adjust-segment-traffic-light")
async def adjust_segment_traffic_light(
    segment_id: str = Query(..., description="Segment ID"),
    direction: str = Query(..., description="Direction: north, south, east, west"),
    green_time: int = Query(..., description="Green time in seconds")
):
    """Adjust traffic light timing on a segment"""
    if green_time < 5 or green_time > 90:
        raise HTTPException(status_code=400, detail="Green time must be between 5 and 90 seconds")
    
    if segment_id not in graph_simulation.segments:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    segment = graph_simulation.segments[segment_id]
    if not segment.traffic_light:
        raise HTTPException(status_code=400, detail="Segment does not have a traffic light")
    
    try:
        direction_enum = Direction(direction.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid direction. Use: north, south, east, west")
    
    segment.traffic_light.set_green_time(direction_enum, green_time)
    graph_simulation.update_flows()
    
    return {
        "status": "success",
        "message": f"Traffic light adjusted for {direction} direction on segment {segment_id}",
        "new_status": graph_simulation.get_status()
    }

@router.get("/network-topology")
async def get_network_topology():
    """Get network topology for visualization"""
    nodes = []
    edges = []
    
    # Prepare nodes for visualization
    for node_id, node in graph_simulation.nodes.items():
        node_data = {
            "id": node_id,
            "name": node.name,
            "type": node.node_type.value,
            "x": node.x,
            "y": node.y,
            "connected_segments": len(node.connected_segments)
        }
        
        if node.traffic_light:
            node_data["has_traffic_light"] = True
            node_data["traffic_light"] = {
                "north": node.traffic_light.north_green,
                "south": node.traffic_light.south_green,
                "east": node.traffic_light.east_green,
                "west": node.traffic_light.west_green
            }
        
        nodes.append(node_data)
    
    # Prepare edges for visualization
    for segment_id, segment in graph_simulation.segments.items():
        edge_data = {
            "id": segment_id,
            "name": segment.name,
            "type": segment.segment_type.value,
            "source": segment.from_node,
            "target": segment.to_node,
            "forward_flow": segment.flow.forward_flow,
            "backward_flow": segment.flow.backward_flow,
            "total_flow": segment.flow.get_total_flow(),
            "capacity": segment.flow.get_total_capacity(),
            "utilization": segment.flow.get_utilization(),
            "congestion_level": segment.flow.get_congestion_level(),
            "police_control": segment.police_control,
            "has_traffic_light": segment.traffic_light is not None,
            "length": segment.length,
            "speed_limit": segment.speed_limit
        }
        
        edges.append(edge_data)
    
    return {
        "nodes": nodes,
        "edges": edges,
        "simulation_time": graph_simulation.simulation_time,
        "simulation_running": graph_simulation.simulation_running
    }