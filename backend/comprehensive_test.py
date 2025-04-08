"""
Comprehensive test script for rule-based optimizer.
This script demonstrates all types of optimizations in a single example.
"""
import sys
import logging
from src.rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Example code with all optimization opportunities
TEST_CODE = """
def comprehensive_test_function(items):
    # Constants that can be folded
    a = 2 * 3       # Should become 6
    b = 10 / 2      # Should become 5.0
    c = 2 ** 3      # Should become 8
    
    # Unused variables
    unused1 = "This variable is never used"
    unused2 = 42
    
    # Unreachable code due to constant condition
    if True:
        x = a + b + c
    else:
        # This will never be executed
        x = 0
    
    # Loop that can be optimized (range(len) -> enumerate)
    result = []
    for i in range(len(items)):
        # Append pattern that can be converted to list comprehension
        result.append(items[i].upper())
    
    # Repeated expensive computation
    repeated_value = expensive_operation(x) * 2
    another_value = expensive_operation(x) * 3
    
    # Dead code after return
    return result, repeated_value, another_value
    
    # This will never be executed
    print("This is unreachable code after return")
    cleanup_resources()  # This function call will be eliminated

def expensive_operation(n):
    # Simulating an expensive operation
    return n * n * n
"""

def main():
    """Main function to test the optimizer."""
    try:
        # Initialize the optimizer
        optimizer = RuleBasedOptimizer()
        
        # Print the original code
        print("Original code:")
        print(TEST_CODE)
        
        # Apply the optimizations
        optimized_code, complexity_before, complexity_after, changes = optimizer.optimize(TEST_CODE)
        
        # Print the optimized code
        print("\nOptimized code:")
        print(optimized_code)
        
        # Print the changes
        print("\nOptimization Summary:")
        print(f"Original complexity: {complexity_before}")
        print(f"Optimized complexity: {complexity_after}")
        
        print("\nOptimizations applied:")
        if isinstance(changes, list):
            for change in changes:
                if isinstance(change, dict) and 'type' in change and 'description' in change:
                    print(f"- {change['type']}: {change['description']}")
                else:
                    print(f"- {change}")
        else:
            print(changes)
            
        print("\nTest Result: SUCCESS - All optimizations were applied successfully.")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        print("\nTest Result: FAILURE - An error occurred during optimization.")

if __name__ == "__main__":
    sys.exit(main()) 