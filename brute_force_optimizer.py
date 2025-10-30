#!/usr/bin/env python3
"""
EFFICODE-ACRR: Brute Force to Optimized Code Converter
Input: Python brute force code
Output: Optimized code with complexity analysis
"""

import ast
import re
import time
from typing import Dict, List, Tuple, Optional

class BruteForceOptimizer:
    def __init__(self):
        self.optimization_patterns = {
            'two_sum': {
                'pattern': r'for.*in.*range.*for.*in.*range.*if.*\+.*==',
                'technique': 'Hash Map',
                'original_complexity': 'O(n²)',
                'optimized_complexity': 'O(n)',
                'data_structure': 'Dictionary/Hash Map'
            },
            'duplicate_detection': {
                'pattern': r'for.*in.*for.*in.*if.*==.*and.*!=',
                'technique': 'Hash Set',
                'original_complexity': 'O(n²)',
                'optimized_complexity': 'O(n)',
                'data_structure': 'Set'
            },
            'max_subarray': {
                'pattern': r'for.*in.*range.*for.*in.*range.*max.*sum',
                'technique': "Kadane's Algorithm",
                'original_complexity': 'O(n²)',
                'optimized_complexity': 'O(n)',
                'data_structure': 'Dynamic Programming'
            },
            'frequency_count': {
                'pattern': r'for.*in.*count.*==.*return',
                'technique': 'Frequency Counter',
                'original_complexity': 'O(n²)',
                'optimized_complexity': 'O(n)',
                'data_structure': 'Dictionary'
            }
        }
    
    def analyze_brute_force(self, code: str) -> Dict:
        """Analyze brute force code and identify optimization opportunities"""
        # Remove comments and normalize whitespace
        clean_code = re.sub(r'#.*', '', code)
        clean_code = ' '.join(clean_code.split())
        
        analysis = {
            'pattern_detected': None,
            'optimization_technique': None,
            'original_complexity': None,
            'optimized_complexity': None,
            'data_structure': None,
            'nested_loops': self._count_nested_loops(code)
        }
        
        # Pattern matching for optimization opportunities
        for pattern_name, pattern_info in self.optimization_patterns.items():
            if re.search(pattern_info['pattern'], clean_code, re.IGNORECASE):
                analysis.update({
                    'pattern_detected': pattern_name,
                    'optimization_technique': pattern_info['technique'],
                    'original_complexity': pattern_info['original_complexity'],
                    'optimized_complexity': pattern_info['optimized_complexity'],
                    'data_structure': pattern_info['data_structure']
                })
                break
        
        return analysis
    
    def _count_nested_loops(self, code: str) -> int:
        """Count nested loop levels"""
        try:
            tree = ast.parse(code)
            max_depth = 0
            
            def visit_node(node, depth=0):
                nonlocal max_depth
                if isinstance(node, (ast.For, ast.While)):
                    depth += 1
                    max_depth = max(max_depth, depth)
                
                for child in ast.iter_child_nodes(node):
                    visit_node(child, depth)
            
            visit_node(tree)
            return max_depth
        except:
            return 0
    
    def optimize_two_sum(self, code: str) -> str:
        """Convert brute force two sum to hash map approach"""
        return '''def two_sum_optimized(nums, target):
    """
    Optimized Two Sum using Hash Map
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(n) - Hash map storage
    Data Structure: Dictionary for O(1) lookups
    """
    num_map = {}  # Hash map: value -> index
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []  # No solution found'''
    
    def optimize_duplicate_detection(self, code: str) -> str:
        """Convert brute force duplicate detection to hash set"""
        return '''def contains_duplicate_optimized(nums):
    """
    Optimized Duplicate Detection using Hash Set
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(n) - Set storage
    Data Structure: Set for O(1) membership testing
    """
    seen = set()  # Hash set for fast lookups
    
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    
    return False'''
    
    def optimize_max_subarray(self, code: str) -> str:
        """Convert brute force max subarray to Kadane's algorithm"""
        return '''def max_subarray_optimized(nums):
    """
    Optimized Maximum Subarray using Kadane's Algorithm
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(1) - Constant space
    Data Structure: Dynamic Programming approach
    """
    if not nums:
        return 0
    
    max_sum = current_sum = nums[0]
    
    for num in nums[1:]:
        # Either extend existing subarray or start new one
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum'''
    
    def optimize_frequency_count(self, code: str) -> str:
        """Convert brute force frequency counting to hash map"""
        return '''def find_duplicates_optimized(nums):
    """
    Optimized Duplicate Finding using Frequency Counter
    Time Complexity: O(n) - Single pass through array
    Space Complexity: O(n) - Dictionary storage
    Data Structure: Dictionary for frequency counting
    """
    frequency = {}  # Hash map: number -> count
    duplicates = []
    
    # Count frequencies
    for num in nums:
        frequency[num] = frequency.get(num, 0) + 1
    
    # Find duplicates
    for num, count in frequency.items():
        if count > 1:
            duplicates.append(num)
    
    return duplicates'''
    
    def optimize_code(self, brute_force_code: str) -> Dict:
        """Main optimization function"""
        start_time = time.time()
        
        # Analyze the brute force code
        analysis = self.analyze_brute_force(brute_force_code)
        
        # Generate optimized version based on detected pattern
        optimized_code = "# No optimization pattern detected"
        explanation = "Could not identify a known optimization pattern."
        
        if analysis['pattern_detected']:
            pattern = analysis['pattern_detected']
            
            if pattern == 'two_sum':
                optimized_code = self.optimize_two_sum(brute_force_code)
                explanation = "Converted nested loops to hash map lookup for O(1) complement search."
            
            elif pattern == 'duplicate_detection':
                optimized_code = self.optimize_duplicate_detection(brute_force_code)
                explanation = "Replaced nested comparison with hash set for O(1) membership testing."
            
            elif pattern == 'max_subarray':
                optimized_code = self.optimize_max_subarray(brute_force_code)
                explanation = "Applied Kadane's algorithm for single-pass maximum subarray calculation."
            
            elif pattern == 'frequency_count':
                optimized_code = self.optimize_frequency_count(brute_force_code)
                explanation = "Used frequency counter to eliminate nested scanning."
        
        processing_time = time.time() - start_time
        
        return {
            'original_code': brute_force_code,
            'optimized_code': optimized_code,
            'analysis': analysis,
            'explanation': explanation,
            'processing_time': processing_time,
            'performance_improvement': self._calculate_improvement(analysis)
        }
    
    def _calculate_improvement(self, analysis: Dict) -> Dict:
        """Calculate theoretical performance improvement"""
        if not analysis['pattern_detected']:
            return {'speedup': '1x', 'description': 'No optimization applied'}
        
        # Theoretical speedup calculations for different input sizes
        improvements = {
            'small_input_100': '100x faster',
            'medium_input_1000': '1,000x faster', 
            'large_input_10000': '10,000x faster',
            'description': f"Reduced from {analysis['original_complexity']} to {analysis['optimized_complexity']}"
        }
        
        return improvements

