"""
Test Script for Rule-Based Optimizer in EFFICODE-ACRR

This script evaluates the performance of the rule-based optimizer
on a variety of complex test cases, including:
- Sorting algorithms
- Search algorithms 
- Data structures
- General Python code optimizations
"""

import os
import sys
import time
import ast
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import matplotlib.pyplot as plt
from tabulate import tabulate

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import rule-based optimizer
from src.rule_based import apply_optimization_rules as optimize_code
from src.utils import measure_execution_time, validate_code_equivalence, count_code_elements

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test case categories
TEST_CATEGORIES = [
    "Sorting Algorithms",
    "Search Algorithms",
    "Data Structures",
    "Loop Optimizations",
    "General Python Code"
]

class TestCase:
    """Test case for evaluating code optimization"""
    
    def __init__(self, name: str, code: str, category: str, description: str = ""):
        """
        Initialize test case
        
        Args:
            name: Test case name
            code: Original code to optimize
            category: Test case category
            description: Test case description
        """
        self.name = name
        self.code = code
        self.category = category
        self.description = description
        self.optimized_code = None
        self.patterns = None
        self.optimization_count = 0
        self.execution_time_before = 0.0
        self.execution_time_after = 0.0
        self.execution_time_std_before = 0.0
        self.execution_time_std_after = 0.0
        self.is_valid = False
        self.code_elements_before = None
        self.code_elements_after = None
        
    def run_optimization(self) -> bool:
        """
        Run optimization on the test case
        
        Returns:
            True if optimization was successful, False otherwise
        """
        try:
            # Optimize the code
            self.optimized_code, self.patterns, self.optimization_count = optimize_code(self.code)
            
            # Check if optimization made any changes
            if self.optimization_count == 0:
                logger.info(f"No optimizations applied to {self.name}")
                return False
            
            # Validate that the code is still valid Python
            try:
                ast.parse(self.optimized_code)
                logger.info(f"Optimization successful for {self.name} with {self.optimization_count} changes")
                return True
            except SyntaxError as e:
                logger.error(f"Optimized code has syntax errors: {e}")
                return False
        except Exception as e:
            logger.error(f"Error optimizing {self.name}: {e}")
            return False
    
    def evaluate_performance(self) -> bool:
        """
        Evaluate the performance of the optimized code
        
        Returns:
            True if evaluation was successful, False otherwise
        """
        try:
            # Measure execution time before optimization
            self.execution_time_before, self.execution_time_std_before, error = measure_execution_time(
                self.code, iterations=5)
            
            if error:
                logger.error(f"Error measuring original execution time: {error}")
                return False
            
            # Measure execution time after optimization
            self.execution_time_after, self.execution_time_std_after, error = measure_execution_time(
                self.optimized_code, iterations=5)
            
            if error:
                logger.error(f"Error measuring optimized execution time: {error}")
                return False
            
            # Validate functional equivalence
            self.is_valid, error_message = validate_code_equivalence(
                self.code, self.optimized_code)
            
            if not self.is_valid:
                logger.error(f"Optimized code is not functionally equivalent: {error_message}")
                return False
            
            # Count code elements before and after
            self.code_elements_before = count_code_elements(self.code)
            self.code_elements_after = count_code_elements(self.optimized_code)
            
            logger.info(f"Evaluation successful for {self.name}")
            logger.info(f"Execution time: {self.execution_time_before:.6f}s -> {self.execution_time_after:.6f}s")
            logger.info(f"Improvement: {(1 - self.execution_time_after / self.execution_time_before) * 100:.2f}%")
            
            return True
        except Exception as e:
            logger.error(f"Error evaluating {self.name}: {e}")
            return False
    
    def get_improvement_ratio(self) -> float:
        """
        Get the improvement ratio of the optimization
        
        Returns:
            Ratio of execution time improvement (1.0 means no change)
        """
        if self.execution_time_before == 0:
            return 1.0
        return self.execution_time_after / self.execution_time_before
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the performance evaluation
        
        Returns:
            Dictionary with performance metrics
        """
        improvement = (1 - self.get_improvement_ratio()) * 100
        
        return {
            "name": self.name,
            "category": self.category,
            "optimization_count": self.optimization_count,
            "execution_time_before": self.execution_time_before,
            "execution_time_after": self.execution_time_after,
            "improvement_percent": improvement,
            "is_valid": self.is_valid,
            "loops_before": self.code_elements_before.get("loops", 0) if self.code_elements_before else 0,
            "loops_after": self.code_elements_after.get("loops", 0) if self.code_elements_after else 0,
            "lines_before": self.code_elements_before.get("lines", 0) if self.code_elements_before else 0,
            "lines_after": self.code_elements_after.get("lines", 0) if self.code_elements_after else 0
        }


# Complex test cases for evaluation

# 1. Sorting Algorithms
bubble_sort_test = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""

insertion_sort_test = """
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
"""

selection_sort_test = """
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
"""

# 2. Search Algorithms
linear_search_test = """
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""

binary_search_test = """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""

string_search_test = """
def string_search(text, pattern):
    n, m = len(text), len(pattern)
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            return i
    return -1
