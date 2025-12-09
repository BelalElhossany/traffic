#!/usr/bin/env python3
"""
Test script to verify time-based traffic patterns
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
                "current_queue": 10.0,
                "current_flow": 720,  # Start with lower flow
                "green_time_seconds": 45,
                "police_control": False,
                "weather_factor": 1.0,
                "length": 100.0,
                "coordinates": [[40.7580, -73.9855]]
            },
            "lincoln_tunnel_entrance": {
                "id": "lincoln_tunnel_entrance",
                "name": "Lincoln Tunnel Entrance",
                "segment_type": "road", 
                "capacity": 2000,
                "current_queue": 15.0,
                "current_flow": 800,
                "green_time_seconds": 60,
                "police_control": False,
                "weather_factor": 1.0,
                "length": 200.0,
                "coordinates": [[40.7614, -74.0055]]
            }
        },
        "connections": {
            "times_square_broadway": ["lincoln_tunnel_entrance"],
            "lincoln_tunnel_entrance": ["times_square_broadway"]
        }
    }

def test_time_patterns():
    """Test traffic patterns over different simulated hours"""
    print("🕐 Testing Time-Based Traffic Patterns")
    print("=" * 50)
    
    # Initialize network
    print("Initializing network...")
    network = create_test_network()
    response = requests.post(f"{API_BASE}/network/initialize", json=network)
    if response.status_code != 200:
        print(f"❌ Network initialization failed: {response.text}")
        return
    
    # Start dynamic simulation
    print("Starting dynamic simulation...")
    response = requests.post(f"{API_BASE}/simulation/start-dynamic")
    if response.status_code != 200:
        print(f"❌ Failed to start simulation: {response.text}")
        return
    
    print("\nMonitoring traffic patterns over simulated time...")
    print("Time    | Hour | Times Square Flow | Lincoln Tunnel Flow | Pattern")
    print("-" * 80)
    
    # Monitor for different time periods to see patterns
    for i in range(20):  # 20 iterations of 3 seconds each
        time.sleep(3)
        
        # Get simulation status
        response = requests.get(f"{API_BASE}/simulation/status")
        if response.status_code == 200:
            sim_status = response.json()
            sim_time = sim_status['simulation_time_formatted']
            current_hour = sim_status['current_hour']
        else:
            continue
        
        # Get live network status
        response = requests.get(f"{API_BASE}/network/live-status")
        if response.status_code == 200:
            live_status = response.json()
            segments = live_status['segments']
            
            times_square_flow = segments.get('times_square_broadway', {}).get('current_flow', 0)
            lincoln_flow = segments.get('lincoln_tunnel_entrance', {}).get('current_flow', 0)
            
            # Determine pattern based on hour
            if 7 <= current_hour <= 9:
                pattern = "Morning Rush"
            elif 17 <= current_hour <= 19:
                pattern = "Evening Rush"
            elif 11 <= current_hour <= 14:
                pattern = "Lunch Time"
            elif 0 <= current_hour <= 6:
                pattern = "Night/Early"
            else:
                pattern = "Regular"
            
            print(f"{sim_time:7s} | {current_hour:4d} | {times_square_flow:15.0f} | {lincoln_flow:17.0f} | {pattern}")
    
    # Stop simulation
    print("\nStopping simulation...")
    requests.post(f"{API_BASE}/simulation/stop-dynamic")
    print("✅ Test completed!")

if __name__ == "__main__":
    test_time_patterns()