from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict
import asyncio
import time
import threading
from ..models.traffic import (
    TrafficNetwork, TrafficSegment, TrafficAction, SimulationResult,
    PredictionResult, AIRecommendation, SimulationScenario
)
from ..services.simulation_engine import TrafficSimulationEngine
from ..services.prediction_engine import TrafficPredictionEngine
from ..services.ai_optimizer import AITrafficOptimizer

router = APIRouter()

# Global network instance (in production, this would be managed differently)
current_network: TrafficNetwork = None
simulation_engine: TrafficSimulationEngine = None
prediction_engine: TrafficPredictionEngine = None
ai_optimizer: AITrafficOptimizer = None

# Dynamic simulation state
simulation_running = False
simulation_thread = None
simulation_time = 0  # Current simulation time in minutes

def dynamic_simulation_loop():
    """Background thread that continuously updates traffic simulation."""
    global simulation_running, simulation_time
    
    while simulation_running:
        if simulation_engine and current_network:
            try:
                # Update traffic flows every 30 seconds (0.5 minutes)
                simulation_engine.simulate_step(int(simulation_time))
                simulation_time += 0.5
                
                # Reset time every 24 hours (1440 minutes) to simulate daily cycles
                if simulation_time >= 1440:
                    simulation_time = 0
                    
            except Exception as e:
                print(f"Error in dynamic simulation: {e}")
        
        time.sleep(30)  # Update every 30 seconds

@router.post("/network/initialize")
async def initialize_network(network: TrafficNetwork):
    """Initialize the traffic network."""
    global current_network, simulation_engine, prediction_engine, ai_optimizer
    
    current_network = network
    simulation_engine = TrafficSimulationEngine(network)
    prediction_engine = TrafficPredictionEngine(network)
    ai_optimizer = AITrafficOptimizer(network)
    
    return {"message": "Network initialized successfully", "segments": len(network.segments)}

@router.get("/network/status")
async def get_network_status():
    """Get current network status."""
    if not current_network:
        raise HTTPException(status_code=404, detail="Network not initialized")
    
    status = {}
    for segment_id, segment in current_network.segments.items():
        status[segment_id] = {
            "name": segment.name,
            "current_queue": segment.current_queue,
            "current_flow": segment.current_flow,
            "capacity": current_network.get_effective_capacity(segment_id),
            "congestion_level": simulation_engine.get_congestion_level(segment_id) if simulation_engine else "unknown"
        }
    
    return status

