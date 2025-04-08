import re
import ast
import time
import logging
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestStandalone")

class StandaloneOptimizer:
    """Simple optimizer to test pattern recognition and optimization features"""
    
    def __init__(self):
        self.improvements = []
        self.algorithm_patterns = self._load_algorithm_patterns()
    
    def _load_algorithm_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load algorithm patterns for recognition and optimization"""
        patterns = {
            "bubble_sort": {
                "pattern": r"def\s+\w+\s*\([^)]*\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):\s*(?:.*?\n)*?\s*if\s+(\w+)\s*\[\s*(\w+)\s*\]\s*>\s*\1\s*\[\s*\2\s*\+\s*1\s*\]",
                "optimized_algorithm": "sorting_algorithm",
                "optimized_code": """def sort_array(arr):
    \"\"\"
    Efficient implementation of sorting algorithm.
    Uses Python's built-in sorted() function, which implements Timsort.
    Time Complexity: O(n log n)
    \"\"\"
    return sorted(arr)
"""
            },
            "recursive_fibonacci": {
                "pattern": r"def\s+(\w+(?:fibonacci|fib|fibo)(?:\w*))?\s*\(\s*(\w+)\s*\):\s*(?:.*?\n)*?\s*if\s+\2\s*(?:<=|<)\s*\d+.*?return.*?(?:else\s*:|(?=return)).*?return\s+\1\s*\(\s*\2\s*-\s*1\s*\)\s*\+\s*\1\s*\(\s*\2\s*-\s*2\s*\)",
                "optimized_algorithm": "fibonacci",
                "optimized_code": """def fibonacci(n):
    \"\"\"
    Efficient implementation of Fibonacci sequence using dynamic programming.
    Time Complexity: O(n) instead of O(2^n) for recursive approach.
    
    Args:
        n: The position in the Fibonacci sequence to calculate
        
    Returns:
        The Fibonacci number at position n
    \"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
        
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
            }
        }
        
        return patterns
        
    def optimize(self, code: str) -> Tuple[str, str, str, str]:
        """Optimize the given code and return the results"""
        self.improvements = []
        
        # Try pattern-based optimization
        algorithm_match = self._recognize_algorithm(code)
        
        if algorithm_match:
            # Apply pattern-based optimization
            optimized_code = self._replace_with_optimized_algorithm(code, algorithm_match)
            
            explanation = f"Replaced {algorithm_match['name']} with optimized {algorithm_match['optimized_algorithm']}"
            
            # Add improvement
            self.improvements.append({
                'type': 'algorithm_replacement',
                'description': explanation,
                'category': 'performance'
            })
            
            return optimized_code, "O(n^2)", "O(n log n)", explanation
        
        # If no algorithm match, just return the original code
        return code, "O(?)", "O(?)", "No optimizations applied"
    
    def _recognize_algorithm(self, code: str) -> Optional[Dict[str, Any]]:
        """Recognize algorithm pattern in code"""
        for algo_name, algo_info in self.algorithm_patterns.items():
            if re.search(algo_info["pattern"], code, re.DOTALL):
                logger.info(f"Recognized {algo_name} algorithm pattern")
                return {
                    "name": algo_name,
                    "optimized_algorithm": algo_info["optimized_algorithm"],
                    "optimized_code": algo_info["optimized_code"]
                }
        
        return None
    
    def _replace_with_optimized_algorithm(self, code: str, algorithm_match: Dict[str, Any]) -> str:
        """Replace recognized algorithm with optimized version"""
        # Extract function name
        func_name = ""
        match = re.search(r"def\s+(\w+)\s*\(", code)
        if match:
            func_name = match.group(1)
        
        # Get parameter names
        param_names = []
        param_match = re.search(r"def\s+\w+\s*\(([^)]*)\)", code)
        if param_match:
            params = param_match.group(1)
            param_names = [p.strip().split(':')[0].split('=')[0].strip() for p in params.split(',') if p.strip()]
        
        # Adapt optimized code template
        optimized_code = algorithm_match["optimized_code"]
        
        # Replace function name
        if func_name:
            optimized_code = re.sub(r"def\s+(\w+)\s*\(", f"def {func_name}(", optimized_code)
        
        # Replace parameter names if possible
        if param_names:
            if algorithm_match["optimized_algorithm"] == "sorting_algorithm" and len(param_names) >= 1:
                optimized_code = optimized_code.replace("arr", param_names[0])
            elif algorithm_match["optimized_algorithm"] == "fibonacci" and len(param_names) >= 1:
                optimized_code = optimized_code.replace("n", param_names[0])
        
        # Check if the optimized code ends with proper newlines
        # Ensure code ends with exactly two newlines for proper spacing
        optimized_code = optimized_code.rstrip('\n')  # Remove any trailing newlines
        optimized_code += '\n\n'  # Add exactly two newlines
        
        return optimized_code
    
    def get_applied_rules(self) -> List[Dict[str, str]]:
        """Get list of improvements applied during optimization"""
        return self.improvements


def run_test(name, code):
    """Run a test on the given code and print the results"""
    print(f"\n===== Testing {name} =====")
    print(f"Original code:\n{code}\n")
    
    # Initialize the optimizer
    optimizer = StandaloneOptimizer()
    
    # Apply optimization
    optimized, original_complexity, optimized_complexity, explanation = optimizer.optimize(code)
    
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
    
    # Summary
    print(f"\n===== Test Summary =====")
    print(f"Successful optimizations: {success_count}/{total_tests}")
    
    return success_count == total_tests

if __name__ == "__main__":
    main() 