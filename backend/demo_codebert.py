#!/usr/bin/env python3
"""
EFFICODE-ACRR CodeBERT Optimizer Demo Script

This script demonstrates the capabilities of the CodeBERT optimizer, including:
1. How to install the required dependencies for the neural model
2. How to optimize code using different optimization levels
3. How to compare results with and without the neural model

Usage:
  python demo_codebert.py [--install-deps] [--use-neural]

Options:
  --install-deps    Install neural model dependencies (torch, transformers)
  --use-neural      Enable neural model optimization if dependencies are installed
"""

import os
import sys
import time
import logging
import argparse
import subprocess
import traceback
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def install_dependencies():
    """Install the required dependencies for the neural model"""
    logger.info("Installing neural model dependencies (torch, transformers)...")
    
    try:
        # Check if pip is available
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        
        # Install dependencies
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "transformers"
        ])
        
        logger.info("Dependencies installed successfully!")
        logger.info("Please restart the script with --use-neural to use the neural model")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing dependencies: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during installation: {e}")
        logger.error(traceback.format_exc())
        return False

def print_optimization_results(title: str, code: str, optimizer, level: str = "medium"):
    """
    Optimize code and print the results
    
    Args:
        title: Title of the optimization case
        code: Code to optimize
        optimizer: CodeBERT optimizer instance
        level: Optimization level
    """
    print(f"\n{'=' * 80}")
    print(f"{title} (Level: {level})")
    print(f"{'=' * 80}")
    
    # Record start time
    start_time = time.time()
    
    # Print original code
    print("\nORIGINAL CODE:")
    print(f"```python\n{code}\n```")
    
    # Optimize the code
    try:
        optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level)
        improvements = optimizer.get_applied_rules()
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Print optimized code
        print("\nOPTIMIZED CODE:")
        print(f"```python\n{optimized_code}\n```")
        
        # Print results
        print("\nOPTIMIZATION RESULTS:")
        print(f"Time: {elapsed_time:.3f} seconds")
        print(f"Complexity: {original_complexity} → {optimized_complexity}")
        print(f"Explanation: {explanation}")
        
        if improvements:
            print("\nIMPROVEMENTS:")
            for imp in improvements:
                print(f"- {imp['description']} ({imp['category']})")
        else:
            print("\nNo improvements were identified")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        logger.error(f"Error during optimization: {e}")
        logger.error(traceback.format_exc())

def main():
    """Main demo function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="CodeBERT Optimizer Demo")
    parser.add_argument("--install-deps", action="store_true", help="Install neural model dependencies")
    parser.add_argument("--use-neural", action="store_true", help="Enable neural model optimization")
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        if install_dependencies():
            return
    
    # Import the CodeBERT optimizer
    try:
        from src.codebert_optimizer import CodeBERTOptimizer, NEURAL_MODEL_AVAILABLE
        logger.info(f"Successfully imported CodeBERT Optimizer (neural available: {NEURAL_MODEL_AVAILABLE})")
    except ImportError as e:
        logger.error(f"Failed to import CodeBERT Optimizer: {str(e)}")
        sys.exit(1)
    
    # Initialize the optimizer
    use_neural = args.use_neural and NEURAL_MODEL_AVAILABLE
    optimizer = CodeBERTOptimizer(use_neural_model=use_neural)
    
    logger.info(f"CodeBERT Optimizer Demo (Neural model: {'enabled' if use_neural else 'disabled'})")
    
    # Define test cases
    test_cases = [
        {
            "title": "Bubble Sort Algorithm",
            "code": """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr""",
            "level": "medium"
        },
        {
            "title": "Recursive Fibonacci",
            "code": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
            "level": "medium"
        },
        {
            "title": "Code Quality Improvement",
            "code": """def clean_data(x, y):
    # Initialize empty list
    z = []
    # Loop through each element
    for i in range(len(x)):
        # Filter values > 10
        if x[i] > 10:
            # Apply transformation and append
            z.append(x[i] * y)
    # Return the result
    return z""",
            "level": "high"
        },
        {
            "title": "List Operations",
            "code": """def filter_and_double_evens(numbers):
    result = []
    for n in numbers:
        if n % 2 == 0:
            result.append(n * 2)
    return result""",
            "level": "medium"
        },
        {
            "title": "Merge Sort Implementation",
            "code": """def merge_sort(arr):
    if len(arr) <= 1:
        return arr
        
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    left_half = merge_sort(left_half)
    right_half = merge_sort(right_half)
    
    return merge(left_half, right_half)
    
def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result""",
            "level": "high"
        }
    ]
    
    # Run test cases
    for case in test_cases:
        print_optimization_results(
            case["title"],
            case["code"],
            optimizer,
            case["level"]
        )
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"CodeBERT Optimizer Demo completed (Neural model: {'enabled' if use_neural else 'disabled'})")
    
    if not NEURAL_MODEL_AVAILABLE:
        print("\nTo enable the neural model capabilities:")
        print("1. Install the required dependencies:")
        print("   python demo_codebert.py --install-deps")
        print("2. Run the demo with neural model enabled:")
        print("   python demo_codebert.py --use-neural")

if __name__ == "__main__":
    main() 