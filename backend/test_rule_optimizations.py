"""
Test script to verify rule-based optimizations are working correctly.
"""
import sys
import logging
from src.rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test cases for various optimizations
TEST_CASES = {
    "fibonacci": """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
""",

    "bubble_sort": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
""",

    "dead_code_elimination": """
def test_dead_code():
    if True:
        x = 10
        return x
        print("This will never execute")  # Dead code after return
    else:
        print("This will never execute")  # Unreachable else branch
    
    print("This will never execute")  # Dead code after function return
""",

    "unused_variable_removal": """
def test_unused_vars():
    x = 10  # Used variable
    y = 20  # Unused variable
    z = 30  # Unused variable
    return x
""",

    "constant_folding": """
def test_constant_folding():
    x = 2 * 3 + 4  # Should be folded to 10
    y = 10 / 2     # Should be folded to 5.0
    z = 2 ** 8     # Should be folded to 256
    return x + y + z
""",

    "loop_optimization": """
def test_loop_optimization():
    items = ["a", "b", "c"]
    result = []
    for i in range(len(items)):
        result.append(items[i].upper())
    return result
""",

    "repeated_computation": """
def test_repeated_computation():
    x = 10
    y = 20
    # The expensive_operation(x+y) computation is repeated
    result1 = expensive_operation(x+y) * 2
    result2 = expensive_operation(x+y) * 3
    return result1 + result2
    
def expensive_operation(n):
    return n * n
"""
}

def test_optimizations():
    """Run all optimization tests."""
    optimizer = RuleBasedOptimizer()
    results = {}
    
    # Test each case
    for name, code in TEST_CASES.items():
        logger.info(f"Testing optimization: {name}")
        print(f"\n{'='*20} TESTING {name} {'='*20}")
        print("\nOriginal code:")
        print(code)
        
        # Apply optimization
        optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level="high")
        
        print("\nOptimized code:")
        print(optimized_code)
        
        # Get applied rules
        improvements = optimizer.get_applied_rules()
        print("\nApplied optimizations:")
        for improvement in improvements:
            if isinstance(improvement, dict):
                print(f"- {improvement.get('type', 'unknown')}: {improvement.get('description', '')}")
            else:
                print(f"- {improvement.type}: {improvement.description}")
        
        # Check if optimization was successful
        success = len(improvements) > 0
        print(f"\nOptimization successful: {success}")
        results[name] = success
    
    # Print overall results
    print("\n\n" + "="*50)
    print("OPTIMIZATION TEST RESULTS")
    print("="*50)
    for name, success in results.items():
        print(f"{name:30} {'✓' if success else '✗'}")
    
    # Return success if all tests passed
    return all(results.values())

if __name__ == "__main__":
    success = test_optimizations()
    print(f"\nOverall result: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1) 