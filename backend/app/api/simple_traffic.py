"""
Simple traffic simulation API with realistic intersection logic
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..services.simple_simulation import simple_simulation

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "simulation_running": simple_simulation.is_running,
        "segments_count": len(simple_simulation.segments)
    }

@router.post("/initialize")
async def initialize_network(segments: List[Dict]):
    """Initialize the traffic network with simple segments"""
    try:
        success = simple_simulation.initialize_network(segments)
        if success:
            return {"status": "success", "message": "Network initialized successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to initialize network")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Get current traffic status"""
    try:
        return simple_simulation.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_simulation():
    """Start the dynamic simulation"""
    try:
        success = simple_simulation.start_simulation()
        if success:
            return {"status": "success", "message": "Simulation started"}
        else:
            return {"status": "info", "message": "Simulation already running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_simulation():
    """Stop the dynamic simulation"""
    try:
        success = simple_simulation.stop_simulation()
        if success:
            return {"status": "success", "message": "Simulation stopped"}
        else:
            return {"status": "info", "message": "Simulation not running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adjust-green-time")
async def adjust_green_time(segment_id: str, green_time: int):
    """Adjust green time for a traffic segment"""
    try:
        success = simple_simulation.adjust_green_time(segment_id, green_time)
        if success:
            return {
                "status": "success", 
                "message": f"Green time adjusted for {segment_id}",
                "new_status": simple_simulation.get_status()
            }
        else:
            raise HTTPException(status_code=404, detail="Segment not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-time")
async def set_time(time_minutes: int):
    """Set simulation time for testing different periods"""
    try:
        simple_simulation.set_time(time_minutes)
        return {
            "status": "success",
            "message": f"Time set to {time_minutes // 60:02d}:{time_minutes % 60:02d}",
            "new_status": simple_simulation.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))