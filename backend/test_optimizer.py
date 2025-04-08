"""
Direct test of the RuleBasedOptimizer used in app.py.
This script tests whether the optimizer is correctly initialized and working.
"""

import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test case
TEST_CODE = """
def test_constant_folding():
    x = 2 * 3 + 4  # Should be folded to 10
    y = 10 / 2     # Should be folded to 5.0
    z = 2 ** 8     # Should be folded to 256
    return x + y + z
"""

def main():
    """Test if the optimizer works directly."""
    try:
        # Import the optimizer from app.py
        sys.path.insert(0, os.path.abspath('.'))
        from app import rule_based_optimizer
        
        # Run optimization
        optimized_code, original_complexity, optimized_complexity, explanation = rule_based_optimizer.optimize(TEST_CODE, level="high")
        
        # Get improvements
        improvements = rule_based_optimizer.get_applied_rules()
        
        # Log results
        logger.info(f"Original code:\n{TEST_CODE}")
        logger.info(f"Optimized code:\n{optimized_code}")
        logger.info(f"Original complexity: {original_complexity}")
        logger.info(f"Optimized complexity: {optimized_complexity}")
        logger.info(f"Explanation: {explanation}")
        logger.info(f"Number of improvements: {len(improvements)}")
        
        # Print improvements
        if improvements:
            logger.info("IMPROVEMENTS:")
            for imp in improvements:
                if isinstance(imp, dict):
                    logger.info(f"  - {imp.get('type', 'unknown')}: {imp.get('description', 'No description')}")
        else:
            logger.info("No improvements recorded")
        
        # Check if optimization was successful
        success = len(improvements) > 0 and optimized_code != TEST_CODE
        logger.info(f"Optimization successful: {success}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    print(f"TEST RESULT: {'SUCCESS' if success else 'FAILURE'}") 