"""
Test script to verify the string join optimization in RuleBasedOptimizer.
"""

import logging
import sys
import os

# Add the parent directory to the path to import the app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the RuleBasedOptimizer from app
from app import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Test code with inefficient string concatenation
TEST_CODE = """
def inefficient_string_concat(items):
    # Creating an empty string and then concatenating
    result = ""
    for item in items:
        result += str(item) + ","
    return result[:-1]  # Remove trailing comma
    
def another_string_concat(items):
    # Multiple concatenations in a single statement
    message = "Items: " + str(items[0]) + ", " + str(items[1]) + ", " + str(items[2])
    return message

def string_concat_with_assignment(names):
    # String concatenation with assignment in a loop
    full_message = "Names: "
    for name in names:
        greeting = "Hello, " + name
        full_message = full_message + greeting + ". "
    return full_message
"""

def main():
    """Run the test to verify string join optimization."""
    logging.info("Testing String Join Optimization...")
    
    # Create an instance of the RuleBasedOptimizer
    optimizer = RuleBasedOptimizer()
    
    # Log the original code
    logging.info("Original Code:")
    logging.info(TEST_CODE)
    
    # Apply optimization to the test code
    result = optimizer.optimize(TEST_CODE)
    optimized_code = result["optimized_code"]
    improvements = result["improvements"]
    
    # Log the optimized code
    logging.info("Optimized Code:")
    logging.info(optimized_code)
    
    # Log the improvements
    logging.info(f"Number of improvements: {len(improvements)}")
    for i, improvement in enumerate(improvements):
        logging.info(f"Improvement {i+1}: {improvement['description']} at line {improvement.get('location', 'unknown')}")
    
    # Check if string optimizations were applied
    string_optimizations = [
        improvement for improvement in improvements 
        if improvement['type'] == 'string_optimization'
    ]
    
    if string_optimizations:
        logging.info(f"SUCCESS: Found {len(string_optimizations)} string join optimizations")
        for opt in string_optimizations:
            logging.info(f"  - {opt['description']}")
    else:
        logging.error("FAILED: No string join optimizations were applied")
    
    # Check overall test result
    if string_optimizations:
        logging.info("String Join Optimization Test: PASSED")
    else:
        logging.error("String Join Optimization Test: FAILED")

if __name__ == "__main__":
    main() 