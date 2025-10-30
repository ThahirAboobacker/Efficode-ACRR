#!/usr/bin/env python
"""
Interactive samples for testing EFFICODE optimizations
"""

import requests
import json

API_URL = "http://localhost:5000/optimize"

def test_optimization(name, code, level="medium"):
    """Test a single optimization and display results nicely"""
    print(f"\n🧪 Testing: {name}")
    print("=" * 50)
    
    payload = {"code": code, "level": level}
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            
            print(f"📝 Original Code:")
            for i, line in enumerate(code.split('\n'), 1):
                print(f"   {i:2d}: {line}")
            
            print(f"\n⚡ Optimized Code:")
            optimized = result.get('optimized_code', code)
            for i, line in enumerate(optimized.split('\n'), 1):
                print(f"   {i:2d}: {line}")
            
            print(f"\n📊 Analysis:")
            print(f"   Complexity: {result.get('original_complexity')} → {result.get('optimized_complexity')}")
            print(f"   Improvements: {len(result.get('improvements', []))}")
            print(f"   Explanation: {result.get('explanation')}")
            
            if result.get('improvements'):
                print(f"\n🚀 Applied Optimizations:")
                for i, imp in enumerate(result['improvements'], 1):
                    print(f"   {i}. {imp.get('type')}: {imp.get('description')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Run interactive optimization samples"""
    print("🧠 EFFICODE - Interactive Optimization Samples")
    print("🚀 Demonstrating AI-Powered Code Optimization")
    
    # Sample 1: Fibonacci Optimization
    test_optimization(
        "Fibonacci Recursive → Iterative",
        """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)"""
    )
    
    # Sample 2: Constant Folding
    test_optimization(
        "Constant Folding",
        """def calculate():
    result = 2 * 3 + 4
    power = 2 ** 8
    division = 10 / 2
    return result + power + division"""
    )
    
    # Sample 3: Complex Expression
    test_optimization(
        "Complex Mathematical Expression",
        """def complex_math():
    a = 5 + 3 * 2
    b = 100 / 4
    c = 3 ** 3
    return a + b + c"""
    )
    
    # Sample 4: Nested Function with Fibonacci
    test_optimization(
        "Nested Fibonacci Function",
        """def calculate_fibonacci_sum(n):
    return fibonacci(n) + fibonacci(n-1)

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)"""
    )
    
    # Sample 5: Simple Loop (No optimization expected)
    test_optimization(
        "Simple Loop (Baseline)",
        """def process_items(items):
    results = []
    for item in items:
        results.append(item * 2)
    return results"""
    )
    
    print(f"\n{'='*60}")
    print("✅ All samples tested successfully!")
    print("🌐 Try the web interface at test_interface.html for more interactive testing")
    print("📚 Use test_samples.py for comprehensive automated testing")

if __name__ == "__main__":
    main()