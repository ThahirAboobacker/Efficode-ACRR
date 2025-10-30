#!/usr/bin/env python
"""
Comprehensive test samples for EFFICODE optimization system
"""

import requests
import json
import time

API_URL = "http://localhost:5000/optimize"

# Test samples with expected optimizations
TEST_SAMPLES = {
    "fibonacci_recursive": {
        "name": "Fibonacci - Recursive to Iterative",
        "code": """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)""",
        "expected_improvement": "O(2^n) → O(n)",
        "description": "Should convert exponential recursive algorithm to linear iterative"
    },
    
    "constant_folding": {
        "name": "Constant Folding",
        "code": """def calculate():
    x = 2 * 3 + 4  # Should become 10
    y = 10 / 2     # Should become 5.0
    z = 2 ** 8     # Should become 256
    return x + y + z""",
        "expected_improvement": "Constant expressions folded",
        "description": "Should fold constant mathematical expressions"
    },
    
    "simple_loop": {
        "name": "Simple Loop",
        "code": """def process_list(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result""",
        "expected_improvement": "Basic analysis",
        "description": "Should analyze loop complexity"
    },
    
    "nested_fibonacci": {
        "name": "Nested Fibonacci Calls",
        "code": """def double_fibonacci(n):
    return fibonacci(n) + fibonacci(n-1)

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)""",
        "expected_improvement": "Multiple optimizations",
        "description": "Should optimize nested recursive calls"
    },
    
    "mathematical_operations": {
        "name": "Mathematical Operations",
        "code": """def math_operations():
    a = 5 + 3 * 2  # Should become 11
    b = 100 / 4    # Should become 25.0
    c = 3 ** 3     # Should become 27
    d = 15 % 4     # Should become 3
    return a + b + c + d""",
        "expected_improvement": "Multiple constant folding",
        "description": "Should fold multiple mathematical expressions"
    },
    
    "factorial_recursive": {
        "name": "Factorial - Recursive",
        "code": """def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n-1)""",
        "expected_improvement": "Complexity analysis",
        "description": "Should analyze recursive factorial complexity"
    },
    
    "power_calculation": {
        "name": "Power Calculations",
        "code": """def power_demo():
    small_power = 2 ** 4    # Should become 16
    medium_power = 3 ** 5   # Should become 243
    large_power = 10 ** 3   # Should become 1000
    return small_power + medium_power + large_power""",
        "expected_improvement": "Power expression folding",
        "description": "Should fold power expressions"
    },
    
    "simple_arithmetic": {
        "name": "Simple Arithmetic",
        "code": """def arithmetic():
    result = 1 + 2 + 3 + 4 + 5  # Should become 15
    return result * 2            # Should become 30""",
        "expected_improvement": "Arithmetic simplification",
        "description": "Should simplify arithmetic expressions"
    }
}

def test_sample(sample_name, sample_data):
    """Test a single code sample"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {sample_data['name']}")
    print(f"📝 Description: {sample_data['description']}")
    print(f"🎯 Expected: {sample_data['expected_improvement']}")
    print('='*60)
    
    payload = {
        "code": sample_data['code'],
        "level": "high"
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=payload, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: {result.get('status', 'unknown')}")
            print(f"⏱️  Processing Time: {end_time - start_time:.3f}s")
            print(f"🔄 Complexity: {result.get('original_complexity', 'N/A')} → {result.get('optimized_complexity', 'N/A')}")
            
            improvements = result.get('improvements', [])
            print(f"🚀 Optimizations Applied: {len(improvements)}")
            
            if improvements:
                for i, imp in enumerate(improvements, 1):
                    print(f"   {i}. {imp.get('type', 'unknown')}: {imp.get('description', 'No description')}")
            
            print(f"💡 Explanation: {result.get('explanation', 'No explanation')}")
            
            # Show code comparison if optimized
            original = result.get('original_code', '')
            optimized = result.get('optimized_code', '')
            
            if original != optimized:
                print(f"\n📋 Original Code:")
                print("   " + "\n   ".join(original.split('\n')))
                print(f"\n⚡ Optimized Code:")
                print("   " + "\n   ".join(optimized.split('\n')))
            else:
                print(f"\n📋 Code: No changes made")
            
            return True
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def run_all_tests():
    """Run all test samples"""
    print("🧠 EFFICODE - Comprehensive Testing Suite")
    print("🚀 Testing AI-Powered Python Code Optimization")
    print(f"🌐 API Endpoint: {API_URL}")
    
    # Test server connectivity first
    try:
        health_response = requests.get("http://localhost:5000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print("⚠️  Server responded but may have issues")
    except:
        print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
        return
    
    results = {}
    total_tests = len(TEST_SAMPLES)
    passed_tests = 0
    
    for sample_name, sample_data in TEST_SAMPLES.items():
        success = test_sample(sample_name, sample_data)
        results[sample_name] = success
        if success:
            passed_tests += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your EFFICODE system is working perfectly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the details above.")
    
    print("\n🔗 Detailed Results:")
    for sample_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {TEST_SAMPLES[sample_name]['name']}")

def test_specific_sample(sample_name):
    """Test a specific sample by name"""
    if sample_name in TEST_SAMPLES:
        test_sample(sample_name, TEST_SAMPLES[sample_name])
    else:
        print(f"❌ Sample '{sample_name}' not found.")
        print("Available samples:")
        for name in TEST_SAMPLES.keys():
            print(f"   - {name}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific sample
        sample_name = sys.argv[1]
        test_specific_sample(sample_name)
    else:
        # Run all tests
        run_all_tests()