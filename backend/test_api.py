#!/usr/bin/env python3
"""
Test script to initialize the traffic network and test API endpoints.
"""

import asyncio
import httpx
from app.services.sample_network import create_sample_network

async def test_api():
    """Test the traffic API endpoints."""
    base_url = "http://localhost:12000"
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        print("Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"Health: {response.json()}")
        
        # Initialize network
        print("\nInitializing network...")
        network = create_sample_network()
        response = await client.post(
            f"{base_url}/api/traffic/network/initialize",
            json=network.model_dump()
        )
        print(f"Network initialization: {response.json()}")
        
        # Get network status
        print("\nGetting network status...")
        response = await client.get(f"{base_url}/api/traffic/network/status")
        status = response.json()
        print(f"Network has {len(status)} segments")
        
        # Test prediction
        print("\nTesting congestion prediction...")
        response = await client.post(f"{base_url}/api/traffic/prediction/forecast?duration_minutes=30")
        prediction = response.json()
        print(f"Prediction generated with {len(prediction['congestion_warnings'])} warnings")
        
        # Test AI recommendations
        print("\nTesting AI recommendations...")
        response = await client.post(f"{base_url}/api/traffic/ai/recommend?duration_minutes=30")
        recommendation = response.json()
        print(f"AI recommendation: {recommendation['best_scenario']} with {recommendation['expected_improvement']:.2%} improvement")
        
        print("\nAPI tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_api())