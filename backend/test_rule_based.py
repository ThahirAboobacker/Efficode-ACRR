"""
Test the rule-based optimizer with various test cases.
"""

import sys
import os
import logging
from src.rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_constant_folding():
    """Test constant folding optimization."""
    logger.info("Testing constant folding...")
    
    code = """
def calculate():
    x = 3 + 5
    y = 10 * 2
    z = 100 / 4
    return x + y + z
"""
    
    optimizer = RuleBasedOptimizer()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level='high')
    
    logger.info(f"Original code:\n{code}")
    logger.info(f"Optimized code:\n{optimized_code}")
    logger.info(f"Explanation: {explanation}")
    logger.info(f"Complexity: {original_complexity} -> {optimized_complexity}")
    logger.info("Applied rules:")
    for rule in optimizer.get_applied_rules():
        logger.info(f"  - {rule.get('type', 'unknown')}: {rule.get('description', '')}")
    
    logger.info("Constant folding test complete\n")
    
    # Check for specific values in the optimized code that indicate constant folding
    return ("x = 8" in optimized_code and 
            "y = 20" in optimized_code and 
            "z = 25.0" in optimized_code)

def test_unused_variable_removal():
    """Test unused variable removal optimization."""
    logger.info("Testing unused variable removal...")
    
    code = """
def process_data(data):
    # Unused variable
    unused_var = 42
    
    # Used variable
    result = data * 2
    
    return result
"""
    
    optimizer = RuleBasedOptimizer()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level='high')
    
    logger.info(f"Original code:\n{code}")
    logger.info(f"Optimized code:\n{optimized_code}")
    logger.info(f"Explanation: {explanation}")
    logger.info(f"Complexity: {original_complexity} -> {optimized_complexity}")
    logger.info("Applied rules:")
    for rule in optimizer.get_applied_rules():
        logger.info(f"  - {rule.get('type', 'unknown')}: {rule.get('description', '')}")
    
    logger.info("Unused variable removal test complete\n")
    return "unused_var" not in optimized_code

def test_dead_code_elimination():
    """Test dead code elimination optimization."""
    logger.info("Testing dead code elimination...")
    
    code = """
def get_value(condition):
    if True:
        return 10
    else:
        return 20
"""
    
    optimizer = RuleBasedOptimizer()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level='high')
    
    logger.info(f"Original code:\n{code}")
    logger.info(f"Optimized code:\n{optimized_code}")
    logger.info(f"Explanation: {explanation}")
    logger.info(f"Complexity: {original_complexity} -> {optimized_complexity}")
    logger.info("Applied rules:")
    for rule in optimizer.get_applied_rules():
        logger.info(f"  - {rule.get('type', 'unknown')}: {rule.get('description', '')}")
    
    logger.info("Dead code elimination test complete\n")
    return "else:" not in optimized_code

def test_loop_unrolling():
    """Test loop unrolling optimization."""
    logger.info("Testing loop unrolling...")
    
    code = """
def sum_small():
    total = 0
    for i in range(3):
        total += i
    return total
"""
    
    optimizer = RuleBasedOptimizer()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level='high')
    
    logger.info(f"Original code:\n{code}")
    logger.info(f"Optimized code:\n{optimized_code}")
    logger.info(f"Explanation: {explanation}")
    logger.info(f"Complexity: {original_complexity} -> {optimized_complexity}")
    logger.info("Applied rules:")
    for rule in optimizer.get_applied_rules():
        logger.info(f"  - {rule.get('type', 'unknown')}: {rule.get('description', '')}")
    
    logger.info("Loop unrolling test complete\n")
    return "range(3)" not in optimized_code

def test_combined_optimizations():
    """Test all optimizations combined."""
    logger.info("Testing combined optimizations...")
    
    code = """
def process_data(data):
    # Unused variable
    unused_var = 42
    
    # Constant folding
    x = 3 + 5
    y = 10 * 2
    
    # Dead code
    if True:
        result = x + y
    else:
        result = 0
    
    # Small loop
    total = 0
    for i in range(3):
        total += i
    
    return result + total
"""
    
    optimizer = RuleBasedOptimizer()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level='high')
    
    logger.info(f"Original code:\n{code}")
    logger.info(f"Optimized code:\n{optimized_code}")
    logger.info(f"Explanation: {explanation}")
    logger.info(f"Complexity: {original_complexity} -> {optimized_complexity}")
    logger.info("Applied rules:")
    for rule in optimizer.get_applied_rules():
        logger.info(f"  - {rule.get('type', 'unknown')}: {rule.get('description', '')}")
    
    logger.info("Combined optimizations test complete\n")
    
    # Check multiple optimizations were applied
    results = []
    results.append("unused_var" not in optimized_code)  # Unused variable removed
    results.append("8" in optimized_code)  # Constant folding applied
    results.append("else:" not in optimized_code)  # Dead code eliminated
    
    return all(results)

def run_all_tests():
    """Run all the tests and report results."""
    tests = [
        test_constant_folding,
        test_unused_variable_removal,
        test_dead_code_elimination,
        test_loop_unrolling,
        test_combined_optimizations
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            logger.error(f"Error in {test.__name__}: {str(e)}")
            results.append((test.__name__, False))
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    passed = 0
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        if result:
            passed += 1
        logger.info(f"{name}: {status}")
    
    logger.info("-"*50)
    logger.info(f"TOTAL: {passed}/{len(results)} tests passed")
    logger.info("="*50)
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 