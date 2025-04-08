"""
Verification script to test that the optimizers are working correctly
with AST transformations disabled and neural models disabled.
"""

import logging
import time
from src.rule_based import RuleBasedOptimizer
from src.codebert_optimizer import CodeBERTOptimizer, apply_codebert_optimization

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test code samples
FIBONACCI_CODE = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""

BUBBLE_SORT_CODE = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

LIST_BUILDING_CODE = """
def process_data(items):
    results = []
    for item in items:
        results.append(item * 2)
    return results
"""

def test_rule_based_optimizer():
    """Test the rule-based optimizer"""
    logger.info("Testing Rule-Based Optimizer...")
    optimizer = RuleBasedOptimizer()
    
    # Test with bubble sort
    start_time = time.time()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(BUBBLE_SORT_CODE)
    elapsed = time.time() - start_time
    
    logger.info(f"Rule-based optimization completed in {elapsed:.3f}s")
    logger.info(f"Original complexity: {original_complexity}")
    logger.info(f"Optimized complexity: {optimized_complexity}")
    logger.info(f"Explanation: {explanation}")
    
    print("\nOriginal code:")
    print(BUBBLE_SORT_CODE)
    print("\nOptimized code:")
    print(optimized_code)
    
    improvements = optimizer.get_applied_rules()
    logger.info(f"Applied {len(improvements)} improvements")
    for imp in improvements:
        if isinstance(imp, dict):
            logger.info(f"- {imp.get('type', 'unknown')}: {imp.get('description', '')}")
        else:
            logger.info(f"- {imp.type}: {imp.description}")
    
    return len(improvements) > 0

def test_codebert_optimizer():
    """Test the CodeBERT optimizer"""
    logger.info("Testing CodeBERT Optimizer...")
    optimizer = CodeBERTOptimizer(use_neural_model=False)
    
    # Test with fibonacci code (pattern-based optimization)
    start_time = time.time()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(FIBONACCI_CODE)
    elapsed = time.time() - start_time
    
    logger.info(f"CodeBERT optimization completed in {elapsed:.3f}s")
    logger.info(f"Original complexity: {original_complexity}")
    logger.info(f"Optimized complexity: {optimized_complexity}")
    logger.info(f"Explanation: {explanation}")
    
    print("\nOriginal code:")
    print(FIBONACCI_CODE)
    print("\nOptimized code:")
    print(optimized_code)
    
    improvements = optimizer.get_applied_rules()
    logger.info(f"Applied {len(improvements)} improvements")
    for imp in improvements:
        if isinstance(imp, dict):
            logger.info(f"- {imp.get('type', 'unknown')}: {imp.get('description', '')}")
        else:
            logger.info(f"- {imp.type}: {imp.description}")
    
    # Test with list building code (regex-based optimization)
    start_time = time.time()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(LIST_BUILDING_CODE)
    elapsed = time.time() - start_time
    
    logger.info(f"CodeBERT list optimization completed in {elapsed:.3f}s")
    logger.info(f"Original complexity: {original_complexity}")
    logger.info(f"Optimized complexity: {optimized_complexity}")
    logger.info(f"Explanation: {explanation}")
    
    print("\nOriginal list code:")
    print(LIST_BUILDING_CODE)
    print("\nOptimized list code:")
    print(optimized_code)
    
    return len(improvements) > 0

def test_app_integration():
    """Test the apply_codebert_optimization function directly"""
    logger.info("Testing app integration with apply_codebert_optimization...")
    
    # Test with fibonacci code
    start_time = time.time()
    optimized_code, improvements, errors = apply_codebert_optimization(FIBONACCI_CODE)
    elapsed = time.time() - start_time
    
    logger.info(f"Integration test completed in {elapsed:.3f}s")
    
    print("\nOriginal code:")
    print(FIBONACCI_CODE)
    print("\nOptimized code:")
    print(optimized_code)
    
    logger.info(f"Applied {len(improvements)} improvements")
    for imp in improvements:
        if isinstance(imp, dict):
            logger.info(f"- {imp.get('type', 'unknown')}: {imp.get('description', '')}")
        else:
            logger.info(f"- {imp.type}: {imp.description}")
    
    if errors:
        logger.error(f"Encountered {len(errors)} errors:")
        for error in errors:
            logger.error(f"- {error}")
    
    return len(improvements) > 0 and len(errors) == 0

def main():
    """Run all tests"""
    logger.info("Starting verification tests...")
    
    rule_based_success = test_rule_based_optimizer()
    logger.info(f"Rule-based test {'succeeded' if rule_based_success else 'failed'}")
    
    codebert_success = test_codebert_optimizer()
    logger.info(f"CodeBERT test {'succeeded' if codebert_success else 'failed'}")
    
    integration_success = test_app_integration()
    logger.info(f"Integration test {'succeeded' if integration_success else 'failed'}")
    
    overall_success = rule_based_success and codebert_success and integration_success
    logger.info(f"Overall verification {'PASSED' if overall_success else 'FAILED'}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 