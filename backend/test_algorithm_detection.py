#!/usr/bin/env python3
"""
Test the algorithm detection capabilities of the RuleBasedOptimizer.
This script tests different algorithms to verify they are correctly identified and optimized.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Test algorithms
ALGORITHM_TESTS = {
    "fibonacci": """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
""",

    "bubble_sort": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
""",

    "inefficient_max": """
def find_max(numbers):
    sorted_list = sorted(numbers)
    return sorted_list[-1]
""",

    "inefficient_min": """
def find_min(numbers):
    sorted_list = sorted(numbers)
    return sorted_list[0]
""",

    "linear_search": """
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""
}

def test_algorithm(optimizer, algorithm_name, code):
    """Test a specific algorithm detection."""
    logger = logging.getLogger(f"test_{algorithm_name}")
    logger.info(f"Testing algorithm detection for: {algorithm_name}")
    
    logger.info("Original code:")
    logger.info(code)
    
    # Apply optimization
    optimized_code, complexity_before, complexity_after, changes = optimizer.optimize(code)
    
    logger.info("Optimized code:")
    logger.info(optimized_code)
    
    logger.info(f"Complexity before: {complexity_before}")
    logger.info(f"Complexity after: {complexity_after}")
    
    if changes:
        logger.info("Optimization improvements:")
        for change in changes:
            # Handle both string format and dictionary format
            if isinstance(change, dict):
                logger.info(f"- {change['type']}: {change['description']}")
            else:
                logger.info(f"- {change}")
        logger.info(f"TEST RESULT: ✅ SUCCESS - {algorithm_name} was successfully optimized")
        return True
    else:
        logger.warning(f"TEST RESULT: ❌ FAILURE - {algorithm_name} was not optimized")
        return False

def main():
    """Run all algorithm detection tests."""
    logger = logging.getLogger("algorithm_detection_tests")
    logger.info("Starting algorithm detection tests")
    
    # Initialize the optimizer
    optimizer = RuleBasedOptimizer()
    logger.info("Initialized RuleBasedOptimizer")
    
    # Run tests for each algorithm
    results = {}
    for algorithm_name, code in ALGORITHM_TESTS.items():
        results[algorithm_name] = test_algorithm(optimizer, algorithm_name, code)
        print("\n" + "-"*80 + "\n")  # Separator between tests
    
    # Print summary
    logger.info("Test Results Summary:")
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for algorithm_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status}: {algorithm_name}")
    
    logger.info(f"Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("All algorithm detection tests passed! 🎉")
        return 0
    else:
        logger.error(f"Some tests failed ({total_tests - passed_tests}/{total_tests})")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 