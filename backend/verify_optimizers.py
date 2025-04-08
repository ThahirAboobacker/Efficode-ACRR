#!/usr/bin/env python
"""
Comprehensive verification of the RuleBasedOptimizer.
This script tests all optimization types to verify they're working correctly.
"""

import logging
import sys
import os
from src.rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test cases for different optimization types
TEST_CASES = {
    "constant_folding": {
        "name": "Constant Folding",
        "code": """
def test_constant_folding():
    x = 2 * 3 + 4  # Should be folded to 10
    y = 10 / 2     # Should be folded to 5.0
    z = 2 ** 8     # Should be folded to 256
    return x + y + z
"""
    },
    "dead_code": {
        "name": "Dead Code Elimination",
        "code": """
def test_dead_code():
    if True:
        x = 10
        return x
        print("This will never execute")  # Dead code after return
    else:
        print("This will never execute")  # Unreachable else branch
"""
    },
    "unused_vars": {
        "name": "Unused Variable Removal",
        "code": """
def test_unused_vars():
    x = 10  # Used variable
    y = 20  # Unused variable
    z = 30  # Unused variable
    return x
"""
    },
    "loop_optimization": {
        "name": "Loop Optimization",
        "code": """
def test_loop_optimization():
    items = ["a", "b", "c"]
    result = []
    for i in range(len(items)):
        result.append(items[i].upper())
    return result
"""
    },
    "repeated_computation": {
        "name": "Repeated Computation Elimination",
        "code": """
def expensive_operation(n):
    return n * n

def test_repeated_computation():
    x = 10
    y = 20
    # The expensive_operation(x+y) computation is repeated
    result1 = expensive_operation(x+y) * 2
    result2 = expensive_operation(x+y) * 3
    return result1 + result2
"""
    },
    "fibonacci": {
        "name": "Fibonacci (Algorithm Replacement)",
        "code": """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""
    },
    "bubble_sort": {
        "name": "Bubble Sort (Algorithm Replacement)",
        "code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    }
}

def test_optimization(optimizer, test_name, code, level="high"):
    """Test an optimization and log results."""
    logger.info(f"Testing {test_name}...")
    
    # Run optimization
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level=level)
    
    # Get improvements
    improvements = optimizer.get_applied_rules()
    
    # Log results
    logger.info(f"Original code length: {len(code)}")
    logger.info(f"Optimized code length: {len(optimized_code)}")
    logger.info(f"Original complexity: {original_complexity}")
    logger.info(f"Optimized complexity: {optimized_complexity}")
    logger.info(f"Number of improvements: {len(improvements)}")
    
    # Print improvements
    if improvements:
        logger.info("Applied optimizations:")
        for imp in improvements:
            if isinstance(imp, dict):
                imp_type = imp.get('type', 'unknown')
                description = imp.get('description', 'No description')
                logger.info(f"  - {imp_type}: {description}")
    else:
        logger.info("No improvements recorded")
    
    # Print code comparison for debug
    logger.info("BEFORE:")
    logger.info("-" * 50)
    logger.info(code)
    logger.info("-" * 50)
    logger.info("AFTER:")
    logger.info("-" * 50)
    logger.info(optimized_code)
    logger.info("-" * 50)
    
    # Check if optimization was successful (different code or improvements)
    success = len(improvements) > 0 or code != optimized_code
    logger.info(f"Optimization successful: {success}")
    logger.info("")
    
    return success

def main():
    """Run all optimization tests."""
    logger.info("Starting comprehensive RuleBasedOptimizer verification")
    
    # Create optimizer
    optimizer = RuleBasedOptimizer()
    
    # Run tests
    results = {}
    for test_id, test_data in TEST_CASES.items():
        results[test_id] = test_optimization(optimizer, test_data["name"], test_data["code"])
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("VERIFICATION RESULTS")
    logger.info("="*50)
    
    all_passed = True
    for test_id, passed in results.items():
        status = "✓" if passed else "✗"
        logger.info(f"{TEST_CASES[test_id]['name']:<30} {status}")
        all_passed = all_passed and passed
    
    logger.info("\nOverall result: " + ("SUCCESS" if all_passed else "FAILURE"))
    return all_passed

if __name__ == "__main__":
    success = main()
    print(f"VERIFICATION RESULT: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1) 