#!/usr/bin/env python
"""
Test script for EFFICODE-ACRR optimization API
"""

import requests
import json
import sys

def test_optimization():
    """Test the optimization API endpoint"""
    url = "http://localhost:5000/api/optimize"
    
    # Test code to optimize
    test_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
    """
    
    # Request data
    data = {
        "code": test_code,
        "optimization_level": "medium"
    }
    
    try:
        # Send request
        print("Sending optimization request...")
        response = requests.post(url, json=data, timeout=10)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("\n=== Optimization successful ===")
            print(f"Original code:\n{result['original_code']}")
            print(f"\nOptimized code:\n{result['optimized_code']}")
            print(f"\nOriginal complexity: {result['original_complexity']}")
            print(f"Optimized complexity: {result['optimized_complexity']}")
            print(f"\nExplanation: {result['explanation']}")
            print(f"Processing time: {result['processing_time']:.2f} seconds")
            return True
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing EFFICODE-ACRR optimization API...")
    success = test_optimization()
    sys.exit(0 if success else 1) 