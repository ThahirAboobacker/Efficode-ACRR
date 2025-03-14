"""
Enhanced algorithm feature extraction for improved complexity prediction.
This module extracts specialized features that help distinguish between
different algorithm complexity classes.
"""

import re
import ast
from typing import Dict, List, Tuple, Any

class AlgorithmPatternDetector:
    """Detects common algorithm patterns in code"""
    
    def __init__(self, code: str):
        """Initialize with code to analyze"""
        self.code = code
        self.tree = None
        try:
            self.tree = ast.parse(code)
        except:
            pass
    
    def extract_advanced_features(self) -> Dict[str, Any]:
        """Extract advanced algorithm features from code"""
        features = {}
        
        # Basic pattern detection
        features['has_binary_search_pattern'] = self.detect_binary_search_pattern()
        features['has_divide_conquer_pattern'] = self.detect_divide_conquer_pattern()
        features['has_nested_loops'] = self.detect_nested_loops()
        features['list_comprehension_count'] = self.count_list_comprehensions()
        
        # Advanced operation detection
        features['halving_operations'] = self.count_halving_operations()
        features['slice_operations'] = self.count_slice_operations()
        features['array_indexing_in_loop'] = self.detect_array_indexing_in_loop()
        features['array_append_operations'] = self.count_append_operations()
        
        # Complexity indicators
        features['recursive_calls'] = self.count_recursive_calls()
        features['divide_by_constant'] = self.detect_divide_by_constant()
        features['multiple_recursive_branches'] = self.detect_multiple_recursive_branches()
        
        return features
    
    def detect_binary_search_pattern(self) -> int:
        """Detect binary search pattern (mid = (left + right) // 2)"""
        if not self.code:
            return 0
            
        # Look for midpoint calculation pattern
        mid_calc_pattern = r'mid\s*=\s*\(?(?:left|start|low|begin|l)\s*\+\s*(?:right|end|high|r)\)?(?:\s*\/\/\s*2|\s*>>>\s*1|\s*>\s*>\s*1)'
        has_mid_calc = 1 if re.search(mid_calc_pattern, self.code, re.IGNORECASE) else 0
        
        # Look for updated bounds pattern (left = mid + 1 or right = mid - 1)
        bounds_update_pattern = r'(?:left|start|low|begin|l)\s*=\s*mid\s*\+\s*1|(?:right|end|high|r)\s*=\s*mid\s*\-\s*1'
        has_bounds_update = 1 if re.search(bounds_update_pattern, self.code, re.IGNORECASE) else 0
        
        # Only count as binary search if both patterns exist
        return 1 if (has_mid_calc and has_bounds_update) else 0
    
    def detect_divide_conquer_pattern(self) -> int:
        """Detect divide and conquer pattern (splitting input and recursive calls)"""
        if not self.code:
            return 0
            
        # Look for midpoint division
        mid_division_pattern = r'(?:mid|middle)\s*=\s*(?:len\(.*?\)|.*?\.length|size|n)\s*//\s*2'
        has_mid_division = 1 if re.search(mid_division_pattern, self.code, re.IGNORECASE) else 0
        
        # Look for recursive calls on divided portions
        recursive_pattern = r'(?:return|=)\s*\w+\s*\(.*?(?:\[:|\.slice|\(|,).*?\)'
        has_recursive_call = 1 if re.search(recursive_pattern, self.code) else 0
        
        # Check for specific merge sort or quick sort patterns
        merge_pattern = r'merge\s*\(\s*\w+\s*\(.*?\)\s*,\s*\w+\s*\(.*?\)\s*\)'
        quick_pattern = r'(?:pivot|partition)'
        
        has_merge = 1 if re.search(merge_pattern, self.code) else 0
        has_quick = 1 if re.search(quick_pattern, self.code) else 0
        
        # Return 1 if we detect divide & conquer patterns
        return 1 if (has_mid_division and has_recursive_call) or has_merge or has_quick else 0
    
    def detect_nested_loops(self) -> int:
        """Detect nested loops in code"""
        if not self.code:
            return 0
            
        # Simple regex for nested loops
        nested_pattern = r'(?:for|while).*?[{:].*?(?:for|while).*?[{:]'
        
        # Remove string literals to avoid false positives
        code_no_strings = re.sub(r'".*?"|\'.*?\'', '""', self.code)
        
        # Look for nested loop pattern in single line or across lines
        single_line = re.search(nested_pattern, code_no_strings, re.DOTALL) is not None
        
        # Try to detect through indentation if we have AST
        indent_nested = False
        if self.tree:
            loop_depths = []
            for node in ast.walk(self.tree):
                if isinstance(node, (ast.For, ast.While)):
                    # Get approximate line indentation
                    lineno = node.lineno - 1
                    if lineno < len(self.code.splitlines()):
                        line = self.code.splitlines()[lineno]
                        indent = len(line) - len(line.lstrip())
                        loop_depths.append(indent)
            
            # Check if we have loops at different indentation levels
            indent_nested = len(set(loop_depths)) > 1 if loop_depths else False
        
        return 1 if single_line or indent_nested else 0
    
    def count_list_comprehensions(self) -> int:
        """Count list comprehensions which are often O(n) operations"""
        if not self.code:
            return 0
            
        # Look for list comprehension pattern
        list_comp_pattern = r'\[.*?\bfor\b.*?\]'
        matches = re.findall(list_comp_pattern, self.code)
        return len(matches)
    
    def count_halving_operations(self) -> int:
        """Count operations that halve values (indicators of logarithmic complexity)"""
        if not self.code:
            return 0
            
        # Look for division by 2, bit shifts, etc.
        halving_patterns = [
            r'\/\/\s*2',      # Integer division by 2
            r'>>\s*1',         # Right shift by 1 (equivalent to div by 2)
            r'\/\s*2\.0',      # Float division by 2
            r'\/\s*2(?!\d)',   # Division by 2 not followed by digit
            r'mid\s*=.*?(low|left|start|begin).*?(high|right|end)'  # Binary search midpoint
        ]
        
        count = 0
        for pattern in halving_patterns:
            matches = re.findall(pattern, self.code)
            count += len(matches)
            
        return count
    
    def count_slice_operations(self) -> int:
        """Count array slice operations (common in divide & conquer)"""
        if not self.code:
            return 0
            
        # Look for Python slicing or equivalent
        slice_pattern = r'\[.*?:.*?\]'
        matches = re.findall(slice_pattern, self.code)
        return len(matches)
    
    def detect_array_indexing_in_loop(self) -> int:
        """Detect array indexing inside loops"""
        if not self.code:
            return 0
            
        # Simple pattern: loop with array indexing inside
        loop_with_indexing = r'(?:for|while).*?{.*?\[.*?\]'
        if re.search(loop_with_indexing, self.code, re.DOTALL):
            return 1
            
        # Alternative approach using lines and indentation
        lines = self.code.splitlines()
        in_loop = False
        for line in lines:
            if re.search(r'^\s*(?:for|while)\b', line):
                in_loop = True
            elif in_loop and re.search(r'\[.*?\]', line) and not re.search(r'^\s*(?:def|class|if|elif|else|for|while)\b', line):
                return 1
            elif in_loop and not line.strip():
                continue
            elif in_loop and re.search(r'^\s*(?:def|class)\b', line):
                in_loop = False
                
        return 0
    
    def count_append_operations(self) -> int:
        """Count array append operations (common in building result arrays)"""
        if not self.code:
            return 0
            
        # Look for append method calls
        append_pattern = r'\.append\s*\('
        matches = re.findall(append_pattern, self.code)
        
        # Also look for array push equivalents
        push_pattern = r'\.push\s*\('
        matches.extend(re.findall(push_pattern, self.code))
        
        return len(matches)
    
    def count_recursive_calls(self) -> int:
        """Count recursive calls in the code"""
        if not self.tree:
            return 0
            
        # Extract function names
        function_names = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                function_names.add(node.name)
        
        # Count calls to these functions within function definitions
        recursive_calls = 0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and hasattr(node, 'func') and hasattr(node.func, 'id'):
                if node.func.id in function_names:
                    recursive_calls += 1
        
        # Fallback to regex if AST approach finds nothing
        if recursive_calls == 0:
            for name in function_names:
                # Look for the function name followed by opening parenthesis
                pattern = r'{}s*\('.format(re.escape(name))
                # Get all occurrences and subtract 1 for the definition
                matches = len(re.findall(pattern, self.code)) - 1
                recursive_calls += max(0, matches)
                
        return recursive_calls
    
    def detect_divide_by_constant(self) -> int:
        """Detect division by constant (often indicates logarithmic behavior)"""
        division_patterns = [
            r'\/\/\s*\d+',  # Integer division by any constant
            r'\/\s*\d+',    # Division by any constant
            r'>>\s*\d+'     # Right shift by constant
        ]
        
        for pattern in division_patterns:
            if re.search(pattern, self.code):
                return 1
                
        return 0
    
    def detect_multiple_recursive_branches(self) -> int:
        """Detect multiple recursive branches (e.g., in quick sort)"""
        if not self.tree:
            return 0
            
        # Extract function names
        function_names = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                function_names.add(node.name)
        
        # Look for functions with multiple recursive calls
        for name in function_names:
            if self.code.count(f"{name}(") > 2:  # More than one call (plus definition)
                return 1
                
        return 0

def extract_algorithm_features(code: str) -> Dict[str, Any]:
    """
    Extract comprehensive algorithm features for complexity prediction
    
    Args:
        code: Python code as string
        
    Returns:
        Dictionary of algorithm features
    """
    detector = AlgorithmPatternDetector(code)
    return detector.extract_advanced_features()