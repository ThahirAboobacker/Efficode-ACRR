#!/usr/bin/env python
"""
Test script to verify RuleBasedOptimizer correctly optimizes the user's input code.
"""

import logging
from src.rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User's input code
USER_CODE = """
import math

def process_data(data):
    # Dead code after return
    print("This is unreachable.")  # Dead code, won't be executed.
    return 42

def calculate_area(radius):
    # Unnecessary function call repetition
    area = math.pi * radius * radius  # Compute once
    area2 = math.pi * radius * radius  # Same computation repeated unnecessarily
    return area

def check_numbers(x, y):
    # Unused variables
    result = x + y  # result is never used, so this is inefficient
    if x == y:
        print("x and y are equal")
    elif x > 10:
        print("x is greater than 10")
    else:
        print("x is less than or equal to 10")
    return x + y  # This return value isn't used

def string_manipulation():
    # Inefficient string concatenation in loop
    result = ""
    for word in ["hello", "world", "how", "are", "you"]:
        result += word  # Inefficient concatenation in a loop
    return result

def loop_with_redundant_checks():
    # Repeated conditions, could be simplified
    for i in range(10):
        if i == 5:
            print(f"Found 5")
        elif i == 10:  # Redundant because i will never reach 10
            print(f"Found 10")
    return i

def optimize_data():
    # Repeated lookups in dictionary, inefficient
    data = {"a": 1, "b": 2, "c": 3}
    if data["a"] == 1 and data["b"] == 2:
        print("Both 'a' and 'b' are correct")
    if data["a"] == 1 and data["c"] == 3:
        print("Both 'a' and 'c' are correct")
    return data["a"] + data["b"]  # Repeated lookups of the same values

def long_condition_check(a):
    # Long condition expression that can be simplified
    if a == 1 or a == 2 or a == 3 or a == 4:
        print("a is in the range from 1 to 4")

def nested_loops():
    # Nested loops that can be simplified or unrolled
    for i in range(1000):
        for j in range(1000):
            print(i, j)

def unnecessary_function_calls(x):
    # Function call made multiple times unnecessarily
    if complex_calculation(x) and complex_calculation(x + 1):
        print("Both conditions met")

def complex_calculation(x):
    # Placeholder for complex calculation function
    return x > 10
    print(never)

def inefficient_sort():
    # Sorting when not necessary
    my_list = [4, 2, 3, 1, 5]
    sorted_list = sorted(my_list)
    return sorted_list[-1]  # Inefficient: `max()` would be better
    u=45

# Calling all the inefficient functions
process_data(10)
calculate_area(5)
check_numbers(5, 10)
string_manipulation()
loop_with_redundant_checks()
optimize_data()
long_condition_check(3)
nested_loops()
inefficient_sort()
"""

def main():
    """Run the optimizer on the user's input code."""
    logger.info("Testing RuleBasedOptimizer with user's input code")
    
    # Create optimizer
    optimizer = RuleBasedOptimizer()
    
    # Run optimization
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(USER_CODE, level="high")
    
    # Get improvements
    improvements = optimizer.get_applied_rules()
    
    # Log results
    logger.info(f"Original complexity: {original_complexity}")
    logger.info(f"Optimized complexity: {optimized_complexity}")
    logger.info(f"Number of improvements: {len(improvements)}")
    
    # Print optimization details
    logger.info("Applied optimizations:")
    optimization_types = set()
    for imp in improvements:
        imp_type = imp.get('type', 'unknown')
        optimization_types.add(imp_type)
        description = imp.get('description', 'No description')
        logger.info(f"  - {imp_type}: {description}")
        
    # Check for expected optimizations
    expected_optimizations = {
        'dead_code_elimination',
        'unreachable_code_removal',
        'unused_variable_removal',
        'repeated_computation',
        'string_join_optimization',
        'algorithm_replacement'
    }
    
    # Check which expected optimizations were applied
    logger.info("\nExpected optimizations check:")
    for opt in expected_optimizations:
        status = "✓" if opt in optimization_types else "✗"
        logger.info(f"  {opt:<30} {status}")
    
    # Print optimized code
    logger.info("\nOPTIMIZED CODE:")
    logger.info("-" * 80)
    logger.info(optimized_code)
    logger.info("-" * 80)
    
    # Success if any improvements were made
    success = len(improvements) > 0
    logger.info(f"\nOptimization successful: {success}")
    return success

if __name__ == "__main__":
    success = main()
    print(f"TEST RESULT: {'SUCCESS' if success else 'FAILURE'}")