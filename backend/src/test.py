"""
Comprehensive Test Suite for Rule-Based Code Optimizer

This script tests the rule-based optimization system against various Python code patterns
to evaluate code optimization effectiveness.
"""

import os
import sys
import time
import logging
import difflib
import tempfile
from typing import Dict, List, Tuple, Any

# Import the rule-based optimizer
from rule_based import apply_optimization_rules

# Compatibility wrapper for the functions needed by test suite
def optimize_code(code: str) -> Tuple[str, List[Dict[str, Any]], int]:
    """
    Wrapper around apply_optimization_rules to maintain backward compatibility
    
    Args:
        code: Python code as string
        
    Returns:
        Tuple of (optimized_code, patterns_applied, optimization_count)
    """
    optimized_code, changes_made = apply_optimization_rules(code)
    
    # Convert string changes to the expected dictionary format
    pattern_dicts = []
    for change in changes_made:
        pattern_dicts.append({
            "name": change,
            "severity": "medium",
            "optimization": "applied",
            "lines": [1, 1]  # Default line numbers
        })
    
    return optimized_code, pattern_dicts, len(changes_made)

def detect_inefficient_patterns(code: str) -> List[Dict[str, Any]]:
    """
    Compatibility function for detecting inefficient patterns
    
    Args:
        code: Python code as string
        
    Returns:
        List of detected patterns as dictionaries
    """
    # Use optimization function to get changes and convert to pattern format
    _, changes_made = apply_optimization_rules(code)
    
    # Convert to expected pattern format
    patterns = []
    for change in changes_made:
        patterns.append({
            "name": change,
            "severity": "medium",
            "optimization": "recommended",
            "lines": [1, 1]  # Default line numbers
        })
    
    return patterns

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Test cases by optimization category
TEST_CASES = {
    "Variable Simplifications": [
        {
            "name": "Remove Unused Variables",
            "code": """
def func():
    x = 10  # This is unused
    y = 5
    print(y)
    return y
""",
            "expected": """
def func():
    y = 5
    print(y)
    return y
"""
        },
        {
            "name": "Inline Single-Use Variables",
            "code": """
def calculate():
    base = 10
    temp = base * 2
    return temp
""",
            "expected": """
def calculate():
    base = 10
    return base * 2
"""
        },
        {
            "name": "Remove Redundant Assignments",
            "code": """
def process():
    value = 5
    value = 10
    return value
""",
            "expected": """
def process():
    value = 10
    return value
"""
        }
    ],
    
    "Loop Optimizations": [
        {
            "name": "Simplify range(len()) Loops",
            "code": """
def process_items(items):
    for i in range(len(items)):
        print(items[i])
""",
            "expected": """
def process_items(items):
    for item in items:
        print(item)
"""
        },
        {
            "name": "Replace List Appends with Comprehension",
            "code": """
def get_squares(numbers):
    result = []
    for num in numbers:
        result.append(num * num)
    return result
""",
            "expected": """
def get_squares(numbers):
    return [num * num for num in numbers]
"""
        },
        {
            "name": "Remove Empty Loops",
            "code": """
def wait_function():
    for _ in range(100):
        pass
    return True
""",
            "expected": """
def wait_function():
    return True
"""
        }
    ],
    
    "Conditional Simplifications": [
        {
            "name": "Simplify Redundant Conditionals",
            "code": """
def check(x, y):
    if x == True:
        return 1
    elif y == False:
        return 2
    return 3
""",
            "expected": """
def check(x, y):
    if x:
        return 1
    elif not y:
        return 2
    return 3
"""
        },
        {
            "name": "Combine Nested If Statements",
            "code": """
def check_bounds(x, y):
    if x > 0:
        if y < 10:
            return True
    return False
""",
            "expected": """
def check_bounds(x, y):
    if x > 0 and y < 10:
        return True
    return False
"""
        },
        {
            "name": "Replace Chained Comparisons",
            "code": """
def check_value(x):
    if x == 1 or x == 2 or x == 3:
        return "Small"
    return "Large"
""",
            "expected": """
def check_value(x):
    if x in {1, 2, 3}:
        return "Small"
    return "Large"
"""
        }
    ],
    
    "Dead Code Elimination": [
        {
            "name": "Remove Code After Return",
            "code": """
def get_value():
    return 42
    print("This won't execute")  # Dead code
""",
            "expected": """
def get_value():
    return 42
"""
        },
        {
            "name": "Delete Unused Imports",
            "code": """
import os  # Unused
import sys

def get_path():
    return sys.path
""",
            "expected": """
import sys

def get_path():
    return sys.path
"""
        },
        {
            "name": "Remove Redundant Pass",
            "code": """
def conditional_action(condition):
    if condition:
        pass
    else:
        return "Action"
    return None
""",
            "expected": """
def conditional_action(condition):
    if not condition:
        return "Action"
    return None
"""
        }
    ],
    
    "String Optimizations": [
        {
            "name": "Convert to F-Strings",
            "code": """
def format_message(name, age):
    return "Name: {}, Age: {}".format(name, age)
""",
            "expected": """
def format_message(name, age):
    return f"Name: {name}, Age: {age}"
"""
        },
        {
            "name": "Replace String Concatenation with Join",
            "code": """
def build_string(parts):
    result = ""
    for part in parts:
        result += part
    return result
""",
            "expected": """
def build_string(parts):
    return "".join(parts)
"""
        }
    ],
    
    "Function Optimizations": [
        {
            "name": "Remove Redundant Return None",
            "code": """
def process_data(data):
    for item in data:
        print(item)
    return None
""",
            "expected": """
def process_data(data):
    for item in data:
        print(item)
"""
        },
        {
            "name": "Simplify Boolean Returns",
            "code": """
def is_even(n):
    if n % 2 == 0:
        return True
    else:
        return False
""",
            "expected": """
def is_even(n):
    return n % 2 == 0
"""
        }
    ],
    
    "Structural Simplifications": [
        {
            "name": "Remove Redundant Parentheses",
            "code": """
def calculate():
    x = (5 + 3)
    y = (x * 2)
    return (y)
""",
            "expected": """
def calculate():
    x = 5 + 3
    y = x * 2
    return y
"""
        },
        {
            "name": "Simplify not not to bool()",
            "code": """
def check_value(value):
    return not not value
""",
            "expected": """
def check_value(value):
    return bool(value)
"""
        }
    ],
    
    "Loop Performance": [
        {
            "name": "Loop Invariant Code Motion",
            "code": """
def calculate_distances(points, origin):
    distances = []
    for i in range(len(points)):
        x_diff = points[i][0] - origin[0]
        y_diff = points[i][1] - origin[1]
        distance = (x_diff ** 2 + y_diff ** 2) ** 0.5
        distances.append(distance)
    return distances
""",
            "expected": """
def calculate_distances(points, origin):
    distances = []
    origin_x = origin[0]
    origin_y = origin[1]
    for i in range(len(points)):
        x_diff = points[i][0] - origin_x
        y_diff = points[i][1] - origin_y
        distance = (x_diff ** 2 + y_diff ** 2) ** 0.5
        distances.append(distance)
    return distances
"""
        }
    ],
    
    "Algorithm Optimizations": [
        {
            "name": "Optimize Bubble Sort",
            "code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
""",
            "expected": """
def bubble_sort(arr):
    arr.sort()
    return arr
"""
        },
        {
            "name": "Optimize Linear Search",
            "code": """
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
""",
            "expected": """
def linear_search(arr, target):
    try:
        return arr.index(target)
    except ValueError:
        return -1
"""
        }
    ],
    
    "Data Structure Optimizations": [
        {
            "name": "Replace List with Set for Membership Check",
            "code": """
def unique_values(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
""",
            "expected": """
def unique_values(items):
    return list(set(items))
"""
        }
    ]
}

class OptimizationTester:
    """Class to test code optimization capabilities"""
    
    def run_tests(self):
        """Run all test cases and report results"""
        logger.info(f"Starting optimization test suite with {sum(len(cases) for cases in TEST_CASES.values())} test cases")
        
        # Track results by category
        results_by_category = {}
        
        # Run tests for each category
        for category, test_cases in TEST_CASES.items():
            logger.info(f"\n==== Testing {category} ====")
            
            category_results = {
                "total": len(test_cases),
                "success": 0,
                "partial": 0,
                "failed": 0,
                "details": []
            }
            
            for test_case in test_cases:
                logger.info(f"Testing: {test_case['name']}")
                
                # Use temporary files to ensure proper indentation
                result = self.test_single_case(test_case["code"], test_case["expected"], test_case["name"], category)
                
                # Record result
                if result["result"] == "success":
                    category_results["success"] += 1
                    logger.info(f"✅ {test_case['name']} successfully optimized")
                elif result["result"] == "partial":
                    category_results["partial"] += 1
                    logger.info(f"⚠️ {test_case['name']} partially optimized")
                    # Show diff if partially optimized
                    self._show_diff(result["original"], result["optimized"])
                else:
                    category_results["failed"] += 1
                    logger.info(f"❌ {test_case['name']} not optimized")
                
                # Track details
                category_results["details"].append(result)
            
            # Store category results
            results_by_category[category] = category_results
        
        # Generate summary report
        self._generate_report(results_by_category)
        
        return results_by_category
    
    def test_single_case(self, code, expected, name, category):
        """
        Test a single code example using temporary files
        
        Args:
            code: Code string to optimize
            expected: Expected optimized code
            name: Name of the test case
            category: Category of the test case
            
        Returns:
            Dictionary with test results
        """
        # Use temporary files to ensure proper indentation
        orig_temp = None
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                orig_temp = f.name
            
            # Read back the code from the file (preserving indentation)
            with open(orig_temp, 'r') as f:
                original_code = f.read()
            
            # Run the optimizer
            logger.info("Initializing RuleBasedOptimizer")
            
            # Detect patterns
            patterns = detect_inefficient_patterns(original_code)
            logger.info(f"Detected {len(patterns)} inefficient patterns")
            
            # Run optimization
            optimized_code, detected_patterns, optimization_stats = optimize_code(original_code)
            
            # Calculate total optimizations (accounts for both old and new API)
            if isinstance(optimization_stats, dict):
                # New API returns a dictionary of optimization types -> counts
                optimization_count = sum(optimization_stats.values())
                optimization_details = optimization_stats
            else:
                # Old API returned a single number
                optimization_count = optimization_stats
                optimization_details = {"total": optimization_count}
                
            if optimization_count > 0:
                logger.info(f"Applied {optimization_count} optimizations")
                
                # Log optimization details if available
                if len(optimization_details) > 1:  # More than just "total"
                    for opt_type, count in optimization_details.items():
                        if count > 0:
                            logger.info(f"  - {opt_type.replace('_', ' ').title()}: {count}")
            
            # Compare with expected
            is_success = optimized_code.strip() == expected.strip()
            is_partial = optimized_code.strip() != original_code.strip()
            
            result = "success" if is_success else "partial" if is_partial else "failed"
            
            return {
                "name": name,
                "category": category,
                "result": result,
                "original": original_code,
                "optimized": optimized_code,
                "expected": expected,
                "patterns": len(patterns),
                "optimizations": optimization_count,
                "optimization_details": optimization_details
            }
                
        finally:
            # Clean up temporary file
            if orig_temp and os.path.exists(orig_temp):
                os.unlink(orig_temp)
    
    def _show_diff(self, original, optimized):
        """Show the difference between original and optimized code"""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            optimized.splitlines(keepends=True),
            fromfile="original",
            tofile="optimized",
            n=0
        )
        
        logger.info("Changes made:")
        for line in diff:
            logger.info(f"  {line.rstrip()}")
    
    def _generate_report(self, results_by_category):
        """Generate a summary report of the test results"""
        logger.info("\n==== Optimization Test Results ====\n")
        
        # Display results by category
        logger.info("Success Rate by Category:\n")
        
        total_tests = 0
        total_success = 0
        total_partial = 0
        
        for category, results in results_by_category.items():
            total = results["total"]
            success = results["success"]
            partial = results["partial"]
            success_rate = success / total * 100 if total > 0 else 0
            partial_rate = partial / total * 100 if total > 0 else 0
            
            logger.info(f"{category}:")
            logger.info(f"  Total tests: {total}")
            logger.info(f"  Successful: {success} ({success_rate:.1f}%)")
            logger.info(f"  Partial: {partial} ({partial_rate:.1f}%)")
            logger.info("")
            
            total_tests += total
            total_success += success
            total_partial += partial
        
        # Overall summary
        total_success_rate = total_success / total_tests * 100 if total_tests > 0 else 0
        total_partial_rate = total_partial / total_tests * 100 if total_tests > 0 else 0
        
        logger.info("Overall Summary:")
        logger.info(f"Total test cases: {total_tests}")
        logger.info(f"Successfully optimized: {total_success} ({total_success_rate:.1f}%)")
        logger.info(f"Partially optimized: {total_partial} ({total_partial_rate:.1f}%)")
        
        # Detailed results for tests
        logger.info("\nDetailed Test Results:\n")
        
        for category, results in results_by_category.items():
            for detail in results["details"]:
                status = "✅ SUCCESS" if detail["result"] == "success" else \
                        "⚠️ PARTIAL" if detail["result"] == "partial" else \
                        "❌ FAILED"
                
                logger.info(f"{detail['name']} - {status}")
                logger.info(f"Category: {category}")
                logger.info(f"Patterns detected: {detail['patterns']}")
                logger.info(f"Optimizations applied: {detail['optimizations']}")
                
                # Display detailed optimization breakdown if available
                if "optimization_details" in detail and isinstance(detail["optimization_details"], dict) and len(detail["optimization_details"]) > 1:
                    logger.info("Optimization breakdown:")
                    for opt_type, count in detail["optimization_details"].items():
                        if count > 0:
                            logger.info(f"  - {opt_type.replace('_', ' ').title()}: {count}")
                            
                logger.info("")
                
                logger.info("Original code:")
                logger.info(detail["original"])
                logger.info("")
                
                logger.info("Expected optimized code:")
                logger.info(detail["expected"])
                logger.info("")
                
                logger.info("Actual optimized code:")
                logger.info(detail["optimized"])
                logger.info("")

def main():
    """Main function to run the tests"""
    tester = OptimizationTester()
    tester.run_tests()

if __name__ == "__main__":
    main()