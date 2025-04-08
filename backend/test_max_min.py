#!/usr/bin/env python3
"""
Test script for specifically testing the max/min replacement optimization.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import app
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

logger = logging.getLogger("max_min_test")

# Test for max replacement
MAX_TEST = """
def find_max(numbers):
    sorted_list = sorted(numbers)
    return sorted_list[-1]
"""

# Test for min replacement
MIN_TEST = """
def find_min(numbers):
    sorted_list = sorted(numbers)
    return sorted_list[0]
"""

def main():
    """Run the max/min replacement tests."""
    optimizer = RuleBasedOptimizer()
    logger.info("Initialized RuleBasedOptimizer")
    
    # Test max replacement
    logger.info("Testing max replacement optimization")
    logger.info("Original max code:\n%s", MAX_TEST)
    max_optimized, max_complexity_before, max_complexity_after, max_changes = optimizer.optimize(MAX_TEST)
    logger.info("Optimized max code:\n%s", max_optimized)
    logger.info("Changes: %s", max_changes)
    
    # Test min replacement
    logger.info("\nTesting min replacement optimization")
    logger.info("Original min code:\n%s", MIN_TEST)
    min_optimized, min_complexity_before, min_complexity_after, min_changes = optimizer.optimize(MIN_TEST)
    logger.info("Optimized min code:\n%s", min_optimized)
    logger.info("Changes: %s", min_changes)
    
    # Check if the optimization improved the code (changed sorted to max/min)
    max_success = "max(" in max_optimized
    min_success = "min(" in min_optimized
    
    if max_success and min_success:
        logger.info("\nBoth tests PASSED! ✅")
        return 0
    else:
        logger.error("\nTests FAILED! ❌")
        if not max_success:
            logger.error("Max replacement failed")
        if not min_success:
            logger.error("Min replacement failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 