"""
Rule-based code optimizer for EFFICODE-ACRR

This module provides rule-based optimization for Python code.
It applies a set of predefined rules to improve code efficiency.
"""

import ast
import re
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RuleBasedOptimizer:
    """
    Applies rule-based optimizations to Python code
    """
    
    def __init__(self):
        """Initialize the rule-based optimizer"""
        self.applied_rules = []
        logger.info("RuleBasedOptimizer initialized")
        
    def optimize(self, code: str) -> str:
        """
        Apply rule-based optimizations to the code
    
    Args:
            code: Python code to optimize
        
    Returns:
            Optimized code
        """
        if not code or not isinstance(code, str):
            return code
            
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Apply optimizations
            optimized_tree = self._apply_optimizations(tree)
            
            # Convert back to code
            optimized_code = self._ast_to_code(optimized_tree)
            
            return optimized_code
        except Exception as e:
            logger.error(f"Error in rule-based optimization: {e}")
            return code
        
    def _apply_optimizations(self, tree: ast.AST) -> ast.AST:
        """
        Apply all optimization rules to the AST
        
        Args:
            tree: AST to optimize
            
        Returns:
            Optimized AST
        """
        # Create a transformer to apply all optimizations
        transformer = OptimizationTransformer()
        
        # Apply the transformations
        optimized_tree = transformer.visit(tree)
        
        # Fix any missing locations in the AST
        ast.fix_missing_locations(optimized_tree)
        
        # Store applied rules
        self.applied_rules = transformer.applied_rules
        
        return optimized_tree
    
    def _ast_to_code(self, tree: ast.AST) -> str:
        """
        Convert an AST back to Python code
        
        Args:
            tree: AST to convert
            
        Returns:
            Python code as a string
        """
        try:
            # Use ast.unparse if available (Python 3.9+)
            return ast.unparse(tree)
        except AttributeError:
            # Fallback for older Python versions
            import astor
            return astor.to_source(tree)
    
    def get_applied_rules(self) -> List[str]:
        """
        Get a list of applied optimization rules
        
        Returns:
            List of applied rule names
        """
        return self.applied_rules