@router.post("/simulation/run")
async def run_simulation(scenario: SimulationScenario) -> SimulationResult:
    """Run traffic simulation with specified actions."""
    if not simulation_engine:
        raise HTTPException(status_code=404, detail="Simulation engine not initialized")
    
    try:
        result = simulation_engine.run_simulation(
            duration_minutes=scenario.duration_minutes,
            actions=scenario.actions
        )
        result.scenario_name = scenario.name
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/prediction/forecast")
async def forecast_congestion(duration_minutes: int = 60) -> PredictionResult:
    """Predict traffic congestion for the next 30-60 minutes."""
    if not prediction_engine:
        raise HTTPException(status_code=404, detail="Prediction engine not initialized")
    
    try:
        result = prediction_engine.predict_congestion(duration_minutes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/prediction/forecast-with-actions")
async def forecast_with_actions(actions: List[TrafficAction], duration_minutes: int = 60) -> PredictionResult:
    """Predict traffic congestion with specific actions applied."""
    if not prediction_engine:
        raise HTTPException(status_code=404, detail="Prediction engine not initialized")
    
    try:
        result = prediction_engine.predict_with_actions(actions, duration_minutes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction with actions failed: {str(e)}")

@router.post("/ai/recommend")
async def get_ai_recommendations(duration_minutes: int = 60) -> AIRecommendation:
    """Get AI-powered traffic control recommendations."""
    if not ai_optimizer:
        raise HTTPException(status_code=404, detail="AI optimizer not initialized")
    
    try:
        recommendation = ai_optimizer.optimize_traffic_actions(duration_minutes)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {str(e)}")

@router.post("/actions/apply")
async def apply_actions(actions: List[TrafficAction]):
    """Apply traffic control actions to the network."""
    if not simulation_engine:
        raise HTTPException(status_code=404, detail="Simulation engine not initialized")
    
    try:
        simulation_engine.apply_actions(actions)
        return {"message": f"Applied {len(actions)} actions successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply actions: {str(e)}")

@router.post("/actions/reset")
async def reset_actions():
    """Reset all traffic control actions to default state."""
    if not simulation_engine:
        raise HTTPException(status_code=404, detail="Simulation engine not initialized")
    
    try:
        simulation_engine.reset_actions()
        return {"message": "All actions reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset actions: {str(e)}")

@router.get("/segments/{segment_id}")
async def get_segment_details(segment_id: str):
    """Get detailed information about a specific segment."""
    if not current_network or segment_id not in current_network.segments:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    segment = current_network.segments[segment_id]
    effective_capacity = current_network.get_effective_capacity(segment_id)
    congestion_level = simulation_engine.get_congestion_level(segment_id) if simulation_engine else "unknown"
    
    return {
        "segment": segment,
        "effective_capacity": effective_capacity,
        "congestion_level": congestion_level
    }

@router.post("/segments/{segment_id}/green-time")
async def adjust_green_time(segment_id: str, adjustment_seconds: float):
    """Adjust green time for a specific intersection."""
    if not current_network or segment_id not in current_network.segments:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    segment = current_network.segments[segment_id]
    if segment.segment_type.value != "intersection":
        raise HTTPException(status_code=400, detail="Green time can only be adjusted for intersections")
    
    segment.green_time_adjustment = adjustment_seconds
    return {"message": f"Green time adjusted by {adjustment_seconds} seconds for {segment.name}"}

@router.post("/segments/{segment_id}/police-control")
async def toggle_police_control(segment_id: str, enable: bool, reduction_factor: float = 0.5):
    """Toggle police flow control for a specific segment."""
    if not current_network or segment_id not in current_network.segments:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    segment = current_network.segments[segment_id]
    segment.police_control = enable
    if enable:
        segment.police_reduction = reduction_factor
    
    action = "enabled" if enable else "disabled"
    return {"message": f"Police control {action} for {segment.name}"}

@router.post("/simulation/start-dynamic")
async def start_dynamic_simulation():
    """Start continuous dynamic traffic simulation."""
    global simulation_running, simulation_thread
    
    if not simulation_engine:
        raise HTTPException(status_code=404, detail="Simulation engine not initialized")
    
    if simulation_running:
        return {"message": "Dynamic simulation already running"}
    
    simulation_running = True
    simulation_thread = threading.Thread(target=dynamic_simulation_loop, daemon=True)
    simulation_thread.start()
    
    return {"message": "Dynamic simulation started"}

@router.post("/simulation/stop-dynamic")
async def stop_dynamic_simulation():
    """Stop continuous dynamic traffic simulation."""
    global simulation_running
    
    simulation_running = False
    return {"message": "Dynamic simulation stopped"}

@router.get("/simulation/status")
async def get_simulation_status():
    """Get current simulation status and time."""
    return {
        "running": simulation_running,
        "simulation_time_minutes": simulation_time,
        "simulation_time_formatted": f"{int(simulation_time // 60):02d}:{int(simulation_time % 60):02d}",
        "current_hour": int(simulation_time // 60) % 24
    }

@router.post("/simulation/set-time")
async def set_simulation_time(time_minutes: int):
    """Set the current simulation time (for testing purposes)."""
    global simulation_time
    simulation_time = time_minutes % 1440  # Keep within 24 hours
    return {
        "message": f"Simulation time set to {simulation_time} minutes",
        "simulation_time_formatted": f"{int(simulation_time // 60):02d}:{int(simulation_time % 60):02d}",
        "current_hour": int(simulation_time // 60) % 24
    }

@router.get("/network/live-status")
async def get_live_network_status():
    """Get current network status with real-time traffic data."""
    if not current_network:
        raise HTTPException(status_code=404, detail="Network not initialized")
    
    status = {}
    current_hour = int(simulation_time // 60) % 24
    
    for segment_id, segment in current_network.segments.items():
        congestion_level = simulation_engine.get_congestion_level(segment_id) if simulation_engine else "unknown"
        effective_capacity = current_network.get_effective_capacity(segment_id)
        
        # Calculate utilization percentage
        utilization = (segment.current_flow / effective_capacity * 100) if effective_capacity > 0 else 0
        
        status[segment_id] = {
            "name": segment.name,
            "current_queue": round(segment.current_queue, 1),
            "current_flow": round(segment.current_flow, 1),
            "capacity": effective_capacity,
            "utilization_percent": round(utilization, 1),
            "congestion_level": congestion_level,
            "segment_type": segment.segment_type.value,
            "police_control": segment.police_control,
            "weather_factor": segment.weather_factor
        }
    
    return {
        "segments": status,
        "simulation_time": simulation_time,
        "current_hour": current_hour,
        "total_segments": len(status),
        "high_congestion_count": sum(1 for s in status.values() if s["utilization_percent"] > 80)
    }

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "network_initialized": current_network is not None,
        "engines_ready": all([simulation_engine, prediction_engine, ai_optimizer]),
        "dynamic_simulation_running": simulation_running
    }