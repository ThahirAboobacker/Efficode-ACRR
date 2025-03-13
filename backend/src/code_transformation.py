"""
Code Transformation Module for EFFICODE-ACRR

This module handles transforming code based on optimization suggestions:
- Parsing Python code into Abstract Syntax Trees (AST)
- Applying transformations to optimize code
- Replacing inefficient algorithms with optimal alternatives
- Generating optimized code from transformed ASTs

"""

import ast
import re
import logging
import inspect
import textwrap
from typing import Dict, List, Tuple, Union, Optional, Any, Callable

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import astor
except ImportError:
    astor = None
    logger.warning("astor package not found, falling back to ast.unparse")

try:
    import astunparse
except ImportError:
    astunparse = None
    logger.warning("astunparse package not found, code formatting may be affected")

# Try to import algorithm templates, or use defaults
try:
    from algorithm_templates import (
        SORTING_ALGORITHMS,
        SEARCH_ALGORITHMS,
        GRAPH_ALGORITHMS,
        DYNAMIC_PROGRAMMING_ALGORITHMS
    )
    logger.info("Loaded algorithm templates from module")
except ImportError:
    logger.info("Algorithm templates module not found, using built-in defaults")
    # Define default algorithm templates at the end of the file

class CodeTransformer:
    """Main class for code transformation operations"""
    
    def __init__(self):
        """Initialize the code transformer"""
        self.ast_tree = None
        self.original_code = None
        self.optimized_code = None
        
        # Register transformation rules
        self.transformation_rules = {
            'sorting': self._optimize_sorting,
            'search': self._optimize_search,
            'loop': self._optimize_loops,
            'data_structure': self._optimize_data_structures,
            'algorithm': self._replace_algorithm
        }
        
        # Algorithm replacements mapping
        self.algorithm_replacements = {
            'bubble_sort': 'quick_sort',
            'selection_sort': 'merge_sort',
            'insertion_sort': 'tim_sort',
            'linear_search': 'binary_search',
            'recursive_fibonacci': 'iterative_fibonacci',
            'naive_string_search': 'kmp_search',
            'bfs_recursive': 'bfs_iterative',
            'dfs_recursive': 'dfs_iterative',
            'brute_force_subset_sum': 'dynamic_subset_sum'
        }
        
        logger.info("CodeTransformer initialized")
    
    def parse_code(self, code: str) -> Optional[ast.AST]:
        """
        Parse Python code into an AST
        
        Args:
            code: Python code as string
            
        Returns:
            AST object or None if parsing fails
        """
        if not isinstance(code, str) or not code.strip():
            logger.error("Empty or invalid code provided")
            return None
            
        try:
            self.original_code = code
            self.ast_tree = ast.parse(code)
            return self.ast_tree
        except SyntaxError as e:
            logger.error(f"Syntax error while parsing code: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing code: {str(e)}")
            return None
    
    def transform_code(self, ast_tree: Optional[ast.AST] = None, 
                       optimizations: List[str] = ['all']) -> Optional[ast.AST]:
        """
        Apply transformations to the AST
        
        Args:
            ast_tree: AST to transform (uses stored AST if None)
            optimizations: List of optimization types to apply
                           Options: ['sorting', 'search', 'loop', 'data_structure', 'algorithm', 'all']
            
        Returns:
            Transformed AST or None if transformation fails
        """
        if ast_tree is not None:
            self.ast_tree = ast_tree
            
        if self.ast_tree is None:
            logger.error("No AST available for transformation")
            return None
        
        try:
            # Create a copy of the AST to transform
            transformer = ASTTransformer()
            
            # Apply specified transformations
            if 'all' in optimizations:
                optimizations = list(self.transformation_rules.keys())
            
            for opt in optimizations:
                if opt in self.transformation_rules:
                    logger.info(f"Applying {opt} optimization")
                    transformer.add_transformation(self.transformation_rules[opt])
                else:
                    logger.warning(f"Unknown optimization type: {opt}")
            
            # Apply the transformations
            transformed_ast = transformer.visit(self.ast_tree)
            ast.fix_missing_locations(transformed_ast)
            
            return transformed_ast
            
        except Exception as e:
            logger.error(f"Error transforming code: {str(e)}")
            return None
    
    def replace_algorithm(self, code: str, source_algo: str, target_algo: str) -> str:
        """
        Replace an algorithm with a more efficient one
        
        Args:
            code: Source code containing the algorithm
            source_algo: Name or identifier of the source algorithm
            target_algo: Name or identifier of the target algorithm
            
        Returns:
            Code with replaced algorithm
        """
        if not code or not source_algo or not target_algo:
            return code
        
        try:
            # Parse the code
            if self.ast_tree is None or self.original_code != code:
                self.parse_code(code)
            
            # If we still don't have a valid AST, return the original code
            if self.ast_tree is None:
                return code
            
            # Identify algorithm function
            func_finder = FunctionFinder(source_algo)
            func_finder.visit(self.ast_tree)
            
            if not func_finder.found_function:
                logger.warning(f"Could not find function for {source_algo}")
                return code
            
            # Get the replacement algorithm code
            replacement_code = self._get_algorithm_template(target_algo)
            if not replacement_code:
                logger.warning(f"No template found for {target_algo}")
                return code
            
            # Parse the replacement code
            try:
                replacement_ast = ast.parse(replacement_code)
            except SyntaxError:
                logger.error(f"Syntax error in replacement algorithm template for {target_algo}")
                return code
            
            # Create a new AST with the replaced function
            replacer = FunctionReplacer(func_finder.function_name, replacement_ast, target_algo)
            new_ast = replacer.visit(self.ast_tree)
            
            # Generate the new code
            return self.generate_optimized_code(new_ast)
            
        except Exception as e:
            logger.error(f"Error replacing algorithm: {str(e)}")
            return code
    
    def generate_optimized_code(self, ast_tree: Optional[ast.AST] = None) -> str:
        """
        Generate code from a transformed AST
        
        Args:
            ast_tree: AST to generate code from (uses transformed AST if None)
            
        Returns:
            Generated code as string
        """
        if ast_tree is None:
            if self.ast_tree is None:
                logger.error("No AST available for code generation")
                return ""
            ast_tree = self.ast_tree
        
        try:
            # Generate code using best available formatter
            if astor:
                try:
                    optimized_code = astor.to_source(ast_tree)
                except Exception as e:
                    logger.warning(f"astor failed to generate code: {e}")
                    if astunparse:
                        optimized_code = astunparse.unparse(ast_tree)
                    else:
                        # Use ast.unparse in Python 3.9+
                        try:
                            optimized_code = ast.unparse(ast_tree)
                        except AttributeError:
                            # For Python < 3.9, create a simple implementation
                            optimized_code = self._basic_unparse(ast_tree)
            elif astunparse:
                optimized_code = astunparse.unparse(ast_tree)
            else:
                # Use ast.unparse in Python 3.9+
                try:
                    optimized_code = ast.unparse(ast_tree)
                except AttributeError:
                    # For Python < 3.9, create a simple implementation
                    optimized_code = self._basic_unparse(ast_tree)
            
            # Clean up the generated code
            optimized_code = self._clean_generated_code(optimized_code)
            
            self.optimized_code = optimized_code
            return optimized_code
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            
            # If code generation fails, return the original code
            return self.original_code if self.original_code else ""
    
    def _clean_generated_code(self, code: str) -> str:
        """
        Clean up generated code for better readability
        
        Args:
            code: Generated code
            
        Returns:
            Cleaned code
        """
        # Remove extra newlines
        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
        
        # Fix indentation issues
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _basic_unparse(self, node: ast.AST) -> str:
        """
        Simple implementation of AST unparsing for Python < 3.9
        
        Args:
            node: AST node to unparse
            
        Returns:
            String representation of the code
        """
        # Handle module nodes
        if isinstance(node, ast.Module):
            return '\n'.join([self._basic_unparse(stmt) for stmt in node.body])
        
        # Handle function definitions
        elif isinstance(node, ast.FunctionDef):
            args = ', '.join([arg.arg for arg in node.args.args])
            body = '\n'.join(['    ' + self._basic_unparse(stmt) for stmt in node.body])
            return f"def {node.name}({args}):\n{body}"
        
        # Handle return statements
        elif isinstance(node, ast.Return):
            if node.value:
                return f"return {self._basic_unparse(node.value)}"
            return "return"
        
        # Handle assignments
        elif isinstance(node, ast.Assign):
            targets = ', '.join([self._basic_unparse(target) for target in node.targets])
            return f"{targets} = {self._basic_unparse(node.value)}"
        
        # Handle binary operations
        elif isinstance(node, ast.BinOp):
            left = self._basic_unparse(node.left)
            right = self._basic_unparse(node.right)
            op = {
                ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
                ast.FloorDiv: '//', ast.Mod: '%', ast.Pow: '**'
            }.get(type(node.op), '?')
            return f"({left} {op} {right})"
        
        # Handle names and constants
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            return str(node.value)
        
        # Handle unsupported nodes
        else:
            return f"# Unsupported AST node: {type(node).__name__}"
    
    def _get_algorithm_template(self, algorithm_name: str) -> str:
        """
        Get template code for a specific algorithm
        
        Args:
            algorithm_name: Name of the algorithm
            
        Returns:
            Template code or empty string if not found
        """
        # Try to find in sorting algorithms
        if algorithm_name in SORTING_ALGORITHMS:
            return SORTING_ALGORITHMS[algorithm_name]
        
        # Try to find in search algorithms
        if algorithm_name in SEARCH_ALGORITHMS:
            return SEARCH_ALGORITHMS[algorithm_name]
        
        # Try to find in graph algorithms
        if algorithm_name in GRAPH_ALGORITHMS:
            return GRAPH_ALGORITHMS[algorithm_name]
        
        # Try to find in dynamic programming algorithms
        if algorithm_name in DYNAMIC_PROGRAMMING_ALGORITHMS:
            return DYNAMIC_PROGRAMMING_ALGORITHMS[algorithm_name]
        
        # If algorithm name contains underscore, try splitting and searching again
        if '_' in algorithm_name:
            parts = algorithm_name.split('_')
            # Try variations like 'quick' instead of 'quick_sort'
            for part in parts:
                if part in SORTING_ALGORITHMS:
                    return SORTING_ALGORITHMS[part]
                if part in SEARCH_ALGORITHMS:
                    return SEARCH_ALGORITHMS[part]
        
        logger.warning(f"No template found for algorithm: {algorithm_name}")
        return ""
    
    def _optimize_sorting(self, node: ast.AST) -> ast.AST:
        """
        Optimize sorting algorithms
        
        Args:
            node: AST node to optimize
            
        Returns:
            Optimized AST node
        """
        # Implementation for sorting optimization
        # This is a placeholder - actual implementation would detect sorting
        # algorithms and replace them with more efficient versions
        return node
    
    def _optimize_search(self, node: ast.AST) -> ast.AST:
        """
        Optimize search algorithms
        
        Args:
            node: AST node to optimize
            
        Returns:
            Optimized AST node
        """
        # Implementation for search optimization
        return node
    
    def _optimize_loops(self, node: ast.AST) -> ast.AST:
        """
        Optimize loops for efficiency
        
        Args:
            node: AST node to optimize
            
        Returns:
            Optimized AST node
        """
        # Check if this is a nested loop that could be optimized
        if isinstance(node, ast.For):
            # Look for nested loops
            nested_loops = [n for n in ast.walk(node) 
                           if isinstance(n, ast.For) and n != node]
            
            if nested_loops:
                # Check for loop invariant code motion opportunities
                pass
        
        return node
    
    def _optimize_data_structures(self, node: ast.AST) -> ast.AST:
        """
        Optimize data structure usage
        
        Args:
            node: AST node to optimize
            
        Returns:
            Optimized AST node
        """
        # Implementation for data structure optimization
        return node
    
    def _replace_algorithm(self, node: ast.AST) -> ast.AST:
        """
        Replace an algorithm with a more efficient alternative
        
        Args:
            node: AST node to optimize
            
        Returns:
            Optimized AST node
        """
        # This is where you would implement general algorithm replacement
        # based on patterns detected in the AST
        return node


