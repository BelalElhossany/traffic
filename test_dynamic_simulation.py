#!/usr/bin/env python3
"""
Test script for dynamic traffic simulation
"""
import requests
import json
import time

API_BASE = "https://work-1-prrnhxygajyxxmlp.prod-runtime.all-hands.dev/api/traffic"

def create_test_network():
    """Create a simple test network"""
    return {
        "segments": {
            "times_square_broadway": {
                "id": "times_square_broadway",
                "name": "Times Square - Broadway",
                "segment_type": "intersection",
                "capacity": 1800,
                "current_queue": 45.2,
                "current_flow": 1620,
                "green_time_seconds": 45,
                "police_control": False,
                "weather_factor": 1.0,
                "length": 100.0,
                "coordinates": [[40.7580, -73.9855]]
            },
            "herald_square_34th": {
                "id": "herald_square_34th",
                "name": "Herald Square - 34th St",
                "segment_type": "intersection", 
                "capacity": 1600,
                "current_queue": 32.1,
                "current_flow": 1440,
                "green_time_seconds": 40,
                "police_control": False,
                "weather_factor": 1.0,
                "length": 120.0,
                "coordinates": [[40.7505, -73.9934]]
            },
            "union_square_14th": {
                "id": "union_square_14th",
                "name": "Union Square - 14th St",
                "segment_type": "intersection",
                "capacity": 1500,
                "current_queue": 28.5,
                "current_flow": 1200,
                "green_time_seconds": 35,
                "police_control": False,
                "weather_factor": 1.0,
                "length": 90.0,
                "coordinates": [[40.7359, -73.9911]]
            }
        },
        "connections": {
            "times_square_broadway": ["herald_square_34th"],
            "herald_square_34th": ["times_square_broadway", "union_square_14th"],
            "union_square_14th": ["herald_square_34th"]
        }
    }

def test_dynamic_simulation():
    """Test the dynamic simulation functionality"""
    print("🚦 Testing Dynamic Traffic Simulation")
    print("=" * 50)
    
    # 1. Check health
    print("1. Checking API health...")
    response = requests.get(f"{API_BASE}/health")
    health = response.json()
    print(f"   Status: {health['status']}")
    print(f"   Network initialized: {health['network_initialized']}")
    print(f"   Dynamic simulation running: {health['dynamic_simulation_running']}")
    
    # 2. Initialize network
    print("\n2. Initializing network...")
    network = create_test_network()
    response = requests.post(f"{API_BASE}/network/initialize", json=network)
    if response.status_code == 200:
        print("   ✅ Network initialized successfully")
    else:
        print(f"   ❌ Network initialization failed: {response.text}")
        return
    
    # 3. Check network status
    print("\n3. Checking network status...")
    response = requests.get(f"{API_BASE}/network/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Total segments: {len(status)}")
        for seg_id, seg_status in status.items():
            print(f"   - {seg_status['name']}: Queue={seg_status['current_queue']:.1f}, Flow={seg_status['current_flow']:.1f}")
    
    # 4. Start dynamic simulation
    print("\n4. Starting dynamic simulation...")
    response = requests.post(f"{API_BASE}/simulation/start-dynamic")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ Failed to start simulation: {response.text}")
        return
    
    # 5. Monitor simulation for 60 seconds
    print("\n5. Monitoring simulation for 60 seconds...")
    for i in range(12):  # 12 iterations of 5 seconds each
        time.sleep(5)
        
        # Get simulation status
        response = requests.get(f"{API_BASE}/simulation/status")
        if response.status_code == 200:
            sim_status = response.json()
            print(f"   Time {i*5:2d}s: Sim time {sim_status['simulation_time_formatted']} (Hour {sim_status['current_hour']})")
        
        # Get live network status
        response = requests.get(f"{API_BASE}/network/live-status")
        if response.status_code == 200:
            live_status = response.json()
            print(f"           High congestion segments: {live_status['high_congestion_count']}/{live_status['total_segments']}")
            
            # Show a few segments with their changing values
            segments = live_status['segments']
            for seg_id in list(segments.keys())[:2]:  # Show first 2 segments
                seg = segments[seg_id]
                print(f"           {seg['name']}: Queue={seg['current_queue']:.1f}, Flow={seg['current_flow']:.1f}, Util={seg['utilization_percent']:.1f}%")
        
        print()
    
    # 6. Stop simulation
    print("6. Stopping dynamic simulation...")
    response = requests.post(f"{API_BASE}/simulation/stop-dynamic")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")
    
    print("\n🎉 Dynamic simulation test completed!")

if __name__ == "__main__":
    test_dynamic_simulation()