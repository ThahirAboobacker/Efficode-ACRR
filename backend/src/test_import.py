"""Test imports for the rule-based module"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    logger.info("Importing rule_based module...")
    from rule_based import apply_optimization_rules
    
    # Test the function
    code = """
def test_func():
    x = 5  # unused variable
    return 10
"""
    
    logger.info("Calling apply_optimization_rules...")
    result = apply_optimization_rules(code)
    
    # Print detailed information about the result
    logger.info(f"Result type: {type(result)}")
    
    if isinstance(result, tuple):
        logger.info(f"Tuple length: {len(result)}")
        for i, item in enumerate(result):
            logger.info(f"Item {i} type: {type(item)}")
            logger.info(f"Item {i} value: {item}")
    else:
        logger.info(f"Result: {result}")
    
    # Create a compatibility wrapper that adapts to the actual return value
    logger.info("Testing compatibility wrapper...")
    def optimize_code(code):
        result = apply_optimization_rules(code)
        
        # Handle various return types
        if isinstance(result, tuple):
            if len(result) >= 3:
                # Might be returning (code, changes, other)
                optimized, changes, *_ = result
            elif len(result) == 2:
                # Returning (code, changes)
                optimized, changes = result
            else:
                # Unexpected tuple length
                optimized = result[0] if result else code
                changes = []
        else:
            # Not a tuple, assume it's just the optimized code
            optimized = result
            changes = []
            
        # Convert changes to expected format
        pattern_dicts = []
        if isinstance(changes, list):
            for change in changes:
                pattern_dicts.append({
                    "name": str(change),
                    "severity": "medium",
                    "optimization": "applied",
                    "lines": [1, 1]
                })
        
        return optimized, pattern_dicts, len(pattern_dicts)
    
    opt_result = optimize_code(code)
    logger.info(f"Wrapper result: {opt_result}")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    logger.info("Test completed") 