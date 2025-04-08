"""
Test script to verify RuleBasedOptimizer correctly records improvements.
"""

import logging
from src.rule_based import RuleBasedOptimizer

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
    """Run the test."""
    logger.info("Testing RuleBasedOptimizer improvements recording")
    
    # Create optimizer
    optimizer = RuleBasedOptimizer()
    
    # Run optimization
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(TEST_CODE, level="high")
    
    # Get improvements
    improvements = optimizer.get_applied_rules()
    
    # Log results
    logger.info(f"Original code length: {len(TEST_CODE)}")
    logger.info(f"Optimized code length: {len(optimized_code)}")
    logger.info(f"Number of improvements: {len(improvements)}")
    
    # Print optimized code
    logger.info("OPTIMIZED CODE:")
    logger.info("-" * 50)
    logger.info(optimized_code)
    logger.info("-" * 50)
    
    # Print improvements
    logger.info("IMPROVEMENTS:")
    logger.info("-" * 50)
    if improvements:
        for imp in improvements:
            if isinstance(imp, dict):
                logger.info(f"Type: {imp.get('type', 'unknown')}")
                logger.info(f"Description: {imp.get('description', 'No description')}")
                logger.info(f"Category: {imp.get('category', 'unknown')}")
            else:
                logger.info(f"Non-dict improvement: {str(imp)}")
            logger.info("-" * 30)
    else:
        logger.info("No improvements recorded")
    
    return len(improvements) > 0

if __name__ == "__main__":
    success = main()
    print(f"TEST RESULT: {'SUCCESS' if success else 'FAILURE'}") 