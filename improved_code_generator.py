#!/usr/bin/env python3
"""
Improved Code Generator with Better Template Accuracy
"""

import ast
import re
from typing import Dict, List, Optional

class ImprovedCodeGenerator:
    def __init__(self):
        self.setup_accurate_templates()
    
    def setup_accurate_templates(self):
        """Setup more accurate code generation templates"""
        self.templates = {
            'two_sum_pattern': {
                'detection': r'for.*range.*for.*range.*\+.*==.*target',
                'template': self.generate_two_sum_optimized
            },
            'contains_duplicate_pattern': {
                'detection': r'for.*range.*for.*range.*==.*and.*!=',
                'template': self.generate_contains_duplicate_optimized
            },
            'max_subarray_pattern': {
                'detection': r'for.*range.*for.*range.*sum.*max',
                'template': self.generate_max_subarray_optimized
            },
            'count_pairs_pattern': {
                'detection': r'for.*range.*for.*range.*\+.*==.*count',
                'template': self.generate_count_pairs_optimized
            }
        }
    
    def analyze_code_pattern(self, code: str) -> Optional[str]:
        """Analyze code to detect specific optimization patterns"""
        clean_code = ' '.join(code.split())
        
        for pattern_name, pattern_info in self.templates.items():
            if re.search(pattern_info['detection'], clean_code, re.IGNORECASE):
                return pattern_name
        
        return None
    
    def extract_function_info(self, code: str) -> Dict:
        """Extract function name and parameters accurately"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    return {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'body': ast.unparse(node) if hasattr(ast, 'unparse') else code
                    }
        except:
            pass
        
        # Fallback regex extraction
        func_match = re.search(r'def (\w+)\((.*?)\):', code)
        if func_match:
            return {
                'name': func_match.group(1),
                'args': [arg.strip() for arg in func_match.group(2).split(',') if arg.strip()],
                'body': code
            }
        
        return {'name': 'optimized_function', 'args': ['arr'], 'body': code}
    
    def generate_optimized_code(self, original_code: str, technique: str) -> str:
        """Generate accurate optimized code"""
        # First try pattern-specific optimization
        pattern = self.analyze_code_pattern(original_code)
        if pattern and pattern in self.templates:
            func_info = self.extract_function_info(original_code)
            return self.templates[pattern]['template'](func_info, original_code)
        
        # Fallback to technique-based optimization
        func_info = self.extract_function_info(original_code)
        
        if technique == 'hash_map':
            return self.generate_hash_map_generic(func_info, original_code)
        elif technique == 'hash_set':
            return self.generate_hash_set_generic(func_info, original_code)
        elif technique == 'dynamic_programming':
            return self.generate_dp_generic(func_info, original_code)
        else:
            return self.generate_generic_optimization(func_info, original_code)
    
    def generate_two_sum_optimized(self, func_info: Dict, original: str) -> str:
        """Generate accurate Two Sum optimization"""
        func_name = func_info['name']
        args = func_info['args']
        
        # Detect parameter names
        nums_param = args[0] if len(args) > 0 else 'nums'
        target_param = args[1] if len(args) > 1 else 'target'
        
        return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized Two Sum using Hash Map
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(n) - Hash map storage
    Data Structure: Dictionary for O(1) complement lookups
    
    Algorithm:
    1. Create hash map to store number -> index mapping
    2. For each number, calculate complement (target - number)
    3. If complement exists in map, return indices
    4. Otherwise, store current number and index in map
    """
    num_map = {{}}  # Hash map: number -> index
    
    for i, num in enumerate({nums_param}):
        complement = {target_param} - num
        
        # Check if complement exists in hash map
        if complement in num_map:
            return [num_map[complement], i]
        
        # Store current number with its index
        num_map[num] = i
    
    return []  # No solution found'''
    
    def generate_contains_duplicate_optimized(self, func_info: Dict, original: str) -> str:
        """Generate accurate Contains Duplicate optimization"""
        func_name = func_info['name']
        args = func_info['args']
        nums_param = args[0] if len(args) > 0 else 'nums'
        
        return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized Contains Duplicate using Hash Set
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(n) - Set storage
    Data Structure: Set for O(1) membership testing
    
    Algorithm:
    1. Create empty set to track seen numbers
    2. For each number in array:
       - If number already in set, return True (duplicate found)
       - Otherwise, add number to set
    3. If loop completes, return False (no duplicates)
    """
    seen = set()  # Hash set for fast membership testing
    
    for num in {nums_param}:
        if num in seen:
            return True  # Duplicate found
        seen.add(num)
    
    return False  # No duplicates found'''
    
    def generate_max_subarray_optimized(self, func_info: Dict, original: str) -> str:
        """Generate accurate Maximum Subarray optimization (Kadane's Algorithm)"""
        func_name = func_info['name']
        args = func_info['args']
        nums_param = args[0] if len(args) > 0 else 'nums'
        
        return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized Maximum Subarray using Kadane's Algorithm
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(1) - Constant space
    Data Structure: Dynamic Programming with optimal substructure
    
    Algorithm (Kadane's Algorithm):
    1. Initialize max_sum and current_sum with first element
    2. For each subsequent element:
       - Decide whether to extend current subarray or start new one
       - current_sum = max(element, current_sum + element)
       - Update global maximum if current_sum is larger
    3. Return global maximum
    """
    if not {nums_param}:
        return 0
    
    # Initialize with first element
    max_sum = current_sum = {nums_param}[0]
    
    # Apply Kadane's algorithm
    for num in {nums_param}[1:]:
        # Either extend current subarray or start new one
        current_sum = max(num, current_sum + num)
        # Update global maximum
        max_sum = max(max_sum, current_sum)
    
    return max_sum'''
    
    def generate_count_pairs_optimized(self, func_info: Dict, original: str) -> str:
        """Generate accurate Count Pairs optimization"""
        func_name = func_info['name']
        args = func_info['args']
        
        return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized Count Pairs using Hash Map
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(n) - Hash map storage
    Data Structure: Dictionary for frequency counting
    
    Algorithm:
    1. Create frequency map to count occurrences
    2. For each number, calculate complement
    3. If complement exists, add its frequency to count
    4. Update frequency of current number
    """
    frequency = {{}}  # Hash map: number -> count
    count = 0
    
    for num in {args[0] if args else 'arr'}:
        complement = {args[1] if len(args) > 1 else 'target'} - num
        
        # Add frequency of complement to count
        if complement in frequency:
            count += frequency[complement]
        
        # Update frequency of current number
        frequency[num] = frequency.get(num, 0) + 1
    
    return count'''
    
    def generate_hash_map_generic(self, func_info: Dict, original: str) -> str:
        """Generate generic hash map optimization"""
        func_name = func_info['name']
        args = func_info['args']
        
        return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized using Hash Map
    Time Complexity: O(n) - Single pass with O(1) lookups
    Space Complexity: O(n) - Hash map storage
    """
    lookup_map = {{}}
    
    for i, item in enumerate({args[0] if args else 'arr'}):
        # Implement hash map logic based on your specific problem
        # This is a generic template - customize for your use case
        pass
    
    return []'''
    
    def generate_hash_set_generic(self, func_info: Dict, original: str) -> str:
        """Generate generic hash set optimization"""
        func_name = func_info['name']
        args = func_info['args']
        
        return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized using Hash Set
    Time Complexity: O(n) - Single pass with O(1) membership testing
    Space Complexity: O(n) - Set storage
    """
    seen = set()
    
    for item in {args[0] if args else 'arr'}:
        if item in seen:
            return True  # Or appropriate logic for your problem
        seen.add(item)
    
    return False'''
    
    def generate_dp_generic(self, func_info: Dict, original: str) -> str:
        """Generate generic dynamic programming optimization"""
        func_name = func_info['name']
        args = func_info['args']
        
        return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized using Dynamic Programming
    Time Complexity: O(n) - Single pass with optimal substructure
    Space Complexity: O(1) - Constant space
    """
    if not {args[0] if args else 'arr'}:
        return 0
    
    # Apply dynamic programming principle
    current_optimal = global_optimal = {args[0] if args else 'arr'}[0]
    
    for item in {args[0] if args else 'arr'}[1:]:
        current_optimal = max(item, current_optimal + item)
        global_optimal = max(global_optimal, current_optimal)
    
    return global_optimal'''
    
    def generate_generic_optimization(self, func_info: Dict, original: str) -> str:
        """Generate generic optimization with suggestions"""
        return f'''# OPTIMIZATION ANALYSIS FOR: {func_info['name']}
# 
# ORIGINAL CODE:
{original}

# OPTIMIZATION SUGGESTIONS:
# 1. HASH MAP: Use dict() for O(1) key-value lookups
# 2. HASH SET: Use set() for O(1) membership testing  
# 3. DYNAMIC PROGRAMMING: Look for optimal substructure
# 4. TWO POINTERS: Consider sorting for pointer-based approach
# 5. SLIDING WINDOW: For subarray/substring problems
#
# RECOMMENDED APPROACH:
# Based on the pattern analysis, consider implementing the
# optimization technique suggested by the ML model.

def {func_info['name']}_optimized({', '.join(func_info['args'])}):
    """
    TODO: Implement optimization based on ML suggestion
    Refer to the specific technique recommended above
    """
    # Implement your optimization here
    pass'''

def test_improved_generator():
    """Test the improved code generator"""
    generator = ImprovedCodeGenerator()
    
    # Test Two Sum
    two_sum_code = '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []'''
    
    print("🧪 Testing Improved Code Generator")
    print("=" * 50)
    
    print("Original Two Sum:")
    print(two_sum_code)
    
    optimized = generator.generate_optimized_code(two_sum_code, 'hash_map')
    print("\nImproved Optimized Version:")
    print(optimized)
    
    # Test Contains Duplicate
    contains_dup_code = '''def containsDuplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False'''
    
    print("\n" + "="*50)
    print("Original Contains Duplicate:")
    print(contains_dup_code)
    
    optimized = generator.generate_optimized_code(contains_dup_code, 'hash_set')
    print("\nImproved Optimized Version:")
    print(optimized)

if __name__ == "__main__":
    test_improved_generator()