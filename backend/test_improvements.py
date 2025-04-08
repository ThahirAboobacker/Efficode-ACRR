#!/usr/bin/env python
"""
Comprehensive test script for improved RuleBasedOptimizer.
Tests all recent enhancements like unused variable removal, unreachable code detection,
inefficient max/min calculation detection, and string concatenation optimization.
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
    "unused_variables": {
        "name": "Improved Unused Variable Removal",
        "code": """
def test_unused_vars():
    x = 10  # Used variable
    y = 20  # Unused variable
    z = 30  # Unused variable
    result = x * 2  # result is unused
    
    # Complex usage pattern
    for i in range(10):
        print(i)
        
    return x
"""
    },
    "unreachable_code": {
        "name": "Enhanced Unreachable Code Detection",
        "code": """
def process_data(data):
    # Dead code after return
    print("This is unreachable.")  # Should be removed
    return 42

def complex_calculation(x):
    # Function with unreachable code
    return x > 10
    print("This will never be called")  # Should be removed
"""
    },
    "inefficient_max": {
        "name": "Inefficient Max Calculation Detection",
        "code": """
def inefficient_sort():
    # Sorting when max() would be better
    my_list = [4, 2, 3, 1, 5]
    sorted_list = sorted(my_list)
    return sorted_list[-1]  # Should be replaced with max(my_list)
"""
    },
    "inefficient_min": {
        "name": "Inefficient Min Calculation Detection",
        "code": """
def inefficient_min():
    # Sorting when min() would be better
    my_list = [4, 2, 3, 1, 5]
    sorted_list = sorted(my_list)
    return sorted_list[0]  # Should be replaced with min(my_list)
"""
    },
    "string_concatenation": {
        "name": "String Concatenation Optimization",
        "code": """
def string_manipulation():
    # Inefficient string concatenation in loop
    result = ""
    for word in ["hello", "world", "how", "are", "you"]:
        result += word  # Should be replaced with join
    return result
"""
    },
    "combined_optimizations": {
        "name": "Combined Optimizations Test",
        "code": """
def combined_test(data):
    # Unused variables
    unused1 = "This is never used"
    
    # Inefficient string concatenation
    result = ""
    for word in ["hello", "world"]:
        result += word
    
    # Unreachable code
    if True:
        x = 10
    else:
        x = 20  # Unreachable
    
    # Inefficient max
    numbers = [1, 2, 3, 4, 5]
    sorted_numbers = sorted(numbers)
    max_value = sorted_numbers[-1]
    
    # Dead code
    return max_value
    print("This will never execute")  # Unreachable
"""
    }
}

def test_optimization(test_name, code, level="high"):
    """Test an optimization and log results."""
    logger.info(f"Testing {test_name}...")
    
    # Create optimizer
    optimizer = RuleBasedOptimizer()
    
    # Run optimization
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level=level)
    
    # Get improvements
    improvements = optimizer.get_applied_rules()
    
    # Log results
    logger.info(f"Original code length: {len(code)}")
    logger.info(f"Optimized code length: {len(optimized_code)}")
    logger.info(f"Number of improvements: {len(improvements)}")
    
    # Print improvements
    if improvements:
        logger.info("Applied optimizations:")
        for imp in improvements:
            imp_type = imp.get('type', 'unknown')
            description = imp.get('description', 'No description')
            logger.info(f"  - {imp_type}: {description}")
    else:
        logger.info("No improvements recorded")
    
    # Print code comparison
    logger.info("BEFORE:")
    logger.info("-" * 50)
    logger.info(code)
    logger.info("-" * 50)
    logger.info("AFTER:")
    logger.info("-" * 50)
    logger.info(optimized_code)
    logger.info("-" * 50)
    
    # Check if optimization was successful (different code or improvements)
    success = len(improvements) > 0 and code != optimized_code
    logger.info(f"Optimization successful: {success}")
    logger.info("")
    
    return success

def main():
    """Run all optimization tests."""
    logger.info("Starting improved RuleBasedOptimizer verification")
    
    # Run tests
    results = {}
    for test_id, test_data in TEST_CASES.items():
        results[test_id] = test_optimization(test_data["name"], test_data["code"])
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS")
    logger.info("="*50)
    
    all_passed = True
    for test_id, passed in results.items():
        status = "✓" if passed else "✗"
        logger.info(f"{TEST_CASES[test_id]['name']:<35} {status}")
        all_passed = all_passed and passed
    
    logger.info("\nOverall result: " + ("SUCCESS" if all_passed else "FAILURE"))
    return all_passed

if __name__ == "__main__":
    success = main()
    print(f"TEST RESULT: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1) 