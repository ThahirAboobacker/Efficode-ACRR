import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the rule-based optimizer
from src.rule_based import RuleBasedOptimizer

# Test code with known optimizations
TEST_CODE = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def test_function():
    # Constant expressions that can be folded
    x = 10 * 5 + 2
    y = (3 + 4) * 2
    
    # Unused variables to be removed
    unused_var = "This won't be used"
    
    # Unreachable code to be eliminated
    if False:
        print("This will never be executed")
    
    return fibonacci(10)
"""

def main():
    logger.info("Testing RuleBasedOptimizer...")
    
    # Create the optimizer
    optimizer = RuleBasedOptimizer()
    
    # Print the original code
    logger.info("Original Code:")
    logger.info(TEST_CODE)
    
    # Apply optimizations
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(TEST_CODE)
    
    # Print the optimized code
    logger.info("Optimized Code:")
    logger.info(optimized_code)
    
    # Print the optimization explanation
    logger.info(f"Original Complexity: {original_complexity}")
    logger.info(f"Optimized Complexity: {optimized_complexity}")
    logger.info(f"Explanation: {explanation}")
    
    # Check if optimizations were applied
    if optimized_code != TEST_CODE:
        logger.info("Optimization SUCCESSFUL - Code was improved!")
        
        # Print the applied optimizations
        logger.info("Applied optimizations:")
        for change in optimizer.get_applied_rules():
            logger.info(f"- {change.get('type', 'unknown')}: {change.get('description', 'No description')}")
    else:
        logger.error("Optimization FAILED - No changes were made to the code.")

if __name__ == "__main__":
    main() 