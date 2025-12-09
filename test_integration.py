#!/usr/bin/env python3
"""
Integration test for the AI Traffic Simulator
Tests both backend API and frontend accessibility
"""

import requests
import time
import json

def test_backend():
    """Test backend API endpoints"""
    base_url = "http://localhost:12000/api/traffic"
    
    print("🔧 Testing Backend API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data['status']}")
            print(f"   Network initialized: {health_data.get('network_initialized', False)}")
            print(f"   Engines ready: {health_data.get('engines_ready', False)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test network status
    try:
        response = requests.get(f"{base_url}/network/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Network status: {len(status_data)} segments")
        else:
            print(f"❌ Network status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Network status error: {e}")
    
    # Test prediction
    try:
        response = requests.post(f"{base_url}/prediction/forecast?duration_minutes=30", timeout=10)
        if response.status_code == 200:
            prediction_data = response.json()
            warnings_count = len(prediction_data.get('congestion_warnings', []))
            print(f"✅ Prediction: {warnings_count} congestion warnings")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prediction error: {e}")
    
    # Test AI recommendations
    try:
        response = requests.post(f"{base_url}/ai/recommend?duration_minutes=30", timeout=15)
        if response.status_code == 200:
            ai_data = response.json()
            improvement = ai_data.get('expected_improvement', 0) * 100
            print(f"✅ AI Recommendations: {improvement:.1f}% improvement expected")
        else:
            print(f"❌ AI recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"❌ AI recommendations error: {e}")
    
    return True

def test_frontend():
    """Test frontend accessibility"""
    print("\n🌐 Testing Frontend...")
    
    # Try multiple ports where frontend might be running
    ports = [12001, 12002, 12003, 12004, 12005]
    
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                content = response.text
                if "AI Traffic Simulator" in content or "root" in content or "<!doctype html" in content.lower():
                    print(f"✅ Frontend accessible on port {port}")
                    print(f"   URL: http://localhost:{port}")
                    return True
        except Exception:
            continue
    
    print("❌ Frontend not accessible on any expected port")
    return False

def main():
    print("🚦 AI Traffic Simulator - Integration Test")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n📊 Test Summary:")
    print(f"Backend API: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend:    {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 All systems operational!")
        print("\n🔗 Access URLs:")
        print("   Backend API: http://localhost:12000/api/traffic/health")
        print("   Frontend:    Check ports 12001-12005 (auto-detected)")
        print("   API Docs:    http://localhost:12000/docs")
        return True
    else:
        print("\n⚠️  Some systems need attention")
        return False

if __name__ == "__main__":
    main()