"""

# 3. Data Structures
linked_list_test = """
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def find_middle(head):
    if head is None:
        return None
    
    slow = head
    fast = head
    
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    
    return slow.data
"""

stack_implementation_test = """
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
"""

binary_tree_traverse_test = """
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder_traversal(root):
    result = []
    
    def traverse(node):
        if node:
            traverse(node.left)
            result.append(node.val)
            traverse(node.right)
    
    traverse(root)
    return result
"""

# 4. Loop Optimizations
nested_loop_test = """
def find_pairs(arr1, arr2, target):
    pairs = []
    for i in range(len(arr1)):
        for j in range(len(arr2)):
            if arr1[i] + arr2[j] == target:
                pairs.append((arr1[i], arr2[j]))
    return pairs
"""

repeated_calculation_test = """
def calculate_distances(points, origin):
    distances = []
    for i in range(len(points)):
        x_diff = points[i][0] - origin[0]
        y_diff = points[i][1] - origin[1]
        distance = (x_diff ** 2 + y_diff ** 2) ** 0.5
        distances.append(distance)
    return distances
"""

string_concat_test = """
def build_report(data):
    report = ""
    for item in data:
        report += "Item: " + item["name"] + "\\n"
        report += "Price: $" + str(item["price"]) + "\\n"
        report += "Quantity: " + str(item["quantity"]) + "\\n"
        report += "----------\\n"
    return report
"""

multiple_traversals_test = """
def process_data(numbers):
    total_sum = 0
    for num in numbers:
        total_sum += num
    
    mean = total_sum / len(numbers)
    
    deviations = []
    for num in numbers:
        deviations.append(num - mean)
    
    squared_deviations = []
    for dev in deviations:
        squared_deviations.append(dev ** 2)
    
    variance = sum(squared_deviations) / len(numbers)
    return mean, variance
"""

# 5. General Python Code
list_comprehension_candidate_test = """
def get_even_squares(numbers):
    result = []
    for num in numbers:
        if num % 2 == 0:
            result.append(num ** 2)
    return result
"""

repeated_dict_lookup_test = """
def get_user_info(user_dict, user_id):
    name = user_dict[user_id]["name"]
    email = user_dict[user_id]["email"]
    address = user_dict[user_id]["address"]
    phone = user_dict[user_id]["phone"]
    return {
        "name": name,
        "email": email,
        "address": address,
        "phone": phone
    }
"""

unnecessary_temp_vars_test = """
def swap_and_sum(a, b):
    temp = a
    a = b
    b = temp
    
    sum_value = a + b
    return sum_value
"""

inefficient_conditionals_test = """
def check_status(value, threshold, is_active):
    if value == True:
        return "Value is true"
    
    if not (value < threshold):
        return "Value is >= threshold"
    
    if is_active == False:
        return "Not active"
    
    return "Default status"