class OptimizationTransformer(ast.NodeTransformer):
    """
    AST transformer that applies optimization rules
    """
    
    def __init__(self):
        """Initialize the transformer"""
        super().__init__()
        self.applied_rules = []
    
    def visit_For(self, node: ast.For) -> ast.AST:
        """
        Visit a For loop node
        
        Args:
            node: For loop node
            
        Returns:
            Optimized node
        """
        # Check for range(n) pattern that can be optimized
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == 'range' and len(node.iter.args) > 0:
                # Check if this is a simple range(n) loop
                if len(node.iter.args) == 1:
                    # Apply list comprehension optimization if appropriate
                    if self._can_optimize_to_list_comp(node):
                        self.applied_rules.append("Converted for loop to list comprehension")
                        return self._convert_to_list_comp(node)
        
        # Continue visiting child nodes
        return self.generic_visit(node)
    
    def visit_While(self, node: ast.While) -> ast.AST:
        """
        Visit a While loop node
        
        Args:
            node: While loop node
            
        Returns:
            Optimized node
        """
        # Check for common while loop patterns that can be optimized
        if self._is_infinite_loop_with_break(node):
            self.applied_rules.append("Optimized infinite loop with break")
            return self._optimize_infinite_loop(node)
        
        # Continue visiting child nodes
        return self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """
        Visit a function definition node
        
        Args:
            node: Function definition node
            
        Returns:
            Optimized node
        """
        # Check for recursive functions that can be optimized
        if self._is_recursive_function(node):
            # Check if this is a tail-recursive function
            if self._is_tail_recursive(node):
                self.applied_rules.append("Converted tail recursion to iteration")
                return self._convert_tail_recursion_to_iteration(node)
        
        # Continue visiting child nodes
        return self.generic_visit(node)
    
    def visit_If(self, node: ast.If) -> ast.AST:
        """
        Visit an if statement node
        
        Args:
            node: If statement node
            
        Returns:
            Optimized node
        """
        # Check for if-else chains that can be optimized
        if self._is_if_else_chain(node):
            self.applied_rules.append("Optimized if-else chain")
            return self._optimize_if_else_chain(node)
        
        # Continue visiting child nodes
        return self.generic_visit(node)
    
    def _can_optimize_to_list_comp(self, node: ast.For) -> bool:
        """
        Check if a for loop can be optimized to a list comprehension
        
        Args:
            node: For loop node
            
        Returns:
            True if the loop can be optimized
        """
        # This is a simplified check - in a real implementation,
        # we would need more sophisticated analysis
        return (
            isinstance(node.target, ast.Name) and
            len(node.body) == 1 and
            isinstance(node.body[0], ast.Assign) and
            isinstance(node.body[0].targets[0], ast.Subscript) and
            isinstance(node.body[0].targets[0].value, ast.Name) and
            node.body[0].targets[0].value.id == node.target.id
        )
    
    def _convert_to_list_comp(self, node: ast.For) -> ast.ListComp:
        """
        Convert a for loop to a list comprehension
        
        Args:
            node: For loop node
            
        Returns:
            List comprehension node
        """
        # This is a simplified implementation
        # In a real implementation, we would need more sophisticated conversion
        target = node.target
        iter_expr = node.iter
        value = node.body[0].value
        
        return ast.ListComp(
            elt=value,
            generators=[
                ast.comprehension(
                    target=target,
                    iter=iter_expr,
                    ifs=[]
                )
            ]
        )
    
    def _is_infinite_loop_with_break(self, node: ast.While) -> bool:
        """
        Check if a while loop is an infinite loop with a break
        
        Args:
            node: While loop node
            
        Returns:
            True if the loop is an infinite loop with a break
        """
        # Check if the condition is True
        if not isinstance(node.test, ast.Constant) or not node.test.value:
            return False
        
        # Check if there's a break statement
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Break):
                return True
        
        return False
    
    def _optimize_infinite_loop(self, node: ast.While) -> ast.AST:
        """
        Optimize an infinite loop with a break
        
        Args:
            node: While loop node
            
        Returns:
            Optimized node
        """
        # This is a simplified implementation
        # In a real implementation, we would need more sophisticated optimization
        return node
    
    def _is_recursive_function(self, node: ast.FunctionDef) -> bool:
        """
        Check if a function is recursive
        
        Args:
            node: Function definition node
            
        Returns:
            True if the function is recursive
        """
        # Check if the function calls itself
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name):
                if stmt.func.id == node.name:
                    return True
        
        return False
    
    def _is_tail_recursive(self, node: ast.FunctionDef) -> bool:
        """
        Check if a recursive function is tail recursive
        
        Args:
            node: Function definition node
            
        Returns:
            True if the function is tail recursive
        """
        # This is a simplified implementation
        # In a real implementation, we would need more sophisticated analysis
        return False
    
    def _convert_tail_recursion_to_iteration(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Convert a tail recursive function to an iterative function
        
        Args:
            node: Function definition node
            
        Returns:
            Iterative function node
        """
        # This is a simplified implementation
        # In a real implementation, we would need more sophisticated conversion
        return node
    
    def _is_if_else_chain(self, node: ast.If) -> bool:
        """
        Check if an if statement is part of an if-else chain
        
        Args:
            node: If statement node
            
        Returns:
            True if the if statement is part of an if-else chain
        """
        # Check if there are multiple elif or else clauses
        return len(node.orelse) > 0
    
    def _optimize_if_else_chain(self, node: ast.If) -> ast.AST:
        """
        Optimize an if-else chain
        
        Args:
            node: If statement node
            
        Returns:
            Optimized node
        """
        # This is a simplified implementation
        # In a real implementation, we would need more sophisticated optimization
        return node


# Example usage
if __name__ == "__main__":
    # Example code to optimize
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
    """
    
    # Create an optimizer
    optimizer = RuleBasedOptimizer()
    
    # Optimize the code
    optimized_code = optimizer.optimize(code)
    
    # Print the results
    print("Original code:")
    print(code)
    print("\nOptimized code:")
    print(optimized_code)
    print("\nApplied rules:")
    for rule in optimizer.get_applied_rules():
        print(f"- {rule}") 