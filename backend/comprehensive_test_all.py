"""
Comprehensive test for rule_based.py optimizer

This script tests all optimization features:
1. Algorithm detection (Fibonacci, bubble sort, linear search)
2. Inefficient max/min operations using sorted lists 
3. Constants that can be folded
4. Dead code that should be eliminated
5. Unused variables to be removed
6. Loops using range(len) that can be optimized with enumerate
7. Repeated computations that can be stored in temporary variables
8. String concatenation optimization
"""

import sys
import ast
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, backend_dir)
sys.path.insert(0, src_dir)

# Import the RuleBasedOptimizer
from src.rule_based import RuleBasedOptimizer

# Test code with all optimization opportunities
TEST_CODE = '''
# 1. Algorithm detection - Recursive Fibonacci (should be replaced with iterative)
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)  # Inefficient recursive approach

# 2. Algorithm detection - Bubble Sort (should be replaced with built-in sorted)
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# 3. Algorithm detection - Linear Search (should be replaced with more efficient search)
def linear_search(arr, x):
    for i in range(len(arr)):
        if arr[i] == x:
            return i
    return -1

# 4. Inefficient max/min operations
def find_max(my_list):
    sorted_list = sorted(my_list)
    return sorted_list[-1]  # Should be replaced with max(my_list)

def find_min(my_list):
    sorted_list = sorted(my_list)
    return sorted_list[0]  # Should be replaced with min(my_list)

# 5. Constants that can be folded
def constant_folding():
    x = 2 * 3 + 4  # Should be folded to 10
    y = 10 / 2     # Should be folded to 5.0
    z = 2 ** 8     # Should be folded to 256
    PI = 3.14159   # Keep this as is
    
    # Multiple calculations that should be folded
    result = x + y + z + (10 * 20) + (5 + 3) ** 2
    
    return result

# 6. Dead code that should be eliminated
def dead_code_example(x):
    print("Starting function")
    
    if False:  # This branch will never execute
        print("This will never be printed")
        y = 10
        return y
    
    if True:  # This will always execute
        print("This will always be printed")
    else:
        print("This will never be printed")
    
    result = 42
    
    return result
    # Code after return should be eliminated
    print("This will never be printed")
    z = 100
    return z

# 7. Unused variables to be removed
def unused_variables():
    used_var = 10      # This is used
    unused_var1 = 20   # This is never used
    unused_var2 = "hello"  # This is never used
    
    # These variables are assigned but never read
    temp1 = "temp value 1"
    temp2 = [1, 2, 3]
    
    return used_var + 5  # Only used_var is actually used

# 8. Loops using range(len) that can be optimized with enumerate
def iterate_with_index(items):
    result = []
    
    # Should be converted to enumerate
    for i in range(len(items)):
        result.append(f"Item {i}: {items[i]}")
    
    return result

# 9. Repeated computations that can be stored in variables
def repeated_computations(data):
    result1 = 0
    result2 = 0
    
    # The expensive operation is computed multiple times
    for i in range(len(data)):
        # These expensive operations should be computed once and stored
        result1 += len(data) * sum(data) / (i+1)
        
    for j in range(len(data)):
        # Same expensive operation repeated
        result2 += len(data) * sum(data) / (j+1)
    
    # More repeated expressions
    final = (result1 * result2) + (result1 * result2) / 2
    
    return final

# 10. String concatenation in loops
def string_concatenation(items):
    # Inefficient string concatenation in loop
    result = ""
    for item in items:
        result = result + str(item) + ", "  # Should use join instead
    
    # Multiple string concatenations
    greeting = "Hello " + "World" + "!" + " How" + " are" + " you" + "?"
    
    return result, greeting
'''