"""

def main():
    """Main function to run the test suite"""
    
    # Create test cases
    test_cases = [
        # Sorting Algorithms
        TestCase("Bubble Sort", bubble_sort_test, "Sorting Algorithms", 
                "O(n²) comparison-based sorting algorithm"),
        TestCase("Insertion Sort", insertion_sort_test, "Sorting Algorithms",
                "O(n²) insertion-based sorting algorithm"),
        TestCase("Selection Sort", selection_sort_test, "Sorting Algorithms",
                "O(n²) selection-based sorting algorithm"),
        
        # Search Algorithms
        TestCase("Linear Search", linear_search_test, "Search Algorithms",
                "O(n) sequential search algorithm"),
        TestCase("Binary Search", binary_search_test, "Search Algorithms",
                "O(log n) divide-and-conquer search algorithm"),
        TestCase("String Search", string_search_test, "Search Algorithms",
                "O(n*m) naive string pattern matching"),
        
        # Data Structures
        TestCase("LinkedList Middle", linked_list_test, "Data Structures",
                "Finding middle element of a linked list using two pointers"),
        TestCase("Stack Implementation", stack_implementation_test, "Data Structures",
                "Basic stack implementation using a list"),
        TestCase("Binary Tree Traversal", binary_tree_traverse_test, "Data Structures",
                "In-order traversal of a binary tree using recursion"),
        
        # Loop Optimizations
        TestCase("Nested Loops", nested_loop_test, "Loop Optimizations",
                "Nested loops for finding pairs with a specific sum"),
        TestCase("Repeated Calculation", repeated_calculation_test, "Loop Optimizations",
                "Repeated calculation of distances in a loop"),
        TestCase("String Concatenation", string_concat_test, "Loop Optimizations",
                "Repeated string concatenation in a loop"),
        TestCase("Multiple Traversals", multiple_traversals_test, "Loop Optimizations",
                "Multiple traversals of the same data"),
        
        # General Python Code
        TestCase("List Comprehension Candidate", list_comprehension_candidate_test, "General Python Code",
                "Loop that could be replaced with a list comprehension"),
        TestCase("Repeated Dict Lookup", repeated_dict_lookup_test, "General Python Code",
                "Repeated dictionary lookups"),
        TestCase("Unnecessary Temp Variables", unnecessary_temp_vars_test, "General Python Code",
                "Unnecessary temporary variables"),
        TestCase("Inefficient Conditionals", inefficient_conditionals_test, "General Python Code",
                "Inefficient conditional expressions")
    ]
    
    # Run optimizations and evaluations
    results = []
    category_success = {category: {"total": 0, "success": 0} for category in TEST_CATEGORIES}
    
    logger.info("Starting test suite with %d test cases", len(test_cases))
    
    for test_case in test_cases:
        logger.info(f"Testing: {test_case.name} ({test_case.category})")
        
        # Update category counts
        category_success[test_case.category]["total"] += 1
        
        # Run optimization
        optimization_success = test_case.run_optimization()
        
        if optimization_success:
            # Only evaluate if optimization was applied
            evaluation_success = test_case.evaluate_performance()
            
            if evaluation_success and test_case.is_valid:
                category_success[test_case.category]["success"] += 1
                logger.info(f"✅ {test_case.name} successfully optimized and validated")
            else:
                logger.info(f"❌ {test_case.name} optimization invalid or not equivalent")
        else:
            logger.info(f"⚠️ No optimization applied to {test_case.name}")
        
        # Collect results for reporting
        results.append(test_case.get_performance_summary())
    
    # Generate report
    logger.info("\n==== Optimization Results ====")
    
    # Create DataFrame from results
    df = pd.DataFrame(results)
    
    # Calculate overall statistics
    total_tests = len(test_cases)
    successful_optimizations = sum(1 for r in results if r["optimization_count"] > 0)
    valid_optimizations = sum(1 for r in results if r["optimization_count"] > 0 and r["is_valid"])
    
    optimization_rate = successful_optimizations / total_tests * 100
    validation_rate = valid_optimizations / successful_optimizations * 100 if successful_optimizations > 0 else 0
    
    # Generate success rate by category
    print("\nSuccess Rate by Category:")
    category_data = []
    for category, counts in category_success.items():
        success_rate = counts["success"] / counts["total"] * 100 if counts["total"] > 0 else 0
        category_data.append({
            "Category": category,
            "Success": f"{counts['success']}/{counts['total']}",
            "Rate": f"{success_rate:.1f}%"
        })
    
    print(tabulate(category_data, headers="keys", tablefmt="grid"))
    
    # Print summary of improvements
    print("\nPerformance Improvements:")
    performance_data = []
    for r in results:
        if r["optimization_count"] > 0 and r["is_valid"]:
            performance_data.append({
                "Test Case": r["name"],
                "Time Before (s)": f"{r['execution_time_before']:.6f}",
                "Time After (s)": f"{r['execution_time_after']:.6f}",
                "Improvement": f"{r['improvement_percent']:.1f}%",
                "Optimizations": r["optimization_count"]
            })
    
    print(tabulate(performance_data, headers="keys", tablefmt="grid"))
    
    # Print overall summary
    print("\nOverall Summary:")
    print(f"Total test cases: {total_tests}")
    print(f"Successful optimizations: {successful_optimizations} ({optimization_rate:.1f}%)")
    print(f"Valid optimizations: {valid_optimizations} ({validation_rate:.1f}%)")
    
    avg_improvement = df[df["is_valid"]]["improvement_percent"].mean()
    print(f"Average performance improvement: {avg_improvement:.1f}%")
    
    # Generate detailed report for each test case
    print("\nDetailed Test Case Reports:")
    for test_case in test_cases:
        if test_case.optimization_count > 0:
            print(f"\n=== {test_case.name} ({test_case.category}) ===")
            print(f"Description: {test_case.description}")
            print(f"Optimizations applied: {test_case.optimization_count}")
            print(f"Functionally equivalent: {'Yes' if test_case.is_valid else 'No'}")
            
            if test_case.is_valid:
                improvement = (1 - test_case.get_improvement_ratio()) * 100
                print(f"Performance improvement: {improvement:.1f}%")
                print(f"Execution time: {test_case.execution_time_before:.6f}s -> {test_case.execution_time_after:.6f}s")
                print(f"Code size: {test_case.code_elements_before['lines']} -> {test_case.code_elements_after['lines']} lines")
                print(f"Loop count: {test_case.code_elements_before['loops']} -> {test_case.code_elements_after['loops']}")
            
            # Print detected patterns
            if test_case.patterns:
                print("\nDetected inefficient patterns:")
                for pattern in test_case.patterns:
                    print(f"- {pattern['name']} (severity: {pattern['severity']}, optimization: {pattern['optimization']})")
            
            # Print side-by-side code comparison for the first few lines
            if test_case.optimized_code:
                print("\nCode comparison (first 5 lines):")
                original_lines = test_case.code.strip().split('\n')[:5]
                optimized_lines = test_case.optimized_code.strip().split('\n')[:5]
                
                for i in range(max(len(original_lines), len(optimized_lines))):
                    orig = original_lines[i] if i < len(original_lines) else ""
                    optim = optimized_lines[i] if i < len(optimized_lines) else ""
                    print(f"Original: {orig}")
                    print(f"Optimized: {optim}")
                    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())