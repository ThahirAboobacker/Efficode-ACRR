import os
import sys
import argparse
from typing import Dict, List, Tuple, Any, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from backend.src.data_processing import load_dataset
from backend.src.feature_extraction import extract_features
from backend.src.rule_based import optimize_with_rules
from backend.src.code_transformation import apply_transformations
from backend.src.complexity_analyzer import analyze_complexity, compare_complexity
from backend.src.explanation_generator import generate_explanation

def optimize_code(code: str, use_ml: bool = True) -> Tuple[str, str, Dict[str, Any]]:
    """
    Main function to optimize Python code.
    
    Args:
        code: Python code string to optimize
        use_ml: Whether to use ML-based optimization in addition to rule-based
        
    Returns:
        Tuple of (optimized_code, explanation, complexity_comparison)
    """
    print("Starting code optimization process...")
    
    # Step 1: Apply rule-based optimizations
    print("Applying rule-based optimizations...")
    optimized_code, applied_rules = optimize_with_rules(code)
    
    # Step 2: Apply ML-based optimizations if requested
    if use_ml:
        print("Applying ML-based optimizations...")
        try:
            # This would be implemented to use CodeBERT for optimization
            # optimized_code, ml_rules = optimize_with_ml(optimized_code)
            # applied_rules.extend(ml_rules)
            pass
        except Exception as e:
            print(f"Warning: ML-based optimization failed: {str(e)}")
    
    # Step 3: Analyze and compare complexity
    print("Analyzing code complexity...")
    original_complexity = analyze_complexity(code)
    optimized_complexity = analyze_complexity(optimized_code)
    complexity_comparison = compare_complexity(original_complexity, optimized_complexity)
    
    # Step 4: Generate explanation
    print("Generating explanation...")
    explanation = generate_explanation(code, optimized_code, applied_rules, complexity_comparison)
    
    print("Code optimization completed successfully!")
    return optimized_code, explanation, complexity_comparison

def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Python Code Optimizer")
    parser.add_argument("--file", type=str, help="Path to Python file to optimize")
    parser.add_argument("--code", type=str, help="Python code string to optimize")
    parser.add_argument("--output", type=str, help="Path to output file")
    parser.add_argument("--no-ml", action="store_true", help="Disable ML-based optimization")
    
    args = parser.parse_args()
    
    # Get the code to optimize
    code = None
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        print("Error: Either --file or --code must be provided")
        parser.print_help()
        return
    
    # Optimize the code
    optimized_code, explanation, complexity_comparison = optimize_code(code, not args.no_ml)
    
    # Output the results
    if args.output:
        with open(args.output, "w") as f:
            f.write(optimized_code)
        print(f"Optimized code written to {args.output}")
    else:
        print("\nOptimized Code:")
        print(optimized_code)
    
    print("\nExplanation:")
    print(explanation)
    
    print("\nComplexity Comparison:")
    for key, value in complexity_comparison.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 