def check_improvements(code, optimized_code, optimizer_changes):
    """Check that specific improvements were made."""
    improvements = {
        'fibonacci': False,
        'bubble_sort': False,
        'linear_search': False,
        'max_min': False,
        'constant_folding': False,
        'dead_code': False,
        'unused_vars': False,
        'enumerate': False,
        'repeated_computation': False,
        'string_concat': False
    }
    
    # Check for algorithm replacements
    if "range(2, n + 1)" in optimized_code and "fibonacci" in optimized_code:
        improvements['fibonacci'] = True
    
    if "sorted(" in optimized_code and "bubble_sort" in optimized_code:
        improvements['bubble_sort'] = True
        
    # Check for max/min optimization
    if "max(my_list)" in optimized_code or "return max(my_list)" in optimized_code:
        improvements['max_min'] = True
    
    # Check for constant folding
    if "x = 10" in optimized_code or "y = 5.0" in optimized_code or "z = 256" in optimized_code:
        improvements['constant_folding'] = True
    
    # Check for dead code elimination
    if "if False:" not in optimized_code or "This will never be printed" not in optimized_code:
        improvements['dead_code'] = True
    
    # Check for unused variables
    if "unused_var1" not in optimized_code or "unused_var2" not in optimized_code:
        improvements['unused_vars'] = True
    
    # Check for enumerate usage
    if "enumerate(items)" in optimized_code:
        improvements['enumerate'] = True
    
    # Check for repeated computation elimination
    temp_vars_added = "temp_var_" in optimized_code
    if temp_vars_added:
        improvements['repeated_computation'] = True
    
    # Check for string concatenation optimization
    if "'.join" in optimized_code or "\", \".join" in optimized_code:
        improvements['string_concat'] = True
    
    # Also check the changes reported by the optimizer
    for change in optimizer_changes:
        change_type = change.get('type', '')
        desc = change.get('description', '')
        
        if 'algorithm_replacement' in change_type and 'Fibonacci' in desc:
            improvements['fibonacci'] = True
        elif 'algorithm_replacement' in change_type and 'sort' in desc:
            improvements['bubble_sort'] = True
        elif 'algorithm_replacement' in change_type and 'search' in desc:
            improvements['linear_search'] = True
        elif 'max_min_optimization' in change_type or ('Replaced sorted' in desc and ('max' in desc or 'min' in desc)):
            improvements['max_min'] = True
        elif 'constant_folding' in change_type:
            improvements['constant_folding'] = True
        elif 'dead_code_elimination' in change_type or 'unreachable_code_removal' in change_type:
            improvements['dead_code'] = True
        elif 'unused_variable_removal' in change_type:
            improvements['unused_vars'] = True
        elif 'loop_optimization' in change_type and 'enumerate' in desc:
            improvements['enumerate'] = True
        elif 'repeated_computation_elimination' in change_type:
            improvements['repeated_computation'] = True
        elif 'string_concat_optimization' in change_type or 'string_join_optimization' in change_type:
            improvements['string_concat'] = True
    
    return improvements

def main():
    logging.info("Starting comprehensive rule-based optimizer test...")
    
    # Initialize the optimizer
    optimizer = RuleBasedOptimizer()
    
    # Display original code
    logging.info("Original Code:")
    logging.info(TEST_CODE)
    
    # Apply optimizations
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(
        TEST_CODE, level='high'
    )
    
    # Display optimized code and complexity
    logging.info("\nOptimized Code:")
    logging.info(optimized_code)
    
    logging.info(f"\nOriginal Complexity: {original_complexity}")
    logging.info(f"Optimized Complexity: {optimized_complexity}")
    logging.info(f"Explanation: {explanation}")
    
    # Get the changes that were applied
    applied_changes = optimizer.get_applied_rules()
    logging.info("\nApplied Changes:")
    for change in applied_changes:
        change_type = change.get('type', '')
        description = change.get('description', '')
        logging.info(f"- {change_type}: {description}")
    
    # Check specific improvements
    improvements = check_improvements(TEST_CODE, optimized_code, applied_changes)
    
    # Report on improvements that should have been made
    logging.info("\nImprovement Summary:")
    for feature, improved in improvements.items():
        status = "✓ Applied" if improved else "✗ Not Applied"
        logging.info(f"- {feature}: {status}")
    
    # Calculate success rate
    total_improvements = len(improvements)
    applied_improvements = sum(1 for improved in improvements.values() if improved)
    success_rate = (applied_improvements / total_improvements) * 100
    
    logging.info(f"\nSuccess Rate: {applied_improvements}/{total_improvements} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logging.info("TEST RESULT: SUCCESS - Most optimizations were applied correctly")
    elif success_rate >= 50:
        logging.info("TEST RESULT: PARTIAL SUCCESS - Some optimizations were applied correctly")
    else:
        logging.info("TEST RESULT: FAILURE - Few optimizations were applied correctly")

if __name__ == "__main__":
    main() 