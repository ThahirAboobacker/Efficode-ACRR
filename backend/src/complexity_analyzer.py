"""
EFFICODE-ACRR Code Complexity Analyzer - Simplified Version

This module analyzes the time complexity of Python code.
"""

import re
import ast
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_complexity(code: str) -> str:
    """
    Analyze the complexity of code
        
        Args:
            code: Python code as string
            
        Returns:
        Complexity as a string (e.g., "O(n)")
    """
    try:
        # Try parsing the code
        tree = ast.parse(code)
        
        # Use the visitor pattern to analyze the AST
        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)
        
        # Get the complexity
        complexity = analyzer.get_complexity()
        
        return complexity
        except Exception as e:
        logger.error(f"Error analyzing complexity: {e}")
        return "O(n)"  # Default fallback

class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor that analyzes code complexity"""
    
    def __init__(self):
        super().__init__()
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.has_recursive_call = False
        self.function_calls = set()
        self.function_definitions = {}
        self.current_function = None
        self.binary_search_pattern = False
        self.divide_and_conquer_pattern = False
        self.simple_operations = 0
    
    def visit_FunctionDef(self, node):
        """Visit a function definition node."""
        prev_function = self.current_function
        self.current_function = node.name
        self.function_definitions[node.name] = node
        
        # Visit child nodes
        self.generic_visit(node)
        
        self.current_function = prev_function
    
    def visit_For(self, node):
        """Visit a for loop node."""
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        
        # Check for range(n) iterating over input size
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == 'range' and len(node.iter.args) > 0:
                # This is a loop that iterates from 0 to some value
                pass
        
        # Check for divide and conquer pattern (recursive calls with sliced input)
        body_contains_call = any(isinstance(n, ast.Call) for n in ast.walk(node))
        if body_contains_call and ":" in ast.unparse(node.iter):
            self.divide_and_conquer_pattern = True
        
        # Visit child nodes
        self.generic_visit(node)
        
        self.loop_depth -= 1
    
    def visit_While(self, node):
        """Visit a while loop node."""
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        
        # Check for binary search pattern - decreasing interval in each iteration
        # while left <= right: ... mid = (left + right) // 2
        contains_mid_calc = False
        for n in ast.walk(node):
            if isinstance(n, ast.Assign):
                try:
                    target_name = n.targets[0].id if isinstance(n.targets[0], ast.Name) else ""
                    if target_name == "mid" and "//" in ast.unparse(n.value):
                        contains_mid_calc = True
                except (AttributeError, IndexError):
                    pass
        
        if contains_mid_calc and any(op_node.op.__class__.__name__ == "LtE" for op_node in ast.walk(node) if isinstance(op_node, ast.Compare)):
            self.binary_search_pattern = True
        
        # Visit child nodes
        self.generic_visit(node)
        
        self.loop_depth -= 1
    
    def visit_Call(self, node):
        """Visit a function call node."""
        # Record function calls
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
            
            # Check for recursive call
            if node.func.id == self.current_function:
                self.has_recursive_call = True
                
                # Check if this is a divide and conquer recursive call
                for arg in node.args:
                    if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Div):
                        self.divide_and_conquer_pattern = True
        
        # Visit child nodes
        self.generic_visit(node)
    
    def visit_Expr(self, node):
        """Visit an expression node."""
        self.simple_operations += 1
        self.generic_visit(node)
    
    def get_complexity(self) -> str:
        """Determine the time complexity based on the analysis."""
        # If no loops or recursion, complexity is O(1)
        if self.max_loop_depth == 0 and not self.has_recursive_call:
            return "O(1)"
        
        # Binary search has O(log n) complexity
        if self.binary_search_pattern:
            return "O(log n)"
        
        # Recursive divide and conquer algorithms
        if self.divide_and_conquer_pattern:
            if self.max_loop_depth > 0:
                # Merge sort, quick sort like algorithms
                return "O(n log n)"
            else:
                # Simple recursive divide and conquer
                return "O(log n)"
        
        # Check for nested loops - polynomial complexity
        if self.max_loop_depth > 1:
            power = min(self.max_loop_depth, 3)  # Cap at n³ for readability
            return f"O(n{'' if power == 1 else '²' if power == 2 else '³'})"
            
        # Single loop - linear complexity
        if self.max_loop_depth == 1:
            return "O(n)"
            
        # Simple recursion without divide and conquer - can be exponential
        if self.has_recursive_call:
            if "fibonacci" in " ".join(self.function_definitions.keys()).lower():
                return "O(2ⁿ)"  # Exponential for naive recursive Fibonacci
            return "O(n)"  # Assume linear for other recursive functions
            
        # Default fallback
        return "O(n)"
        
    # Helper function to check if a string is used in indexing     
    def _is_used_in_indexing(self, name, node):
        """Check if a variable is used for indexing."""
        for n in ast.walk(node):
            if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Name):
                if n.slice.id == name:
                    return True
        return False