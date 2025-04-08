#!/usr/bin/env python3
"""
Test script for CodeBERT Optimizer

This script evaluates the functionality of the CodeBERT optimizer,
including its ability to recognize algorithms, improve code quality,
and integrate with the rule-based optimizer.
"""

import os
import sys
import logging
from typing import Dict, Any
from src.codebert_optimizer import CodeBERTOptimizer, NEURAL_MODEL_AVAILABLE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CodeBERTTest")

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Mock RuleBasedOptimizer to avoid dependency issues
class MockRuleBasedOptimizer:
    def optimize(self, code, level='medium'):
        return code, "O(n)", "O(n)", "No optimizations applied in mock"
    
    def get_applied_rules(self):
        return []

# Patch the import in codebert_optimizer
sys.modules['src.rule_based'] = type('module', (), {'RuleBasedOptimizer': MockRuleBasedOptimizer})

def run_test(name: str, code: str, level: str = "medium") -> Dict[str, Any]:
    """
    Run a test case with the CodeBERT optimizer
    
    Args:
        name: Test case name
        code: Code to optimize
        level: Optimization level
        
    Returns:
        Dictionary with test results
    """
    print(f"\n===== Testing {name} =====")
    print(f"Original code:\n{code}\n")
    
    # Initialize the optimizer
    optimizer = CodeBERTOptimizer(use_neural_model=False)
    
    # Apply optimization
    optimized, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level)
    
    print(f"Optimized code:\n{optimized}\n")
    print(f"Complexity: {original_complexity} -> {optimized_complexity}")
    print(f"Explanation: {explanation}")
    
    # Get improvements
    improvements = optimizer.get_applied_rules()
    if improvements:
        print("\nImprovements applied:")
        for improvement in improvements:
            print(f"- {improvement['type']}: {improvement['description']}")
    else:
        print("\nNo improvements applied")
    
    print("=" * 50)
    return optimized != code

def main():
    """Run tests for different optimization scenarios"""
    success_count = 0
    total_tests = 0
    
    # Test recursive Fibonacci optimization
    fib_code = """
def recursive_fibonacci(n):
    if n <= 1:
        return n
    else:
        return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)
"""
    total_tests += 1
    if run_test("Recursive Fibonacci", fib_code):
        success_count += 1
    
    # Test bubble sort optimization
    sort_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    total_tests += 1
    if run_test("Bubble Sort", sort_code):
        success_count += 1
    
    # Test list building optimization
    list_code = """
def process_data(items):
    # Build a list
    results = []
    for item in items:
        results.append(item * 2)
    return results
"""
    total_tests += 1
    if run_test("List Building", list_code):
        success_count += 1
    
    # Test variable naming optimization
    var_code = """
def calculate(a, x, y):
    n = len(a)
    s = 0
    for i in range(n):
        if a[i] > x:
            s += a[i] * y
    return s
"""
    total_tests += 1
    if run_test("Variable Naming", var_code):
        success_count += 1
    
    # Summary
    print(f"\n===== Test Summary =====")
    print(f"Successful optimizations: {success_count}/{total_tests}")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 