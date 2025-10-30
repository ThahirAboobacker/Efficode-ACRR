#!/usr/bin/env python
"""
Test script for the EFFICODE API
"""

import requests
import json

def test_api():
    url = "http://localhost:5000/optimize"
    
    # Test case 1: Fibonacci optimization
    test_code = """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)"""
    
    payload = {
        "code": test_code,
        "level": "medium"
    }
    
    try:
        print("Testing EFFICODE API...")
        print("=" * 50)
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Test Successful!")
            print(f"Status: {result.get('status')}")
            print(f"Original Complexity: {result.get('original_complexity')}")
            print(f"Optimized Complexity: {result.get('optimized_complexity')}")
            print(f"Improvements: {len(result.get('improvements', []))}")
            print(f"Explanation: {result.get('explanation')}")
            
            if result.get('improvements'):
                print("\nApplied Optimizations:")
                for i, imp in enumerate(result['improvements'], 1):
                    print(f"  {i}. {imp.get('type')}: {imp.get('description')}")
            
            return True
        else:
            print(f"❌ API Test Failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ API Test Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 Your EFFICODE server is working!")
        print("Open test_interface.html in your browser to use the web interface.")
    else:
        print("\n❌ There's an issue with the server.")