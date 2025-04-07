"""
Direct test script for the rule-based optimizer
"""
import json
import logging
import time
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the rule-based optimizer
try:
    from src.rule_based import RuleBasedOptimizer
    print("Successfully imported RuleBasedOptimizer")
except ImportError:
    print("Failed to import RuleBasedOptimizer from src.rule_based")
    try:
        from rule_based import RuleBasedOptimizer
        print("Successfully imported RuleBasedOptimizer from rule_based")
    except ImportError:
        print("Failed to import RuleBasedOptimizer from both locations")
        sys.exit(1)

def main():
    """Main test function"""
    print("Starting direct test of rule-based optimizer")
    
    # Read the test input
    try:
        with open('test_input.json', 'r') as f:
            test_data = json.load(f)
            print("Successfully loaded test_input.json")
    except Exception as e:
        print(f"Error loading test_input.json: {e}")
        return
    
    # Extract the code
    code = test_data.get('code', '')
    if not code:
        print("No code found in test_input.json")
        return
    
    print("Input code:")
    print("-" * 40)
    print(code)
    print("-" * 40)
    
    # Initialize the optimizer
    optimizer = RuleBasedOptimizer()
    print("Initialized RuleBasedOptimizer")
    
    # Time the optimization
    start_time = time.time()
    
    # Apply optimization
    try:
        result = optimizer.optimize(code)
        print("Successfully applied optimization")
    except Exception as e:
        print(f"Error applying optimization: {e}")
        return
    
    # Extract results
    optimized_code = result.get('optimized_code', code)
    applied_rules = result.get('applied_rules', [])
    
    # Print results
    print(f"Optimization completed in {time.time() - start_time:.4f} seconds")
    print(f"Applied {len(applied_rules)} rules")
    
    print("Applied rules:")
    for rule in applied_rules:
        print(f"- {rule['rule']}: {rule['description']}")
    
    print("\nOptimized code:")
    print("-" * 40)
    print(optimized_code)
    print("-" * 40)
    
    # Check if code was changed
    if optimized_code == code:
        print("No changes were made to the code")
    else:
        print("Code was successfully optimized")

if __name__ == '__main__':
    main() 