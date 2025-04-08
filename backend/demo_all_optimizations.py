"""
OPTIMIZATION CAPABILITIES DEMO

This file demonstrates all optimization capabilities of the RuleBasedOptimizer:
1. Algorithm detection (Fibonacci, bubble sort, linear search)
2. Inefficient max/min operations using sorted lists
3. Constants that can be folded
4. Dead code elimination
5. Unused variable removal
6. Loop optimization with enumerate
7. Repeated computation elimination
8. String concatenation optimization
"""

import sys
import os
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, backend_dir)
sys.path.insert(0, src_dir)

# Import the optimizer
from src.rule_based import RuleBasedOptimizer

# This code contains all the patterns that can be optimized
DEMO_CODE = '''
def demo_all_optimizations(data, threshold=10):
    """
    This function demonstrates all the patterns that can be optimized
    by the RuleBasedOptimizer in a single example.
    """
    # 1. Constants that can be folded
    x = 2 * 3 + 4           # Should become x = 10
    y = 10 / 2              # Should become y = 5.0
    z = 2 ** 8              # Should become z = 256
    PI = 3.14159            # This is fine as is
    
    # 2. Unused variables that should be removed
    unused_var1 = "This variable is never used"
    unused_var2 = 42
    
    # 3. Dead code that should be eliminated
    if False:
        print("This code is unreachable")
        unreachable_var = 100
    
    if True:
        used_var = "This variable is used"
    else:
        print("This branch is unreachable")
    
    # 4. Algorithm detection - Inefficient Fibonacci
    def fibonacci(n):
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fibonacci(n-1) + fibonacci(n-2)
    
    # 5. Algorithm detection - Bubble Sort
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr
    
    # 6. Algorithm detection - Linear search
    def linear_search(arr, target):
        for i in range(len(arr)):
            if arr[i] == target:
                return i
        return -1
    
    # 7. Inefficient max/min operations
    def find_max(my_list):
        sorted_list = sorted(my_list)
        return sorted_list[-1]  # Should use max() instead
    
    def find_min(my_list):
        sorted_list = sorted(my_list)
        return sorted_list[0]   # Should use min() instead
    
    # 8. Loops using range(len) that can be optimized with enumerate
    results = []
    for i in range(len(data)):
        results.append(f"Item {i}: {data[i]}")
    
    # 9. Repeated computations that can be stored in variables
    total = 0
    for i in range(len(data)):
        # The expensive operation is computed multiple times
        total += len(data) * sum(data) / (i+1)
    
    expensive_result1 = find_max(data) * find_min(data) * len(data)
    expensive_result2 = find_max(data) * find_min(data) * len(data)  # Same computation repeated
    
    # 10. Inefficient string concatenation
    message = ""
    for item in data:
        message = message + str(item) + ", "  # Should use join instead
    
    greeting = "Hello " + "world" + "! " + "How" + " are" + " you" + "?"  # Should be concatenated
    
    # Actual computation using some of the functions
    if threshold > 5:
        result = fibonacci(10)  # Should be optimized to iterative version
        sorted_data = bubble_sort(data.copy())  # Should use built-in sorted
        max_value = find_max(data)  # Should use max() directly
    else:
        result = 0
        sorted_data = []
        max_value = 0
    
    return {
        "result": result,
        "constants": (x, y, z),
        "max_value": max_value,
        "sorted_data": sorted_data,
        "message": message,
        "greeting": greeting,
        "used_variable": used_var,
        "expensive_results": (expensive_result1, expensive_result2),
        "processed_items": results
    }
'''

def main():
    # Initialize the optimizer
    optimizer = RuleBasedOptimizer()
    
    # Print original code
    print("\n" + "="*80)
    print("ORIGINAL CODE:")
    print("="*80)
    print(DEMO_CODE)
    
    # Time the optimization
    start_time = time.time()
    
    # Apply optimization
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(
        DEMO_CODE, level='high'
    )
    
    optimization_time = time.time() - start_time
    
    # Print optimized code
    print("\n" + "="*80)
    print("OPTIMIZED CODE:")
    print("="*80)
    print(optimized_code)
    
    # Print optimization summary
    print("\n" + "="*80)
    print("OPTIMIZATION SUMMARY:")
    print("="*80)
    print(f"Original complexity: {original_complexity}")
    print(f"Optimized complexity: {optimized_complexity}")
    print(f"Explanation: {explanation}")
    print(f"Optimization time: {optimization_time:.4f} seconds")
    
    # Get and print applied rules
    applied_rules = optimizer.get_applied_rules()
    
    print("\n" + "="*80)
    print("APPLIED OPTIMIZATIONS:")
    print("="*80)
    
    # Group optimizations by type
    optimization_types = {}
    for rule in applied_rules:
        rule_type = rule.get('type', 'unknown')
        if rule_type not in optimization_types:
            optimization_types[rule_type] = []
        optimization_types[rule_type].append(rule.get('description', 'No description'))
    
    # Print optimizations by type
    for opt_type, descriptions in optimization_types.items():
        print(f"\n{opt_type.replace('_', ' ').title()}:")
        for desc in descriptions:
            print(f"  - {desc}")
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main() 