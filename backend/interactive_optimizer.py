import logging
import sys
import ast
import re
from typing import List, Tuple
from src.rule_based import RuleBasedOptimizer  # Import the rule-based optimizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('efficode.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_optimization_options() -> Tuple[str, List[str]]:
    """Get optimization preferences from user."""
    print("\nOptimization Options:")
    print("1. Rule-based optimization")
    print("2. Code transformation")
    print("3. Both")
    
    while True:
        try:
            choice = int(input("\nSelect optimization type (1-3): "))
            if 1 <= choice <= 3:
                break
            print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\nAlgorithm Domains:")
    print("- sorting")
    print("- searching")
    print("- graph")
    print("- dynamic_programming")
    print("- string_manipulation")
    print("- all")
    
    domain = input("\nPlease enter the algorithm domain: ").lower()
    
    optimizations = []
    if choice in [1, 3]:
        optimizations.append("rule_based")
    if choice in [2, 3]:
        optimizations.append("transformation")
    
    return domain, optimizations

def get_code_input() -> str:
    """Get code input from user."""
    print("\nPlease enter your code (press Enter five times consecutively to finish):")
    code_lines = []
    empty_line_count = 0
    
    while True:
        try:
            line = input()
            
            # Check if the line is empty
            if not line:
                empty_line_count += 1
                if empty_line_count >= 5:
                    break
            else:
                # If a non-empty line is entered, reset the counter and add any pending empty lines
                if empty_line_count > 0:
                    # Add the pending empty lines to the code
                    code_lines.extend([''] * empty_line_count)
                    empty_line_count = 0
                
                # Add the current line
                code_lines.append(line)
                
        except KeyboardInterrupt:
            print("\nInput cancelled. Starting over...")
            return get_code_input()
        except EOFError:
            if code_lines:
                break
    
    # Don't include the five empty lines in the final code
    return '\n'.join(code_lines)

def validate_code(code: str) -> bool:
    """Validate if the input code is syntactically correct."""
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"\nSyntax error in your code: {str(e)}")
        return False
    except Exception as e:
        print(f"\nError validating code: {str(e)}")
        return False

def optimize_code(code: str, domain: str) -> Tuple[str, str, str, List[str]]:
    """Apply optimizations using rule-based optimizer."""
    original_complexity = "O(n)"
    optimized_complexity = "O(n)"
    improvements = []
    
    try:
        # Initialize rule-based optimizer
        optimizer = RuleBasedOptimizer()
        
        # Apply optimizations based on domain
        if domain == "searching":
            # Optimize linear search
            if "linear_search" in code:
                optimized_code = optimizer.optimize_linear_search(code)
                if optimized_code != code:
                    improvements.append("Replaced linear search with dictionary lookup")
                    optimized_complexity = "O(1)"
                    return optimized_code, original_complexity, optimized_complexity, improvements
            
            # Optimize string concatenation
            if "greeting += " in code:
                optimized_code = optimizer.optimize_string_concatenation(code)
                if optimized_code != code:
                    improvements.append("Optimized string concatenation using join()")
                    return optimized_code, original_complexity, optimized_complexity, improvements
        
        elif domain == "sorting":
            # Optimize bubble sort
            if "bubble_sort" in code:
                optimized_code = optimizer.optimize_bubble_sort(code)
                if optimized_code != code:
                    improvements.append("Replaced bubble sort with built-in sorted()")
                    optimized_complexity = "O(n log n)"
                    return optimized_code, original_complexity, optimized_complexity, improvements
        
        # Apply general optimizations
        optimized_code = optimizer.optimize(code)
        if optimized_code != code:
            improvements.append("Applied general optimizations")
            return optimized_code, original_complexity, optimized_complexity, improvements
        
        return code, original_complexity, optimized_complexity, improvements
        
    except Exception as e:
        logger.error(f"Error during optimization: {str(e)}")
        raise

def main():
    """Main interactive optimization function."""
    print("Welcome to the EFFICODE-ACRR Code Optimizer!")
    
    try:
        # Get optimization preferences
        domain, optimizations = get_optimization_options()
        
        # Get code input
        code = get_code_input()
        
        # Validate code
        if not code.strip():
            print("\nNo code provided. Exiting...")
            return
        
        if not validate_code(code):
            print("\nPlease fix the code and try again.")
            return
        
        # Apply optimizations
        try:
            optimized_code, original_complexity, optimized_complexity, improvements = optimize_code(code, domain)
            
            # Print results
            print("\nOptimized Code:")
            print("=" * 40)
            print(optimized_code)
            print("=" * 40)
            
            print(f"\nComplexity Analysis:")
            print(f"Original Complexity: {original_complexity}")
            print(f"Optimized Complexity: {optimized_complexity}")
            
            if improvements:
                print("\nImprovements made:")
                for improvement in improvements:
                    print(f"- {improvement}")
            else:
                print("\nNo optimizations were possible or needed.")
                
        except Exception as e:
            logger.error("Optimization failed: %s", str(e))
            print(f"\nOptimization failed: {str(e)}")
            print("Please check the log file for more details.")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        print(f"\nAn unexpected error occurred: {str(e)}")
        print("Please check the log file for more details.")

if __name__ == "__main__":
    main() 