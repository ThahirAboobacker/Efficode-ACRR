#!/usr/bin/env python3
"""
AST-Based Code Transformer for Automatic Optimization
Converts brute force code to optimized versions using AST manipulation
"""

import ast
from typing import Dict, List, Optional, Any

class ASTCodeTransformer:
    def __init__(self):
        self.transformation_rules = {
            'two_sum_pattern': self.transform_two_sum,
            'contains_duplicate_pattern': self.transform_contains_duplicate,
            'max_subarray_pattern': self.transform_max_subarray,
            'nested_loop_sum': self.transform_nested_sum,
            'frequency_counting': self.transform_frequency_count
        }
    
    def detect_optimization_pattern(self, code: str) -> Optional[str]:
        """Detect which optimization pattern applies to the code"""
        try:
            tree = ast.parse(code)
            
            # Analyze AST structure
            analysis = self.analyze_ast_structure(tree)
            
            # Pattern matching logic
            if self.is_two_sum_pattern(analysis, code):
                return 'two_sum_pattern'
            elif self.is_contains_duplicate_pattern(analysis, code):
                return 'contains_duplicate_pattern'
            elif self.is_max_subarray_pattern(analysis, code):
                return 'max_subarray_pattern'
            elif self.is_nested_sum_pattern(analysis, code):
                return 'nested_loop_sum'
            elif self.is_frequency_pattern(analysis, code):
                return 'frequency_counting'
            
            return None
            
        except Exception as e:
            print(f"Error in pattern detection: {e}")
            return None
    
    def analyze_ast_structure(self, tree: ast.AST) -> Dict:
        """Analyze AST structure for pattern detection"""
        analysis = {
            'nested_loops': 0,
            'max_nested_depth': 0,
            'has_return_in_loop': False,
            'has_sum_operation': False,
            'has_equality_check': False,
            'has_append_operation': False,
            'variables_used': set(),
            'function_calls': [],
            'loop_variables': [],
            'comparison_operations': []
        }
        
        class AnalysisVisitor(ast.NodeVisitor):
            def __init__(self, analysis_dict):
                self.analysis = analysis_dict
                self.loop_depth = 0
                self.max_depth = 0
            
            def visit_For(self, node):
                self.loop_depth += 1
                self.max_depth = max(self.max_depth, self.loop_depth)
                
                # Extract loop variable
                if isinstance(node.target, ast.Name):
                    self.analysis['loop_variables'].append(node.target.id)
                
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_While(self, node):
                self.loop_depth += 1
                self.max_depth = max(self.max_depth, self.loop_depth)
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_Return(self, node):
                if self.loop_depth > 0:
                    self.analysis['has_return_in_loop'] = True
                self.generic_visit(node)
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.analysis['function_calls'].append(node.func.id)
                    if node.func.id == 'sum':
                        self.analysis['has_sum_operation'] = True
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'append':
                        self.analysis['has_append_operation'] = True
                self.generic_visit(node)
            
            def visit_Compare(self, node):
                self.analysis['comparison_operations'].append(node)
                for op in node.ops:
                    if isinstance(op, ast.Eq):
                        self.analysis['has_equality_check'] = True
                self.generic_visit(node)
            
            def visit_Name(self, node):
                self.analysis['variables_used'].add(node.id)
                self.generic_visit(node)
        
        visitor = AnalysisVisitor(analysis)
        visitor.visit(tree)
        
        analysis['nested_loops'] = visitor.max_depth
        analysis['max_nested_depth'] = visitor.max_depth
        
        return analysis
    
    def is_two_sum_pattern(self, analysis: Dict, code: str) -> bool:
        """Detect Two Sum pattern"""
        return (analysis['nested_loops'] >= 2 and 
                analysis['has_equality_check'] and
                analysis['has_return_in_loop'] and
                '+' in code and
                'target' in analysis['variables_used'])
    
    def is_contains_duplicate_pattern(self, analysis: Dict, code: str) -> bool:
        """Detect Contains Duplicate pattern"""
        return (analysis['nested_loops'] >= 2 and
                analysis['has_equality_check'] and
                analysis['has_return_in_loop'] and
                'True' in code and
                'False' in code)
    
    def is_max_subarray_pattern(self, analysis: Dict, code: str) -> bool:
        """Detect Maximum Subarray pattern"""
        return (analysis['nested_loops'] >= 2 and
                analysis['has_sum_operation'] and
                'max' in analysis['function_calls'])
    
    def is_nested_sum_pattern(self, analysis: Dict, code: str) -> bool:
        """Detect nested sum pattern"""
        return (analysis['nested_loops'] >= 2 and
                (analysis['has_sum_operation'] or '+' in code))
    
    def is_frequency_pattern(self, analysis: Dict, code: str) -> bool:
        """Detect frequency counting pattern"""
        return (analysis['nested_loops'] >= 2 and
                ('count' in code.lower() or 'freq' in code.lower()))
    
    def transform_code(self, code: str, technique: str) -> str:
        """Transform code using detected pattern"""
        pattern = self.detect_optimization_pattern(code)
        
        if pattern and pattern in self.transformation_rules:
            return self.transformation_rules[pattern](code)
        else:
            # Fallback to technique-based transformation
            return self.transform_by_technique(code, technique)
    
    def transform_two_sum(self, code: str) -> str:
        """Transform Two Sum brute force to hash map"""
        try:
            tree = ast.parse(code)
            
            # Extract function info
            func_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_def = node
                    break
            
            if not func_def:
                return code
            
            # Generate optimized AST
            optimized_code = f'''def {func_def.name}_optimized({', '.join([arg.arg for arg in func_def.args.args])}):
    """
    Optimized Two Sum using Hash Map
    Time Complexity: O(n) - Single pass
    Space Complexity: O(n) - Hash map storage
    """
    num_map = {{}}
    
    for i, num in enumerate({func_def.args.args[0].arg}):
        complement = {func_def.args.args[1].arg} - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []'''
            
            return optimized_code
            
        except Exception as e:
            print(f"Error in Two Sum transformation: {e}")
            return code
    
    def transform_contains_duplicate(self, code: str) -> str:
        """Transform Contains Duplicate to hash set"""
        try:
            tree = ast.parse(code)
            
            func_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_def = node
                    break
            
            if not func_def:
                return code
            
            optimized_code = f'''def {func_def.name}_optimized({', '.join([arg.arg for arg in func_def.args.args])}):
    """
    Optimized Contains Duplicate using Hash Set
    Time Complexity: O(n) - Single pass
    Space Complexity: O(n) - Set storage
    """
    seen = set()
    
    for item in {func_def.args.args[0].arg}:
        if item in seen:
            return True
        seen.add(item)
    
    return False'''
            
            return optimized_code
            
        except Exception as e:
            print(f"Error in Contains Duplicate transformation: {e}")
            return code
    
    def transform_max_subarray(self, code: str) -> str:
        """Transform Maximum Subarray to Kadane's algorithm"""
        try:
            tree = ast.parse(code)
            
            func_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_def = node
                    break
            
            if not func_def:
                return code
            
            optimized_code = f'''def {func_def.name}_optimized({', '.join([arg.arg for arg in func_def.args.args])}):
    """
    Optimized Maximum Subarray using Kadane's Algorithm
    Time Complexity: O(n) - Single pass
    Space Complexity: O(1) - Constant space
    """
    if not {func_def.args.args[0].arg}:
        return 0
    
    max_sum = current_sum = {func_def.args.args[0].arg}[0]
    
    for num in {func_def.args.args[0].arg}[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum'''
            
            return optimized_code
            
        except Exception as e:
            print(f"Error in Max Subarray transformation: {e}")
            return code
    
    def transform_nested_sum(self, code: str) -> str:
        """Transform nested sum operations"""
        return self.transform_by_technique(code, 'hash_map')
    
    def transform_frequency_count(self, code: str) -> str:
        """Transform frequency counting operations"""
        return self.transform_by_technique(code, 'frequency_map')
    
    def transform_by_technique(self, code: str, technique: str) -> str:
        """Fallback transformation based on technique"""
        try:
            tree = ast.parse(code)
            
            func_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_def = node
                    break
            
            if not func_def:
                return f"# Could not parse function definition\n{code}"
            
            func_name = func_def.name
            args = [arg.arg for arg in func_def.args.args]
            
            if technique == 'hash_map':
                return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized using Hash Map
    Time Complexity: O(n) - Hash map lookups
    Space Complexity: O(n) - Hash map storage
    """
    lookup_map = {{}}
    
    for i, item in enumerate({args[0] if args else 'data'}):
        # TODO: Implement hash map logic based on your specific problem
        # This is a template - customize for your use case
        pass
    
    return []'''
            
            elif technique == 'hash_set':
                return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized using Hash Set
    Time Complexity: O(n) - Set operations
    Space Complexity: O(n) - Set storage
    """
    seen = set()
    
    for item in {args[0] if args else 'data'}:
        if item in seen:
            return True  # Or appropriate logic
        seen.add(item)
    
    return False'''
            
            elif technique == 'dynamic_programming':
                return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized using Dynamic Programming
    Time Complexity: O(n) - Single pass
    Space Complexity: O(1) - Constant space
    """
    if not {args[0] if args else 'data'}:
        return 0
    
    current_optimal = global_optimal = {args[0] if args else 'data'}[0]
    
    for item in {args[0] if args else 'data'}[1:]:
        current_optimal = max(item, current_optimal + item)
        global_optimal = max(global_optimal, current_optimal)
    
    return global_optimal'''
            
            else:
                return f'''def {func_name}_optimized({', '.join(args)}):
    """
    Optimized using {technique.replace('_', ' ').title()}
    TODO: Implement specific optimization logic
    """
    # Original code with optimization suggestions
{code}
    
    # TODO: Apply {technique} optimization'''
            
        except Exception as e:
            print(f"Error in technique-based transformation: {e}")
            return code

def test_ast_transformer():
    """Test the AST code transformer"""
    transformer = ASTCodeTransformer()
    
    print("🧪 TESTING AST CODE TRANSFORMER")
    print("=" * 50)
    
    # Test Two Sum
    two_sum_code = '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []'''
    
    print("Original Two Sum:")
    print(two_sum_code)
    
    pattern = transformer.detect_optimization_pattern(two_sum_code)
    print(f"\nDetected Pattern: {pattern}")
    
    optimized = transformer.transform_code(two_sum_code, 'hash_map')
    print(f"\nTransformed Code:")
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
    
    pattern = transformer.detect_optimization_pattern(contains_dup_code)
    print(f"\nDetected Pattern: {pattern}")
    
    optimized = transformer.transform_code(contains_dup_code, 'hash_set')
    print(f"\nTransformed Code:")
    print(optimized)

if __name__ == "__main__":
    test_ast_transformer()