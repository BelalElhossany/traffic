from fastapi import APIRouter, HTTPException
from typing import List, Dict
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

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "network_initialized": current_network is not None,
        "engines_ready": all([simulation_engine, prediction_engine, ai_optimizer])
    }