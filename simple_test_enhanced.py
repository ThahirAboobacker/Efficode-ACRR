#!/usr/bin/env python
"""
Simple test for the enhanced server
"""

import requests
import json

def test_server():
    try:
        # Test root endpoint
        response = requests.get("http://192.168.1.10:5001/")
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        
        # Test health
        response = requests.get("http://192.168.1.10:5001/health")
        print(f"\nHealth endpoint: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        
        # Test optimization
        payload = {
            "code": """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)""",
            "level": "high"
        }
        
        response = requests.post("http://192.168.1.10:5001/optimize", json=payload)
        print(f"\nOptimization endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Original complexity: {result['original_complexity']}")
            print(f"Optimized complexity: {result['optimized_complexity']}")
            print(f"Performance improvement: {result['performance_improvement']}%")
            print(f"Code changed: {result['original_code'] != result['optimized_code']}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")