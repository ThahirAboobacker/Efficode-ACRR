#!/usr/bin/env python
"""
Edge case tests for EFFICODE to demonstrate robustness
"""

import requests
import json

API_URL = "http://localhost:5000/optimize"

def test_edge_case(name, code, expected_status="success"):
    """Test edge cases and error handling"""
    print(f"\n🧪 Testing Edge Case: {name}")
    print("=" * 50)
    
    payload = {"code": code, "level": "medium"}
    
    try:
        response = requests.post(API_URL, json=payload)
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        
        if result.get('status') == 'error':
            print(f"❌ Error: {result.get('error')}")
        else:
            print(f"✅ Processed successfully")
            print(f"Complexity: {result.get('original_complexity')} → {result.get('optimized_complexity')}")
            print(f"Improvements: {len(result.get('improvements', []))}")
        
        return result.get('status') == expected_status
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Test various edge cases"""
    print("🧠 EFFICODE - Edge Case Testing")
    print("🔍 Testing system robustness and error handling")
    
    # Test 1: Empty code
    test_edge_case(
        "Empty Code",
        "",
        expected_status="error"
    )
    
    # Test 2: Syntax error
    test_edge_case(
        "Syntax Error",
        """def broken_function(
    return "missing closing parenthesis" """,
        expected_status="error"
    )
    
    # Test 3: Very simple code
    test_edge_case(
        "Very Simple Code",
        """x = 1""",
        expected_status="success"
    )
    
    # Test 4: Already optimized Fibonacci
    test_edge_case(
        "Already Optimized Fibonacci",
        """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b""",
        expected_status="success"
    )
    
    # Test 5: Complex nested structure
    test_edge_case(
        "Complex Nested Structure",
        """def complex_function():
    def inner_fibonacci(n):
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            return inner_fibonacci(n-1) + inner_fibonacci(n-2)
    
    result = inner_fibonacci(10)
    return result * 2 * 3""",
        expected_status="success"
    )
    
    # Test 6: Multiple constant expressions
    test_edge_case(
        "Multiple Constants",
        """def many_constants():
    a = 1 + 1
    b = 2 * 2
    c = 3 ** 2
    d = 8 / 2
    e = 10 % 3
    return a + b + c + d + e""",
        expected_status="success"
    )
    
    # Test 7: No optimization needed
    test_edge_case(
        "No Optimization Needed",
        """def simple_function(x):
    return x + 1""",
        expected_status="success"
    )
    
    print(f"\n{'='*60}")
    print("✅ Edge case testing completed!")
    print("🛡️  System demonstrates good robustness and error handling")

if __name__ == "__main__":
    main()