class ASTTransformer(ast.NodeTransformer):
    """AST transformer for applying multiple transformations"""
    
    def __init__(self):
        """Initialize the transformer"""
        super().__init__()
        self.transformations = []
    
    def add_transformation(self, transformation: Callable[[ast.AST], ast.AST]):
        """
        Add a transformation function
        
        Args:
            transformation: Function that takes and returns an AST node
        """
        self.transformations.append(transformation)
    
    def visit(self, node: ast.AST) -> ast.AST:
        """
        Visit a node and apply all transformations
        
        Args:
            node: AST node to visit
            
        Returns:
            Transformed node
        """
        # Apply the parent class's visit method first
        node = super().visit(node)
        
        # Apply each transformation
        for transform in self.transformations:
            if node is not None:
                node = transform(node)
        
        return node


class FunctionFinder(ast.NodeVisitor):
    """AST visitor for finding functions that match a specific algorithm"""
    
    def __init__(self, algorithm_name: str):
        """
        Initialize the function finder
        
        Args:
            algorithm_name: Name or identifier of the algorithm to find
        """
        self.algorithm_name = algorithm_name.lower()
        self.found_function = False
        self.function_name = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Visit function definitions and check for algorithm match
        
        Args:
            node: Function definition node
        """
        # Check if function name contains the algorithm name
        if self.algorithm_name in node.name.lower():
            self.found_function = True
            self.function_name = node.name
        
        # Continue visiting in case there are multiple matches
        self.generic_visit(node)


class RecursiveFunctionCallTransformer(ast.NodeTransformer):
    """AST transformer for updating recursive function calls"""
    
    def __init__(self, original_name: str, target_name: str):
        """
        Initialize the transformer
        
        Args:
            original_name: Original function name in recursive calls
            target_name: Target function name to replace with
        """
        super().__init__()
        self.original_name = original_name
        self.target_name = target_name
        self.transformed = False
    
    def visit_Call(self, node: ast.Call) -> ast.Call:
        """
        Visit function calls and update recursive calls
        
        Args:
            node: Function call node
            
        Returns:
            Updated function call node
        """
        # Check if this is a direct call to the original function
        if isinstance(node.func, ast.Name) and node.func.id == self.original_name:
            # Update the function name to the target name
            node.func.id = self.target_name
            self.transformed = True
        
        # Continue visiting child nodes
        return self.generic_visit(node)


class FunctionReplacer(ast.NodeTransformer):
    """AST transformer for replacing specific functions"""
    
    def __init__(self, function_name: str, replacement_ast: ast.AST, original_replacement_name: str = None):
        """
        Initialize the function replacer
        
        Args:
            function_name: Name of the function to replace
            replacement_ast: AST containing the replacement function
            original_replacement_name: Original name of the replacement function (for recursive calls)
        """
        super().__init__()
        self.function_name = function_name
        self.original_replacement_name = original_replacement_name
        self.replacement_function = None
        
        # Extract the function definition from the replacement AST
        if isinstance(replacement_ast, ast.Module):
            for node in replacement_ast.body:
                if isinstance(node, ast.FunctionDef):
                    # Store the original name before modifying
                    if self.original_replacement_name is None:
                        self.original_replacement_name = node.name
                    
                    # Fix recursive calls in the replacement function
                    self._fix_recursive_calls(node)
                    
                    # Set the replacement function name to match the target
                    node.name = function_name
                    self.replacement_function = node
                    break
    
    def _fix_recursive_calls(self, func_node: ast.FunctionDef):
        """
        Fix recursive function calls in the replacement function
        
        Args:
            func_node: Function definition node
        """
        # Only fix recursive calls if we have the original name
        if self.original_replacement_name:
            transformer = RecursiveFunctionCallTransformer(
                self.original_replacement_name, 
                self.function_name
            )
            transformer.visit(func_node)
            
            if transformer.transformed:
                logger.info(f"Fixed recursive calls from '{self.original_replacement_name}' to '{self.function_name}'")
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """
        Visit function definitions and replace if name matches
        
        Args:
            node: Function definition node
            
        Returns:
            Original or replacement function node
        """
        if node.name == self.function_name and self.replacement_function is not None:
            # Preserve the original function arguments
            self.replacement_function.args = node.args
            
            # Make a copy to avoid modifying the original
            import copy
            replacement = copy.deepcopy(self.replacement_function)
            
            # Add original docstring if the replacement doesn't have one
            if not replacement.body or not isinstance(replacement.body[0], ast.Expr):
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                    replacement.body.insert(0, node.body[0])
            
            return replacement
        
        return node


# Default algorithm templates if external module not available
if 'algorithm_templates' not in globals():
    # Simple templates for common algorithms
    SORTING_ALGORITHMS = {
        'quick_sort': """