def main():
    """Interactive demo of the brute force optimizer"""
    optimizer = BruteForceOptimizer()
    
    print("🚀 EFFICODE-ACRR: Brute Force Code Optimizer")
    print("=" * 50)
    print("Input your brute force Python code and get optimized version!")
    print()
    
    # Example brute force codes for testing
    examples = {
        '1': '''def two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []''',
        
        '2': '''def contains_duplicate_brute(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j] and i != j:
                return True
    return False''',
        
        '3': '''def max_subarray_brute(nums):
    max_sum = float('-inf')
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            current_sum = sum(nums[i:j+1])
            max_sum = max(max_sum, current_sum)
    return max_sum'''
    }
    
    while True:
        print("\nChoose an option:")
        print("1. Two Sum (Brute Force)")
        print("2. Contains Duplicate (Brute Force)")
        print("3. Maximum Subarray (Brute Force)")
        print("4. Enter custom code")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '5':
            break
        
        if choice in examples:
            code = examples[choice]
            print(f"\n📝 Input Code:\n{code}")
        elif choice == '4':
            print("\n📝 Enter your brute force code (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            code = '\n'.join(lines[:-1])  # Remove last empty line
        else:
            print("Invalid choice!")
            continue
        
        # Optimize the code
        result = optimizer.optimize_code(code)
        
        # Display results
        print("\n" + "="*60)
        print("🔍 ANALYSIS RESULTS")
        print("="*60)
        
        analysis = result['analysis']
        print(f"Pattern Detected: {analysis['pattern_detected'] or 'None'}")
        print(f"Optimization Technique: {analysis['optimization_technique'] or 'None'}")
        print(f"Data Structure Used: {analysis['data_structure'] or 'None'}")
        print(f"Original Complexity: {analysis['original_complexity'] or 'Unknown'}")
        print(f"Optimized Complexity: {analysis['optimized_complexity'] or 'Unknown'}")
        print(f"Nested Loop Levels: {analysis['nested_loops']}")
        
        print(f"\n⚡ PERFORMANCE IMPROVEMENT")
        print("-" * 30)
        perf = result['performance_improvement']
        print(f"Description: {perf['description']}")
        if 'small_input_100' in perf:
            print(f"For 100 elements: {perf['small_input_100']}")
            print(f"For 1,000 elements: {perf['medium_input_1000']}")
            print(f"For 10,000 elements: {perf['large_input_10000']}")
        
        print(f"\n🚀 OPTIMIZED CODE")
        print("-" * 30)
        print(result['optimized_code'])
        
        print(f"\n💡 EXPLANATION")
        print("-" * 30)
        print(result['explanation'])
        
        print(f"\n⏱️  Processing Time: {result['processing_time']:.4f} seconds")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    main()