def quick_sort(arr):
    \"\"\"
    Quick sort implementation with O(n log n) average time complexity.
    \"\"\"
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
""",
        
        'merge_sort': """
def merge_sort(arr):
    \"\"\"
    Merge sort implementation with O(n log n) time complexity.
    \"\"\"
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result
"""
    }
    
    SEARCH_ALGORITHMS = {
        'binary_search': """
def binary_search(arr, target):
    \"\"\"
    Binary search implementation with O(log n) time complexity.
    Requires a sorted array.
    \"\"\"
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Target not found
"""
    }
    
    GRAPH_ALGORITHMS = {}
    DYNAMIC_PROGRAMMING_ALGORITHMS = {}

def main():
    """Example usage of the code transformer"""
    # Example bubble sort code
    bubble_sort_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Test with a sample array
test_array = [64, 34, 25, 12, 22, 11, 90]
print(bubble_sort(test_array))
"""
    
    transformer = CodeTransformer()
    
    # Replace bubble sort with quick sort
    optimized_code = transformer.replace_algorithm(
        bubble_sort_code, 'bubble_sort', 'quick_sort'
    )
    
    print("Original code:")
    print(bubble_sort_code)
    print("\nOptimized code:")
    print(optimized_code)
    
    # Execute the optimized code to demonstrate it works
    print("\nExecuting optimized code:")
    exec_globals = {}
    exec(optimized_code, exec_globals)

if __name__ == "__main__":
    main()