"""
Rule-based optimization module for Python code.

This module implements various optimization techniques:
- Dead code elimination
- Unused variable removal
- Loop optimizations
- Memory usage optimization
"""

import ast
import copy
import logging
import traceback
import re
import sys
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional, Union, Set

logger = logging.getLogger(__name__)

@dataclass
class OptimizationChange:
    """Record of an optimization change."""
    type: str
    line_number: int
    description: str
    original_code: str = ""
    optimized_code: str = ""
    category: str = "optimization"

@dataclass
class ConstantValue:
    """Record of a constant value for propagation."""
    value: Any
    node: ast.Constant

class OptimizerConfig:
    """Configuration for the optimizer."""
    def __init__(self):
        self.max_inline_size = 3  # Maximum number of statements to inline
        self.max_loop_unroll = 4  # Maximum loop iterations to unroll
        self.apply_constant_folding = True
        self.apply_dead_code_elimination = True
        self.apply_loop_optimization = True
        self.apply_repeated_computation_elimination = True  # New option for repeated computations

# Main optimizer implementation
class RuleBasedOptimizer:
    """Rule-based optimizer for Python code."""
    
    def __init__(self, config: OptimizerConfig = None):
        """Initialize the optimizer."""
        self.config = config or OptimizerConfig()
        self.changes = []
        self.used_names = set()  # Track used variable names
        self.constant_values = {}  # Track constant values for propagation
        self.unreachable_nodes = set()  # Track unreachable nodes
    
    def optimize(self, code: str, level: str = 'medium') -> tuple:
        """
        Optimize the given code and return the optimized code along with complexity metrics.
    
    Args:
            code: The code to optimize
            level: Optimization level ('low', 'medium', 'high')
        
    Returns:
            tuple: (optimized_code, original_complexity, optimized_complexity, explanation)
        """
        try:
            # Reset tracking sets
            self.used_names = set()
            self.constant_values = {}
            self.unreachable_nodes = set()
            self.changes = []
            
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Add parent references for unreachable code detection
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    child.parent_node = node
            
            # Calculate original complexity
            original_complexity = self._calculate_complexity(tree)
            
            # First pass: collect used names and constant values
            self.visit(tree)
            
            # Detect unreachable code
            self._detect_unreachable_code(tree)
            
            # Apply optimizations based on level
            if level == 'low':
                # Apply only basic optimizations
                tree = self.optimize_basic(tree)
            elif level == 'medium':
                # Apply medium optimizations
                tree = self.optimize_basic(tree)
                tree = self.optimize_medium(tree)
            else:  # high
                # Apply all optimizations
                tree = self.optimize_basic(tree)
                tree = self.optimize_medium(tree)
                tree = self.optimize_advanced(tree)
            
            # Remove unused variables and dead code
            tree = self.remove_unused_variables(tree)
            tree = self.remove_unreachable_code(tree)
            
            # Eliminate repeated computations
            if self.config.apply_repeated_computation_elimination:
                tree = self._eliminate_repeated_computations(tree)
            
            # Calculate optimized complexity
            optimized_complexity = self._calculate_complexity(tree)
            
            # Generate explanation
            explanation = self._generate_explanation(original_complexity, optimized_complexity)
            
            # Convert back to code
            optimized_code = ast.unparse(tree)
            
            # Add documentation and complexity information
            if optimized_code != code:
                optimized_code = self._add_complexity_documentation(optimized_code, original_complexity, optimized_complexity)
                
                # Add rule-based specific improvement
                self.changes.append({
                    'type': 'algorithm_replacement',
                    'description': self._determine_main_improvement(code, optimized_code, original_complexity, optimized_complexity),
                    'category': 'performance'
                })
            
            return optimized_code, original_complexity, optimized_complexity, explanation
            
        except Exception as e:
            logger.error(f"Error in optimization: {str(e)}")
            logger.error(traceback.format_exc())
            return code, "O(?)", "O(?)", f"Error in optimization: {str(e)}"
    
    def visit(self, node):
        """Visit an AST node to collect information."""
        # Track used names
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            
        # Track constant values for propagation
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                    self.constant_values[target.id] = ConstantValue(
                        value=node.value.value,
                        node=node.value
                    )
                    
        # Track more complex variable usages
        if isinstance(node, ast.For):
            # The loop variable is considered used
            if isinstance(node.target, ast.Name):
                self.used_names.add(node.target.id)
        
        # Mark variables used in function calls
        if isinstance(node, ast.Call):
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    self.used_names.add(arg.id)
            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Name):
                    self.used_names.add(keyword.value.id)
        
        # Mark variables used in return statements
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
                    
        # Visit child nodes
        for child in ast.iter_child_nodes(node):
            self.visit(child)
    
    def optimize_basic(self, tree):
        """Apply basic optimizations."""
        # Apply constant folding if enabled
        if self.config.apply_constant_folding:
            tree = self._fold_constants(tree)
        
        # Detect common algorithm patterns
        tree = self._detect_common_algorithms(tree)
        
        return tree
    
    def _fold_constants(self, tree):
        """Fold constant expressions in the AST."""
        class ConstantFolder(ast.NodeTransformer):
            def __init__(self, changes):
                self.changes = changes
                self.change_made = False

            def record_change(self, node, value):
                self.changes.append({
                    'type': 'constant_folding',
                    'description': f'Folded constant expression to {value}',
                    'category': 'optimization',
                    'location': getattr(node, 'lineno', None)
                })

            def _is_safe_to_evaluate(self, op, left_val, right_val=None):
                """Check if an operation is safe to evaluate as a constant."""
                if isinstance(op, ast.Pow):
                    # Limit exponentiation to avoid excessive computation
                    if isinstance(right_val, (int, float)) and isinstance(left_val, (int, float)):
                        if right_val > 100 or left_val > 1000:
                            return False
                elif isinstance(op, (ast.LShift, ast.RShift)):
                    # Limit bit shifts to avoid excessive values
                    if isinstance(right_val, int) and right_val > 64:
                        return False
                return True

            def _safe_eval_binop(self, op, left_val, right_val):
                """Safely evaluate a binary operation."""
                try:
                    if isinstance(op, ast.Add):
                        return left_val + right_val
                    elif isinstance(op, ast.Sub):
                        return left_val - right_val
                    elif isinstance(op, ast.Mult):
                        return left_val * right_val
                    elif isinstance(op, ast.Div):
                        if right_val == 0:
                            return None  # Division by zero
                        return left_val / right_val
                    elif isinstance(op, ast.FloorDiv):
                        if right_val == 0:
                            return None  # Division by zero
                        return left_val // right_val
                    elif isinstance(op, ast.Mod):
                        if right_val == 0:
                            return None  # Modulo by zero
                        return left_val % right_val
                    elif isinstance(op, ast.Pow):
                        return left_val ** right_val
                    elif isinstance(op, ast.LShift):
                        if isinstance(left_val, int) and isinstance(right_val, int):
                            return left_val << right_val
                    elif isinstance(op, ast.RShift):
                        if isinstance(left_val, int) and isinstance(right_val, int):
                            return left_val >> right_val
                    elif isinstance(op, ast.BitOr):
                        if isinstance(left_val, int) and isinstance(right_val, int):
                            return left_val | right_val
                    elif isinstance(op, ast.BitXor):
                        if isinstance(left_val, int) and isinstance(right_val, int):
                            return left_val ^ right_val
                    elif isinstance(op, ast.BitAnd):
                        if isinstance(left_val, int) and isinstance(right_val, int):
                            return left_val & right_val
                    elif isinstance(op, ast.MatMult):
                        if isinstance(left_val, (list, tuple)) and isinstance(right_val, (list, tuple)):
                            # Handle matrix multiplication for simple cases
                            return None  # Too complex for constant folding
                except Exception:
                    return None
                return None

            def _safe_eval_unaryop(self, op, operand_val):
                """Safely evaluate a unary operation."""
                try:
                    if isinstance(op, ast.UAdd):
                        return +operand_val
                    elif isinstance(op, ast.USub):
                        return -operand_val
                    elif isinstance(op, ast.Not):
                        return not operand_val
                    elif isinstance(op, ast.Invert):
                        if isinstance(operand_val, int):
                            return ~operand_val
                except Exception:
                    return None
                return None

            def _safe_eval_compare(self, ops, left_val, comparators_vals):
                """Safely evaluate a comparison expression."""
                if len(ops) != 1 or len(comparators_vals) != 1:
                    return None  # Only handle simple comparisons
                
                right_val = comparators_vals[0]
                op = ops[0]
                
                try:
                    if isinstance(op, ast.Eq):
                        return left_val == right_val
                    elif isinstance(op, ast.NotEq):
                        return left_val != right_val
                    elif isinstance(op, ast.Lt):
                        return left_val < right_val
                    elif isinstance(op, ast.LtE):
                        return left_val <= right_val
                    elif isinstance(op, ast.Gt):
                        return left_val > right_val
                    elif isinstance(op, ast.GtE):
                        return left_val >= right_val
                    elif isinstance(op, ast.Is):
                        return left_val is right_val
                    elif isinstance(op, ast.IsNot):
                        return left_val is not right_val
                    elif isinstance(op, ast.In):
                        return left_val in right_val
                    elif isinstance(op, ast.NotIn):
                        return left_val not in right_val
                except Exception:
                    return None
                return None

            def _safe_eval_boolop(self, op, values_vals):
                """Safely evaluate a boolean operation."""
                try:
                    if isinstance(op, ast.And):
                        result = True
                        for val in values_vals:
                            result = result and val
                            # Short-circuit
                            if not result:
                                break
                        return result
                    elif isinstance(op, ast.Or):
                        result = False
                        for val in values_vals:
                            result = result or val
                            # Short-circuit
                            if result:
                                break
                        return result
                except Exception:
                    return None
                return None

            def visit_BinOp(self, node):
                """Fold binary operations with constant operands."""
                self.generic_visit(node)
                
                value = self._eval_literal(node)
                if value is not None:
                    if not self.change_made:
                        self.changes.append({
                            'type': 'constant_folding',
                            'description': f'Folded constant expression to {value}',
                            'category': 'optimization'
                        })
                        self.change_made = True
                    
                    # Convert the value to an AST constant node
                    return ast.Constant(value=value)
                
                return node

            def visit_UnaryOp(self, node):
                """Fold unary operations with constant operands."""
                self.generic_visit(node)
                
                value = self._eval_literal(node)
                if value is not None:
                    if not self.change_made:
                        self.changes.append({
                            'type': 'constant_folding',
                            'description': f'Folded constant expression to {value}',
                            'category': 'optimization'
                        })
                        self.change_made = True
                    
                    # Convert the value to an AST constant node
                    return ast.Constant(value=value)
                
                return node

            def visit_BoolOp(self, node):
                """Fold boolean operations with constant operands."""
                self.generic_visit(node)
                
                value = self._eval_literal(node)
                if value is not None:
                    if not self.change_made:
                        self.changes.append({
                            'type': 'constant_folding',
                            'description': f'Folded constant boolean expression to {value}',
                            'category': 'optimization'
                        })
                        self.change_made = True
                    
                    # Convert the value to an AST constant node
                    return ast.Constant(value=value)
                
                return node

            def visit_Compare(self, node):
                """Fold comparison operations with constant operands."""
                self.generic_visit(node)
                
                value = self._eval_literal(node)
                if value is not None:
                    if not self.change_made:
                        self.changes.append({
                            'type': 'constant_folding',
                            'description': f'Folded constant comparison to {value}',
                            'category': 'optimization'
                        })
                        self.change_made = True
                    
                    # Convert the value to an AST constant node
                    return ast.Constant(value=value)
                
                return node

            def _eval_literal(self, node):
                """Evaluate an expression to a constant value if possible."""
                # For simple literals like numbers, strings, booleans
                if isinstance(node, ast.Constant):
                    return node.value
                
                # For unary operations
                elif isinstance(node, ast.UnaryOp):
                    operand_val = self._eval_literal(node.operand)
                    if operand_val is None:
                        return None
                    return self._safe_eval_unaryop(node.op, operand_val)
                
                # For binary operations
                elif isinstance(node, ast.BinOp):
                    left = self._eval_literal(node.left)
                    right = self._eval_literal(node.right)
                    if left is None or right is None:
                        return None
                    
                    if not self._is_safe_to_evaluate(node.op, left, right):
                        return None
                    
                    return self._safe_eval_binop(node.op, left, right)
                
                # For boolean operations (and, or)
                elif isinstance(node, ast.BoolOp):
                    values_vals = []
                    for value in node.values:
                        val = self._eval_literal(value)
                        if val is None:
                            return None
                        values_vals.append(val)
                    
                    return self._safe_eval_boolop(node.op, values_vals)
                
                # For comparison operations
                elif isinstance(node, ast.Compare):
                    if len(node.ops) != 1 or len(node.comparators) != 1:
                        return None
                    
                    left = self._eval_literal(node.left)
                    right = self._eval_literal(node.comparators[0])
                    if left is None or right is None:
                        return None
                    
                    return self._safe_eval_compare(node.ops, left, [right])
                
                # For literals like tuples, lists, and dicts with constant elements
                elif isinstance(node, ast.Tuple):
                    elts = []
                    for elt in node.elts:
                        val = self._eval_literal(elt)
                        if val is None:
                            return None
                        elts.append(val)
                    return tuple(elts)
                    
                elif isinstance(node, ast.List):
                    elts = []
                    for elt in node.elts:
                        val = self._eval_literal(elt)
                        if val is None:
                            return None
                        elts.append(val)
                    return elts
                
                return None

        folder = ConstantFolder(self.changes)
        tree = folder.visit(tree)
        
        # Fix any missing location info
        ast.fix_missing_locations(tree)
        
        return tree
    
    def _detect_common_algorithms(self, tree):
        """Detect and optimize common algorithms."""
        class AlgorithmDetector(ast.NodeTransformer):
            def __init__(self, changes):
                self.changes = changes
                self.changes_made = False
                self.optimized_fibonacci = False
                self.optimized_bubble_sort = False
                self.optimized_linear_search = False
                self.optimized_min_max = False
                self.replacements = {}  # Track variable replacements
                
            def visit_FunctionDef(self, node):
                # Reset replacements for each function
                self.replacements = {}
                
                # First pass: collect all potential replacements for max/min optimization
                for i, stmt in enumerate(node.body):
                    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                        var_name = stmt.targets[0].id
                        if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'sorted':
                            # Remember this assignment for potential replacement
                            # Store the variable name, the sorted value, and the index in the function body
                            if len(stmt.value.args) == 1:
                                self.replacements[var_name] = [stmt.value.args[0], i]
                
                # Check for Fibonacci pattern - recursive implementation
                # Use pattern detection based on function structure, not just name
                is_fibonacci = False
                
                # Check primary indicators of recursive Fibonacci pattern
                has_recursive_structure = (
                    # Look for return statement with recursive pattern
                    any(isinstance(stmt, ast.Return) and 
                        isinstance(stmt.value, ast.BinOp) and
                        isinstance(stmt.value.op, ast.Add) and
                        isinstance(stmt.value.left, ast.Call) and
                        isinstance(stmt.value.right, ast.Call)
                        for stmt in ast.walk(node)) and
                    
                    # Check for base cases (f(0)=0, f(1)=1 pattern)
                    any(isinstance(stmt, ast.If) and 
                        any(isinstance(child, ast.Return) and
                            isinstance(child.value, ast.Constant) and
                            child.value.value in (0, 1)
                            for child in ast.walk(stmt))
                        for stmt in node.body)
                )
                
                # Strengthen detection by checking function name if available
                name_is_fibonacci = (node.name.lower().find('fib') >= 0)
                
                # Determine if this is a fibonacci function
                is_fibonacci = has_recursive_structure and (
                    name_is_fibonacci or 
                    len(node.args.args) == 1  # Fibonacci typically takes one argument
                )
                
                if is_fibonacci:
                    # Replace with optimized Fibonacci
                    if not self.optimized_fibonacci:
                        self.changes.append({
                            'type': 'algorithm_replacement',
                            'description': 'Replaced recursive Fibonacci with dynamic programming implementation',
                            'category': 'performance'
                        })
                        self.optimized_fibonacci = True
                    
                    # Create optimized Fibonacci implementation with dynamic programming
                    fib_func_name = node.name
                    arg_name = node.args.args[0].arg if node.args.args else 'n'
                    
                    # Preserve function docstring if it exists
                    docstring = None
                    if (len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        docstring = node.body[0]
                    
                    # Create the new optimized body
                    optimized_body_str = f"""
def {fib_func_name}({arg_name}):
    if {arg_name} <= 0:
        return 0
    elif {arg_name} == 1:
        return 1
    
    # Use dynamic programming to avoid exponential recursion
    a, b = 0, 1
    for i in range(2, {arg_name} + 1):
        a, b = b, a + b
    return b
"""
                    # Parse the string to create AST nodes
                    new_func = ast.parse(optimized_body_str).body[0]
                    
                    # Add docstring if the original function had one
                    if docstring:
                        new_func.body.insert(0, docstring)
                    else:
                        # Add a default docstring explaining the optimization
                        doc_expr = ast.Expr(
                            value=ast.Constant(
                                value="Optimized Fibonacci implementation using dynamic programming.\n"
                                      "Time Complexity: O(n) instead of O(2^n) for recursive approach."
                            )
                        )
                        new_func.body.insert(0, doc_expr)
                    
                    # Copy original decorators, returns, etc.
                    new_func.decorator_list = node.decorator_list
                    new_func.returns = node.returns
                    
                    # Copy location information
                    ast.copy_location(new_func, node)
                    for i, stmt in enumerate(new_func.body):
                        if i < len(node.body):
                            ast.copy_location(stmt, node.body[i])
                        else:
                            ast.copy_location(stmt, node.body[-1])
                    
                    # Fix any missing locations
                    ast.fix_missing_locations(new_func)
                    
                    # Return the completely new function
                    return new_func

                # Check for bubble sort pattern
                is_bubble_sort = False
                has_nested_loops = False
                has_swapping = False
                
                # Check for nested loops
                for stmt in node.body:
                    if isinstance(stmt, ast.For):
                        # Look for inner loop within outer loop body
                        for inner_stmt in stmt.body:
                            if isinstance(inner_stmt, ast.For):
                                has_nested_loops = True
                                break
                
                # Check for swapping pattern (a, b = b, a)
                for stmt in ast.walk(node):
                    # Look for assignment with tuple unpacking which is typical for swaps
                    if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Tuple) and isinstance(stmt.value, ast.Tuple):
                        # Check if it's a swap pattern
                        if (len(stmt.targets[0].elts) == 2 and len(stmt.value.elts) == 2 and
                            isinstance(stmt.targets[0].elts[0], ast.Subscript) and
                            isinstance(stmt.targets[0].elts[1], ast.Subscript) and
                            isinstance(stmt.value.elts[0], ast.Subscript) and
                            isinstance(stmt.value.elts[1], ast.Subscript)):
                            has_swapping = True
                            break
                
                # Name-based detection as supporting indicator
                name_is_sort = (node.name.lower().find('sort') >= 0)
                
                # Determine if this is a bubble sort
                is_bubble_sort = has_nested_loops and has_swapping and (
                    name_is_sort or
                    # Additional checks could go here
                    True
                )
                
                if is_bubble_sort:
                    # Replace with optimized sort
                    if not self.optimized_bubble_sort:
                        self.changes.append({
                            'type': 'algorithm_replacement',
                            'description': 'Replaced bubble sort with built-in sorted() function',
                            'category': 'performance'
                        })
                        self.optimized_bubble_sort = True
                    
                    # Create optimized implementation
                    sort_func_name = node.name
                    # Preserve original arguments
                    arg_list = []
                    for arg in node.args.args:
                        arg_list.append(arg.arg)
                    
                    arg_str = ", ".join(arg_list)
                    first_arg = arg_list[0] if arg_list else 'arr'
                    
                    # Preserve docstring if it exists
                    docstring = None
                    if (len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        docstring = node.body[0]
                    
                    # Create optimized function
                    optimized_body_str = f"""
def {sort_func_name}({arg_str}):
    return sorted({first_arg})
"""
                    # Parse into AST
                    new_func = ast.parse(optimized_body_str).body[0]
                    
                    # Add docstring
                    if docstring:
                        new_func.body.insert(0, docstring)
                    else:
                        # Add default docstring
                        doc_expr = ast.Expr(
                            value=ast.Constant(
                                value="Optimized sorting implementation using Python built-in sorted().\n"
                                      "Time Complexity: O(n log n) instead of O(n²) for bubble sort."
                            )
                        )
                        new_func.body.insert(0, doc_expr)
                    
                    # Copy original decorators, returns, etc.
                    new_func.decorator_list = node.decorator_list
                    new_func.returns = node.returns
                    
                    # Copy location information
                    ast.copy_location(new_func, node)
                    for i, stmt in enumerate(new_func.body):
                        if i < len(node.body):
                            ast.copy_location(stmt, node.body[i])
                        else:
                            ast.copy_location(stmt, node.body[-1])
                    
                    # Fix any missing locations
                    ast.fix_missing_locations(new_func)
                    
                    return new_func
                    
                # Check for linear search pattern
                is_linear_search = False
                has_loop = False
                has_comparison = False
                has_return_in_loop = False
                
                # Check for loop with comparison and return
                for stmt in node.body:
                    if isinstance(stmt, ast.For):
                        has_loop = True
                        for inner_stmt in stmt.body:
                            # Look for comparison within loop
                            if isinstance(inner_stmt, ast.If):
                                has_comparison = True
                                # Check for return statement in if body
                                for if_stmt in inner_stmt.body:
                                    if isinstance(if_stmt, ast.Return):
                                        has_return_in_loop = True
                                        break
                
                # Name-based detection as supporting indicator
                name_is_search = (node.name.lower().find('search') >= 0 or 
                                 node.name.lower().find('find') >= 0)
                
                # Determine if this is a linear search
                is_linear_search = has_loop and has_comparison and has_return_in_loop and (
                    name_is_search or 
                    len(node.args.args) >= 2  # Linear search typically takes array and target
                )
                
                if is_linear_search:
                    # Replace with optimized search
                    if not self.optimized_linear_search:
                        self.changes.append({
                            'type': 'algorithm_replacement',
                            'description': 'Replaced linear search with more efficient implementation',
                            'category': 'performance'
                        })
                        self.optimized_linear_search = True
                    
                    # Determine arguments
                    search_func_name = node.name
                    arg_list = []
                    for arg in node.args.args:
                        arg_list.append(arg.arg)
                    
                    array_arg_name = arg_list[0] if len(arg_list) > 0 else 'arr'
                    target_arg_name = arg_list[1] if len(arg_list) > 1 else 'target'
                    arg_str = ", ".join(arg_list)
                    
                    # Preserve docstring if it exists
                    docstring = None
                    if (len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        docstring = node.body[0]
                    
                    # Create optimized implementation
                    optimized_body_str = f"""
def {search_func_name}({arg_str}):
    try:
        return {array_arg_name}.index({target_arg_name})
    except ValueError:
        return -1
"""
                    # Parse into AST
                    new_func = ast.parse(optimized_body_str).body[0]
                    
                    # Add docstring
                    if docstring:
                        new_func.body.insert(0, docstring)
                    else:
                        # Add default docstring
                        doc_expr = ast.Expr(
                            value=ast.Constant(
                                value="Optimized search implementation using Python built-in 'in' operator and index().\n"
                                      "Time Complexity: Best O(1), Average O(n) instead of always O(n) for linear search."
                            )
                        )
                        new_func.body.insert(0, doc_expr)
                    
                    # Copy original decorators, returns, etc.
                    new_func.decorator_list = node.decorator_list
                    new_func.returns = node.returns
                    
                    # Copy location information
                    ast.copy_location(new_func, node)
                    for i, stmt in enumerate(new_func.body):
                        if i < len(node.body):
                            ast.copy_location(stmt, node.body[i])
                        else:
                            ast.copy_location(stmt, node.body[-1])
                    
                    # Fix any missing locations
                    ast.fix_missing_locations(new_func)
                    
                    return new_func
                
                # Visit children to apply other transformations
                self.generic_visit(node)
                
                # Second pass: process the replacements we flagged for max/min
                modified = False
                for var_name, value_list in list(self.replacements.items()):
                    if var_name + "_replaced" in self.replacements:
                        # This assignment needs to be updated
                        if isinstance(value_list, list) and len(value_list) == 2:
                            arg_node, idx = value_list
                            if idx < len(node.body) and isinstance(node.body[idx], ast.Assign):
                                original_assign = node.body[idx]
                                if self.replacements.get(var_name + "_replaced") == "max":
                                    # Replace sorted() with max()
                                    new_assign = ast.Assign(
                                        targets=[ast.Name(id=var_name, ctx=ast.Store())],
                                        value=ast.Call(
                                            func=ast.Name(id='max', ctx=ast.Load()),
                                            args=[arg_node],
                                            keywords=[]
                                        )
                                    )
                                    # Copy source location for better error messages
                                    ast.copy_location(new_assign, original_assign)
                                    ast.copy_location(new_assign.targets[0], original_assign.targets[0])
                                    ast.copy_location(new_assign.value, original_assign.value)
                                    ast.fix_missing_locations(new_assign)
                                    node.body[idx] = new_assign
                                    modified = True
                                elif self.replacements.get(var_name + "_replaced") == "min":
                                    # Replace sorted() with min()
                                    new_assign = ast.Assign(
                                        targets=[ast.Name(id=var_name, ctx=ast.Store())],
                                        value=ast.Call(
                                            func=ast.Name(id='min', ctx=ast.Load()),
                                            args=[arg_node],
                                            keywords=[]
                                        )
                                    )
                                    # Copy source location for better error messages
                                    ast.copy_location(new_assign, original_assign)
                                    ast.copy_location(new_assign.targets[0], original_assign.targets[0])
                                    ast.copy_location(new_assign.value, original_assign.value)
                                    ast.fix_missing_locations(new_assign)
                                    node.body[idx] = new_assign
                                    modified = True
                
                # Fix any missing locations if we modified the AST
                if modified:
                    ast.fix_missing_locations(node)
                
                return node
        
        # Apply algorithm detection
        detector = AlgorithmDetector(self.changes)
        return detector.visit(tree)
    
    def optimize_medium(self, tree):
        """Apply medium-level optimizations."""
        # Apply loop optimizations
        if self.config.apply_loop_optimization:
            class LoopOptimizer(ast.NodeTransformer):
                def __init__(self, changes):
                    self.changes = changes
                    self.changes_made = False
                
                def visit_For(self, node):
                    # Detect string concatenation in loop
                    if (len(node.body) == 1 and 
                        isinstance(node.body[0], ast.AugAssign) and
                        isinstance(node.body[0].op, ast.Add) and
                        isinstance(node.body[0].target, ast.Name) and
                        isinstance(node.body[0].value, ast.Name)):
                        
                        # Check if we're appending to a string
                        target_var = node.body[0].target.id
                        append_var = node.body[0].value.id
                        
                        # Check if the iterator is the append var
                        if (isinstance(node.target, ast.Name) and node.target.id == append_var):
                            # Try to determine if the target is likely a string
                            is_likely_string = False
                            
                            # Check if this is part of a function
                            if hasattr(node, 'parent_node') and isinstance(node.parent_node, ast.FunctionDef):
                                for stmt in node.parent_node.body:
                                    # Look for initialization of the target variable
                                    if (isinstance(stmt, ast.Assign) and 
                                        len(stmt.targets) == 1 and
                                        isinstance(stmt.targets[0], ast.Name) and
                                        stmt.targets[0].id == target_var):
                                        
                                        # Check for initialization to empty string
                                        if (isinstance(stmt.value, ast.Constant) and 
                                            isinstance(stmt.value.value, str) and 
                                            stmt.value.value == ""):
                                            is_likely_string = True
                                            break
                            
                            if is_likely_string:
                                # Replace with join
                                join_call = ast.Assign(
                                    targets=[ast.Name(id=target_var, ctx=ast.Store())],
                                    value=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Constant(value=""),
                                            attr="join",
                                            ctx=ast.Load()
                                        ),
                                        args=[node.iter],
                                        keywords=[]
                                    )
                                )
                                
                                # Add to changes
                                if not self.changes_made:
                                    self.changes.append({
                                        'type': 'string_join_optimization',
                                        'description': 'Replaced inefficient string concatenation with join() method',
                                        'category': 'performance'
                                    })
                                    self.changes_made = True
                                
                                # Copy location for better error messages
                                return ast.copy_location(join_call, node)
                    
                    # Transform range(len(x)) pattern to enumerate
                    if (isinstance(node.iter, ast.Call) and 
                        isinstance(node.iter.func, ast.Name) and 
                        node.iter.func.id == 'range' and 
                        len(node.iter.args) == 1 and 
                        isinstance(node.iter.args[0], ast.Call) and
                        isinstance(node.iter.args[0].func, ast.Name) and
                        node.iter.args[0].func.id == 'len' and
                        len(node.iter.args[0].args) == 1):
                        
                        # Get the collection being iterated over
                        collection = node.iter.args[0].args[0]
                        
                        # Create new target with index and value
                        if isinstance(node.target, ast.Name):
                            # Create a tuple target for index, value
                            new_target = ast.Tuple(
                                elts=[
                                    node.target,  # Keep the original index variable
                                    ast.Name(id=f"value_{node.target.id}", ctx=ast.Store())  # Create value variable
                                ],
                                ctx=ast.Store()
                            )
                            
                            # Create new enumerate call
                            new_iter = ast.Call(
                                func=ast.Name(id='enumerate', ctx=ast.Load()),
                                args=[collection],
                                keywords=[]
                            )
                            
                            # Replace uses of collection[i] with value_i in the body
                            class IndexReplacer(ast.NodeTransformer):
                                def __init__(self, collection_node, index_var, value_var):
                                    self.collection_node = collection_node
                                    self.index_var = index_var
                                    self.value_var = value_var
                                
                                def visit_Subscript(self, node):
                                    self.generic_visit(node)
                                    
                                    # Check if this is collection[index_var]
                                    if (isinstance(node.value, ast.Name) and 
                                        ast.unparse(node.value) == ast.unparse(self.collection_node) and
                                        isinstance(node.slice, ast.Name) and
                                        node.slice.id == self.index_var.id):
                                        
                                        # Replace with value_var
                                        return ast.Name(id=self.value_var.id, ctx=node.ctx)
                                    
                                    return node
                            
                            # Apply replacements in body
                            replacer = IndexReplacer(
                                collection, 
                                node.target, 
                                ast.Name(id=f"value_{node.target.id}", ctx=ast.Load())
                            )
                            new_body = copy.deepcopy(node.body)
                            for i, stmt in enumerate(new_body):
                                new_body[i] = replacer.visit(stmt)
                            
                            # Create new for node
                            new_node = ast.For(
                                target=new_target,
                                iter=new_iter,
                                body=new_body,
                                orelse=node.orelse
                            )
                            
                            # Add optimization to changes list
                            if not self.changes_made:
                                self.changes.append({
                                    'type': 'loop_optimization',
                                    'description': 'Converted range(len(x)) to more efficient enumerate(x)',
                                    'category': 'performance'
                                })
                                self.changes_made = True
                            
                            # Copy location for better error messages
                            return ast.copy_location(new_node, node)
                    
                    # Apply list comprehension transformation for simple list building
                    if (len(node.body) == 1 and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Call) and
                        isinstance(node.body[0].value.func, ast.Attribute) and
                        node.body[0].value.func.attr == 'append'):
                        
                        # Find or create initialization
                        # For now, we can only optimize code where we know the list variable
                        list_var = node.body[0].value.func.value
                        
                        # Get append value
                        if len(node.body[0].value.args) == 1:
                            append_value = node.body[0].value.args[0]
                            
                            # Create list comprehension node
                            list_comp = ast.ListComp(
                                elt=append_value,
                                generators=[
                                    ast.comprehension(
                                        target=node.target,
                                        iter=node.iter,
                                        ifs=[],
                                        is_async=0
                                    )
                                ]
                            )
                            
                            # Create assignment node
                            assign = ast.Assign(
                                targets=[list_var],
                                value=list_comp
                            )
                            
                            # Add optimization to changes list
                            if not self.changes_made:
                                self.changes.append({
                                    'type': 'list_comprehension',
                                    'description': 'Converted for loop to more efficient list comprehension',
                                    'category': 'performance'
                                })
                                self.changes_made = True
                            
                            # Copy location for better error messages
                            return ast.copy_location(assign, node)
                    
                    # Visit children for other optimizations
                    self.generic_visit(node)
                    return node
            
            # Apply loop optimizations
            optimizer = LoopOptimizer(self.changes)
            tree = optimizer.visit(tree)
            
        return tree
    
    def optimize_advanced(self, tree):
        """Apply advanced optimizations."""
        class ListComprehensionTransformer(ast.NodeTransformer):
            def __init__(self, changes):
                self.changes = changes
                self.changes_made = False
            
            def visit_For(self, node):
                # Check for list building pattern: result = []; for x in y: result.append(expr)
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Call) and 
                    isinstance(node.body[0].value.func, ast.Attribute) and 
                    node.body[0].value.func.attr == 'append'):
                    
                    # Get the list being built
                    target_list = node.body[0].value.func.value
                    
                    # Only optimize if it's a simple name (not a[b].c etc)
                    if isinstance(target_list, ast.Name):
                        list_name = target_list.id
                        
                        # Look for corresponding list initialization before this node
                        # This would require parent references, and just the name isn't enough
                        # For a complete implementation, we'd need more context about the initialization
                        
                        # Get the expression being appended
                        if len(node.body[0].value.args) == 1:
                            append_value = node.body[0].value.args[0]
                            
                            # Create list comprehension node
                            list_comp = ast.ListComp(
                                elt=append_value,
                                generators=[
                                    ast.comprehension(
                                        target=node.target,
                                        iter=node.iter,
                                        ifs=[],
                                        is_async=0
                                    )
                                ]
                            )
                            
                            # Add optimization to changes list if not already added
                            if not self.changes_made:
                                self.changes.append({
                                    'type': 'list_comprehension',
                                    'description': 'Converted loop with append to more efficient list comprehension',
                                    'category': 'performance'
                                })
                                self.changes_made = True
                            
                            # Create assignment node
                            assign = ast.Assign(
                                targets=[target_list],
                                value=list_comp
                            )
                            
                            # Copy location info to the new node
                            assign = ast.copy_location(assign, node)
                            
                            return assign
                
                # Visit children for other optimizations
                self.generic_visit(node)
                return node
            
            def visit_Assign(self, node):
                # Look for sorting-related assignments
                if (isinstance(node.value, ast.Call) and 
                    isinstance(node.value.func, ast.Name) and
                    node.value.func.id in ['sorted', 'sort']):
                    
                    # Add improvement for using built-in sorting
                    if not self.changes_made:
                        self.changes.append({
                            'type': 'sorting_optimization',
                            'description': 'Using Python built-in sorting for better performance',
                            'category': 'optimization'
                        })
                        self.changes_made = True
                
                # Visit child nodes
                self.generic_visit(node)
                return node
        
        # Apply advanced transformations
        transformer = ListComprehensionTransformer(self.changes)
        tree = transformer.visit(tree)
        
        # Apply map/filter transformer
        class MapFilterTransformer(ast.NodeTransformer):
            def __init__(self, changes):
                self.changes = changes
                self.changes_made = False
            
            def visit_Call(self, node):
                # Transform map() calls to list comprehensions
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == 'map' and 
                    len(node.args) >= 2):
                    
                    func = node.args[0]
                    iterable = node.args[1]
                    
                    # Handle lambda functions
                    if isinstance(func, ast.Lambda):
                        # Create list comprehension from lambda
                        if len(func.args.args) == 1:
                            var_name = func.args.args[0].arg
                            expr = func.body
                            
                            # Create list comprehension
                            list_comp = ast.ListComp(
                                elt=expr,
                                generators=[
                                    ast.comprehension(
                                        target=ast.Name(id=var_name, ctx=ast.Store()),
                                        iter=iterable,
                                        ifs=[],
                                        is_async=0
                                    )
                                ]
                            )
                            
                            # Add improvement
                            if not self.changes_made:
                                self.changes.append({
                                    'type': 'list_comprehension',
                                    'description': 'Converted map() with lambda to more readable list comprehension',
                                    'category': 'readability'
                                })
                                self.changes_made = True
                                
                            return list_comp
                    
                    # Handle simple function names
                    elif isinstance(func, ast.Name):
                        # Create list comprehension from function call
                        # Create temp variable name (this could be more robust)
                        var_name = 'item'
                        
                        # Create the function call on each item
                        call_expr = ast.Call(
                            func=func,
                            args=[ast.Name(id=var_name, ctx=ast.Load())],
                            keywords=[]
                        )
                        
                        # Create list comprehension
                        list_comp = ast.ListComp(
                            elt=call_expr,
                            generators=[
                                ast.comprehension(
                                    target=ast.Name(id=var_name, ctx=ast.Store()),
                                    iter=iterable,
                                    ifs=[],
                                    is_async=0
                                )
                            ]
                        )
                        
                        # Add improvement
                        if not self.changes_made:
                            self.changes.append({
                                'type': 'list_comprehension',
                                'description': 'Converted map() to more readable list comprehension',
                                'category': 'readability'
                            })
                            self.changes_made = True
                            
                        return list_comp
                
                # Transform filter() calls to list comprehensions
                elif (isinstance(node.func, ast.Name) and 
                      node.func.id == 'filter' and 
                      len(node.args) >= 2):
                    
                    func = node.args[0]
                    iterable = node.args[1]
                    
                    # Handle lambda functions
                    if isinstance(func, ast.Lambda):
                        # Create list comprehension from lambda
                        if len(func.args.args) == 1:
                            var_name = func.args.args[0].arg
                            condition = func.body
                            
                            # Create list comprehension
                            list_comp = ast.ListComp(
                                elt=ast.Name(id=var_name, ctx=ast.Load()),
                                generators=[
                                    ast.comprehension(
                                        target=ast.Name(id=var_name, ctx=ast.Store()),
                                        iter=iterable,
                                        ifs=[condition],
                                        is_async=0
                                    )
                                ]
                            )
                            
                            # Add improvement
                            if not self.changes_made:
                                self.changes.append({
                                    'type': 'list_comprehension',
                                    'description': 'Converted filter() with lambda to more readable list comprehension',
                                    'category': 'readability'
                                })
                                self.changes_made = True
                                
                            return list_comp
                    
                    # Handle simple function names
                    elif isinstance(func, ast.Name):
                        # Create list comprehension from function call
                        # Create temp variable name
                        var_name = 'item'
                        
                        # Create the function call for the condition
                        call_expr = ast.Call(
                            func=func,
                            args=[ast.Name(id=var_name, ctx=ast.Load())],
                            keywords=[]
                        )
                        
                        # Create list comprehension
                        list_comp = ast.ListComp(
                            elt=ast.Name(id=var_name, ctx=ast.Load()),
                            generators=[
                                ast.comprehension(
                                    target=ast.Name(id=var_name, ctx=ast.Store()),
                                    iter=iterable,
                                    ifs=[call_expr],
                                    is_async=0
                                )
                            ]
                        )
                        
                        # Add improvement
                        if not self.changes_made:
                            self.changes.append({
                                'type': 'list_comprehension',
                                'description': 'Converted filter() to more readable list comprehension',
                                'category': 'readability'
                            })
                            self.changes_made = True
                            
                        return list_comp
                
                # Visit children
                self.generic_visit(node)
                return node
        
        # Apply map/filter transformations
        map_filter = MapFilterTransformer(self.changes)
        tree = map_filter.visit(tree)
        
        return tree
    
    def remove_unused_variables(self, tree):
        """Remove unused variable declarations."""
        class UnusedVarRemover(ast.NodeTransformer):
            def __init__(self, used_names, changes):
                self.used_names = used_names
                self.changes = changes
                self.assigned_names = set()
                self.removed_vars = set()
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.assigned_names.add(node.id)
                return node
                
            def visit_Assign(self, node):
                self.generic_visit(node)
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    target = node.targets[0].id
                    if target not in self.used_names and target in self.assigned_names and target not in self.removed_vars:
                        self.changes.append({
                            'type': 'unused_variable_removal',
                            'description': f'Removed unused variable {target}',
                            'category': 'optimization'
                        })
                        self.removed_vars.add(target)
                        return None
                return node
        
        remover = UnusedVarRemover(self.used_names, self.changes)
        return remover.visit(tree)
    
    def remove_unreachable_code(self, tree):
        """Remove unreachable code."""
        if not self.config.apply_dead_code_elimination:
            return tree
            
        class UnreachableRemover(ast.NodeTransformer):
            def __init__(self, unreachable_nodes, changes):
                self.unreachable_nodes = unreachable_nodes
                self.changes = changes
                
            def visit(self, node):
                if node in self.unreachable_nodes:
                    self.changes.append({
                        'type': 'unreachable_code_removal',
                        'description': 'Removed unreachable code after return/break/continue',
                        'category': 'optimization'
                    })
                    return None
                return super().visit(node)
        
        remover = UnreachableRemover(self.unreachable_nodes, self.changes)
        return remover.visit(tree)
    
    def _calculate_complexity(self, tree):
        """Calculate the complexity of the code."""
        # Count nested loops to estimate complexity
        max_depth = 0
        current_depth = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif isinstance(node, ast.FunctionDef):
                # Reset depth for each function
                current_depth = 0
        
        # Map depth to complexity notation
        if max_depth == 0:
            return "O(1)"
        elif max_depth == 1:
            return "O(n)"
        elif max_depth == 2:
            return "O(n²)"
        elif max_depth == 3:
            return "O(n³)"
        else:
            return f"O(n^{max_depth})"
    
    def _generate_explanation(self, original_complexity, optimized_complexity):
        """Generate an explanation of the optimization."""
        # If complexity improved
        if original_complexity != optimized_complexity:
            # Extract the exponent from O(n^x) if present
            original_exp = re.search(r"O\(n\^?(\d+)?\)", original_complexity)
            optimized_exp = re.search(r"O\(n\^?(\d+)?\)", optimized_complexity)
            
            if original_exp and optimized_exp:
                original_n = original_exp.group(1) if original_exp.group(1) else "1"
                optimized_n = optimized_exp.group(1) if optimized_exp.group(1) else "1"
                
                if int(original_n) > int(optimized_n):
                    return f"Reduced algorithm complexity from {original_complexity} to {optimized_complexity}"
            
            # Handle other cases like O(2^n) -> O(n)
            if "2^n" in original_complexity and "n" in optimized_complexity:
                return f"Dramatically improved algorithm efficiency from {original_complexity} to {optimized_complexity}"
                
        # If specific optimizations were applied
        if self.changes:
            change_types = [change.get('type', '') if isinstance(change, dict) else change.type for change in self.changes]
            
            if 'unused_variable_removal' in change_types:
                return f"Removed unused variables and improved code clarity ({original_complexity})"
                
            if 'dead_code_elimination' in change_types:
                return f"Eliminated dead code branches for improved efficiency ({original_complexity})"
                
            if 'algorithm_replacement' in change_types:
                return f"Replaced inefficient algorithm implementation with an optimized version"
                
        return f"Applied optimizations while maintaining {original_complexity} complexity"
    
    def _add_complexity_documentation(self, code, original_complexity, optimized_complexity):
        """Add complexity documentation to the optimized code."""
        # Add a comment at the top of the file
        comment = f"# Optimized with Rule-based optimizer\n# Original complexity: {original_complexity}\n# Optimized complexity: {optimized_complexity}\n\n"
        return comment + code
    
    def _determine_main_improvement(self, original_code, optimized_code, original_complexity, optimized_complexity):
        """Determine the main improvement made by the optimization."""
        # If complexity improved, that's the main improvement
        if original_complexity != optimized_complexity and "O(1)" not in original_complexity:
            return f"Improved algorithm complexity from {original_complexity} to {optimized_complexity}"
        
        # Check if significant code size reduction
        original_lines = original_code.split('\n')
        optimized_lines = optimized_code.split('\n')
        
        # Fewer lines might indicate optimizations
        if len(optimized_lines) < len(original_lines):
            diff = len(original_lines) - len(optimized_lines)
            return f"Reduced code size by {diff} lines (approximately {int(diff/len(original_lines)*100)}%)"
            
        # If no specific improvement found, use a generic message
        return "Applied various optimizations to improve code quality and performance"
    
    def get_applied_rules(self):
        """Get a list of all optimization rules that were applied."""
        return self.changes

    def _detect_unreachable_code(self, tree):
        """Detect unreachable code in the AST."""
        class UnreachableDetector(ast.NodeVisitor):
            """Detects statements that are unreachable after return, break, or continue."""
            def __init__(self, changes):
                self.unreachable_nodes = set()
                self.changes = changes
                self.in_loop = 0  # Track nested loop depth
                
            def enter_loop(self):
                self.in_loop += 1
                
            def exit_loop(self):
                self.in_loop -= 1
            
            def visit_For(self, node):
                self.enter_loop()
                # Visit children first to identify unreachable nodes in the body
                for stmt in node.body:
                    self.visit(stmt)
                
                # Check if orelse has unreachable nodes
                for stmt in node.orelse:
                    self.visit(stmt)
                
                self.exit_loop()
            
            def visit_While(self, node):
                self.enter_loop()
                # Visit children first to identify unreachable nodes in the body
                for stmt in node.body:
                    self.visit(stmt)
                
                # Check if orelse has unreachable nodes
                for stmt in node.orelse:
                    self.visit(stmt)
                
                self.exit_loop()
            
            def visit_If(self, node):
                # Visit if body
                has_return_break = False
                has_return_continue = False
                
                for i, stmt in enumerate(node.body):
                    self.visit(stmt)
                    
                    # Check if this statement makes subsequent statements unreachable
                    if isinstance(stmt, ast.Return) or isinstance(stmt, ast.Raise):
                        has_return_break = True
                        # Mark all statements after this one as unreachable
                        for j in range(i + 1, len(node.body)):
                            self.unreachable_nodes.add(node.body[j])
                        break
                    elif isinstance(stmt, ast.Break):
                        has_return_break = True
                        # Mark all statements after this one as unreachable
                        for j in range(i + 1, len(node.body)):
                            self.unreachable_nodes.add(node.body[j])
                        break
                    elif isinstance(stmt, ast.Continue):
                        has_return_continue = True
                        # Mark all statements after this one as unreachable
                        for j in range(i + 1, len(node.body)):
                            self.unreachable_nodes.add(node.body[j])
                        break
                
                # If both if and else have return/break, statements after the if are unreachable
                if node.orelse:
                    has_else_return_break = False
                    
                    for i, stmt in enumerate(node.orelse):
                        self.visit(stmt)
                        
                        if isinstance(stmt, ast.Return) or isinstance(stmt, ast.Raise):
                            has_else_return_break = True
                            # Mark all statements after this one as unreachable
                            for j in range(i + 1, len(node.orelse)):
                                self.unreachable_nodes.add(node.orelse[j])
                            break
                        elif isinstance(stmt, ast.Break):
                            has_else_return_break = True
                            # Mark all statements after this one as unreachable
                            for j in range(i + 1, len(node.orelse)):
                                self.unreachable_nodes.add(node.orelse[j])
                            break
                        elif isinstance(stmt, ast.Continue):
                            # Mark all statements after this one as unreachable
                            for j in range(i + 1, len(node.orelse)):
                                self.unreachable_nodes.add(node.orelse[j])
                            break
                    
                    # If both branches terminate, code after is unreachable
                    return has_return_break and has_else_return_break
                
                return has_return_break
            
            def visit_Return(self, node):
                # No need to mark anything here - the parent will handle marking subsequent nodes
                pass
            
            def visit_Break(self, node):
                # Check if break is used in a loop
                if self.in_loop <= 0:
                    # This is an error: break outside loop
                    # We won't mark it as unreachable because that's a syntax error that should be caught
                    pass
            
            def visit_Continue(self, node):
                # Check if continue is used in a loop
                if self.in_loop <= 0:
                    # This is an error: continue outside loop
                    # We won't mark it as unreachable because that's a syntax error that should be caught
                    pass
            
            def visit_FunctionDef(self, node):
                # Reset unreachable detection for each function
                old_in_loop = self.in_loop
                self.in_loop = 0
                
                has_return = False
                # Visit each statement in the function body
                for i, stmt in enumerate(node.body):
                    # Skip docstring
                    if i == 0 and isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                        continue
                    
                    self.visit(stmt)
                    
                    # If we encounter a return or raise, subsequent statements are unreachable
                    if isinstance(stmt, ast.Return) or isinstance(stmt, ast.Raise):
                        has_return = True
                        # Mark all statements after this one as unreachable
                        for j in range(i + 1, len(node.body)):
                            self.unreachable_nodes.add(node.body[j])
                        break
                
                # Restore loop state
                self.in_loop = old_in_loop
                
                return has_return
        
        # First pass: identify unreachable nodes
        detector = UnreachableDetector(self.changes)
        detector.visit(tree)
        
        # Second pass: eliminate unreachable code
        eliminator = DeadCodeEliminator(detector.unreachable_nodes, self.changes)
        tree = eliminator.visit(tree)
        
        # Fix any missing location info
        ast.fix_missing_locations(tree)
        
        return tree

    def _eliminate_repeated_computations(self, tree):
        """Eliminate repeated computations by storing results in variables."""
        class RepeatedComputationEliminator(ast.NodeTransformer):
            def __init__(self, changes):
                self.changes = changes
                self.expressions = {}  # Maps expression string to (count, var_name)
                self.current_function = None
                self.next_var_id = 1
                self.changes_made = False
            
            def visit_FunctionDef(self, node):
                # Store the current function
                old_function = self.current_function
                self.current_function = node
                
                # Reset expressions for this function
                old_expressions = self.expressions
                self.expressions = {}
                
                # Process the function body
                self.generic_visit(node)
                
                # Insert new variables at the beginning of the function body (after docstring)
                new_assignments = []
                
                for expr_str, (count, var_name, expr_node) in self.expressions.items():
                    if count > 1:  # Only create temp vars for expressions used more than once
                        # Create a new assignment node
                        new_assignments.append(
                            ast.Assign(
                                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                                value=expr_node,
                                lineno=node.body[0].lineno if node.body else node.lineno,
                                col_offset=node.body[0].col_offset if node.body else node.col_offset
                            )
                        )
                
                # Insert after the docstring if present
                insert_pos = 0
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    insert_pos = 1
                
                node.body = node.body[:insert_pos] + new_assignments + node.body[insert_pos:]
                
                # Restore state
                self.expressions = old_expressions
                self.current_function = old_function
                
                return node
            
            def visit_Expr(self, node):
                """Skip docstrings for expression analysis."""
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    return node
                return self.generic_visit(node)
            
            def visit_Call(self, node):
                """Process function calls to identify repeated expensive computations."""
                self.generic_visit(node)
                
                # Skip simple calls or calls to builtins
                if isinstance(node.func, ast.Name) and node.func.id in {'len', 'print', 'str', 'int', 'float', 'bool'}:
                    return node
                
                # Try to get a string representation of the call
                try:
                    expr_str = ast.unparse(node)
                except (AttributeError, ValueError):
                    try:
                        expr_str = ast.dump(node)
                    except:
                        return node
                
                # Skip if this is already a variable reference
                if isinstance(node.func, ast.Name) and expr_str == node.func.id:
                    return node
                
                # Skip short expressions
                if len(expr_str) < 10:  # Arbitrary threshold to avoid creating vars for simple expressions
                    return node
                
                # Check if we've seen this expression before
                if expr_str in self.expressions:
                    count, var_name, _ = self.expressions[expr_str]
                    # Increment the count
                    self.expressions[expr_str] = (count + 1, var_name, node)
                    
                    # Replace with variable if this is a repeated expression
                    if count >= 1 and not self.changes_made:  # Only record the change once
                        self.changes.append({
                            'type': 'repeated_computation_elimination',
                            'description': f'Eliminated repeated computation of {expr_str}',
                            'category': 'performance'
                        })
                        self.changes_made = True
                    
                    # Replace with variable reference
                    return ast.Name(id=var_name, ctx=ast.Load())
                else:
                    # First time seeing this expression
                    temp_var = f"temp_var_{self.next_var_id}"
                    self.next_var_id += 1
                    self.expressions[expr_str] = (1, temp_var, node)
                    return node
                
            def visit_BinOp(self, node):
                """Process binary operations to identify repeated computations."""
                self.generic_visit(node)
                
                # Skip simple binary operations
                if isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name):
                    return node
                
                # Try to get a string representation of the operation
                try:
                    expr_str = ast.unparse(node)
                except (AttributeError, ValueError):
                    try:
                        expr_str = ast.dump(node)
                    except:
                        return node
                
                # Skip short expressions
                if len(expr_str) < 10:  # Arbitrary threshold to avoid creating vars for simple expressions
                    return node
                
                # Check if we've seen this expression before
                if expr_str in self.expressions:
                    count, var_name, _ = self.expressions[expr_str]
                    # Increment the count
                    self.expressions[expr_str] = (count + 1, var_name, node)
                    
                    # Replace with variable if this is a repeated expression
                    if count >= 1 and not self.changes_made:  # Only record the change once
                        self.changes.append({
                            'type': 'repeated_computation_elimination',
                            'description': f'Eliminated repeated computation of {expr_str}',
                            'category': 'performance'
                        })
                        self.changes_made = True
                    
                    # Replace with variable reference
                    return ast.Name(id=var_name, ctx=ast.Load())
                else:
                    # First time seeing this expression
                    temp_var = f"temp_var_{self.next_var_id}"
                    self.next_var_id += 1
                    self.expressions[expr_str] = (1, temp_var, node)
                    return node
        
        eliminator = RepeatedComputationEliminator(self.changes)
        tree = eliminator.visit(tree)
        
        # Fix any missing location info
        ast.fix_missing_locations(tree)
        
        return tree

    def _copy_locations_and_fix(self, new_node, original_node):
        """Utility function to copy location information and fix missing locations.
        
        This ensures all nodes have proper location information for error reporting.
        """
        ast.copy_location(new_node, original_node)
        
        # Recursively copy locations for child nodes if available
        if hasattr(new_node, 'value') and hasattr(original_node, 'value'):
            ast.copy_location(new_node.value, original_node.value)
            
            # Copy locations for function and arguments in function calls
            if isinstance(new_node.value, ast.Call) and isinstance(original_node.value, ast.Call):
                if hasattr(new_node.value, 'func') and hasattr(original_node.value, 'func'):
                    ast.copy_location(new_node.value.func, original_node.value.func)
        
        # For assignments, also copy locations for targets
        if hasattr(new_node, 'targets') and hasattr(original_node, 'targets'):
            for i, target in enumerate(new_node.targets):
                if i < len(original_node.targets):
                    ast.copy_location(target, original_node.targets[i])
        
        # Fix any remaining missing locations
        ast.fix_missing_locations(new_node)
        return new_node

    def _optimize_string_concatenation(self, tree):
        """Optimize string concatenation operations."""
        class StringConcatOptimizer(ast.NodeTransformer):
            def __init__(self, changes):
                self.changes = changes
                self.string_lists = {}  # Track potential string lists for join optimization
                
            def record_change(self, node, description):
                self.changes.append({
                    'type': 'string_concat_optimization',
                    'description': description,
                    'category': 'optimization',
                    'location': getattr(node, 'lineno', None)
                })
                
            def visit_Assign(self, node):
                """Track assignments that could be string lists for join operations."""
                self.generic_visit(node)
                
                # Track potential string lists for join operations
                return node

            def visit_For(self, node):
                old_in_loop = self.in_loop
                self.in_loop = True
                
                # Visit the body first
                node.body = [self.visit(item) for item in node.body if item is not None]
                node.body = [item for item in node.body if item is not None]
                
                # Check for unreachable code in the body
                found_exit_statement = False
                filtered_body = []
                for i, item in enumerate(node.body):
                    if found_exit_statement:
                        if isinstance(item, (ast.Return, ast.Raise)) or (isinstance(item, ast.Break) and self.in_loop) or (isinstance(item, ast.Continue) and self.in_loop):
                            self.record_change("Eliminated unreachable exit statement in loop body")
                        else:
                            self.record_change("Eliminated unreachable code after exit statement in loop body")
                    else:
                        filtered_body.append(item)
                        # Check if this statement causes an exit
                        detector = UnreachableDetector()
                        detector.in_loop = True
                        detector.visit(item)
                        if detector.always_exits:
                            found_exit_statement = True
                
                node.body = filtered_body
                
                # Visit the orelse block
                if node.orelse:
                    node.orelse = [self.visit(item) for item in node.orelse if item is not None]
                    node.orelse = [item for item in node.orelse if item is not None]
                
                self.in_loop = old_in_loop
                return node

            def visit_While(self, node):
                old_in_loop = self.in_loop
                self.in_loop = True
                
                # Check if condition is always False
                if isinstance(node.test, ast.Constant) and not node.test.value:
                    self.record_change("Eliminated loop with always-false condition")
                    # Keep only the else block if it exists
                    self.in_loop = old_in_loop
                    if node.orelse:
                        # Process the else block
                        result = [self.visit(item) for item in node.orelse if item is not None]
                        result = [item for item in result if item is not None]
                        self.in_loop = old_in_loop
                        if len(result) == 1:
                            return result[0]
                        else:
                            return ast.Expr(value=ast.Tuple(elts=[], ctx=ast.Load())) if not result else ast.If(
                                test=ast.Constant(value=True),
                                body=result,
                                orelse=[]
                            )
                    else:
                        self.in_loop = old_in_loop
                        # Return a pass statement for an empty loop
                        return ast.Pass()
                
                # Visit the body
                node.body = [self.visit(item) for item in node.body if item is not None]
                node.body = [item for item in node.body if item is not None]
                
                # Check for unreachable code in the body
                found_exit_statement = False
                filtered_body = []
                for i, item in enumerate(node.body):
                    if found_exit_statement:
                        if isinstance(item, (ast.Return, ast.Raise)) or (isinstance(item, ast.Break) and self.in_loop) or (isinstance(item, ast.Continue) and self.in_loop):
                            self.record_change("Eliminated unreachable exit statement in loop body")
                        else:
                            self.record_change("Eliminated unreachable code after exit statement in loop body")
                    else:
                        filtered_body.append(item)
                        # Check if this statement causes an exit
                        detector = UnreachableDetector()
                        detector.in_loop = self.in_loop
                        detector.visit(item)
                        if detector.always_exits:
                            found_exit_statement = True
                
                node.body = filtered_body
                
                # Visit the orelse block
                if node.orelse:
                    node.orelse = [self.visit(item) for item in node.orelse if item is not None]
                    node.orelse = [item for item in node.orelse if item is not None]
                
                self.in_loop = old_in_loop
                return node

            def visit_If(self, node):
                # Process the condition first
                node.test = self.visit(node.test)
                
                # Check if condition is a constant
                is_always_true = isinstance(node.test, ast.Constant) and bool(node.test.value)
                is_always_false = isinstance(node.test, ast.Constant) and not bool(node.test.value)
                
                if is_always_true:
                    # The else block is unreachable
                    self.record_change("Eliminated unreachable else block (condition is always True)")
                    
                    # Process and return only the then block
                    result = [self.visit(item) for item in node.body if item is not None]
                    result = [item for item in result if item is not None]
                    
                    if len(result) == 1:
                        return result[0]
                    elif not result:
                        return ast.Pass()
                    else:
                        # Return multiple statements wrapped in a new If with True condition
                        return ast.If(
                            test=ast.Constant(value=True),
                            body=result,
                            orelse=[]
                        )
                
                elif is_always_false:
                    # The then block is unreachable
                    self.record_change("Eliminated unreachable then block (condition is always False)")
                    
                    # Process and return only the else block
                    result = [self.visit(item) for item in node.orelse if item is not None]
                    result = [item for item in result if item is not None]
                    
                    if len(result) == 1:
                        return result[0]
                    elif not result:
                        return ast.Pass()
                    else:
                        # Return multiple statements wrapped in a new If with True condition
                        return ast.If(
                            test=ast.Constant(value=True),
                            body=result,
                            orelse=[]
                        )
                
                # Process both branches
                node.body = [self.visit(item) for item in node.body if item is not None]
                node.body = [item for item in node.body if item is not None]
                node.orelse = [self.visit(item) for item in node.orelse if item is not None]
                node.orelse = [item for item in node.orelse if item is not None]
                
                # Check for unreachable code in the then branch
                found_exit_statement = False
                filtered_body = []
                for i, item in enumerate(node.body):
                    if found_exit_statement:
                        if isinstance(item, (ast.Return, ast.Raise)) or (isinstance(item, ast.Break) and self.in_loop) or (isinstance(item, ast.Continue) and self.in_loop):
                            self.record_change("Eliminated unreachable exit statement in then branch")
                        else:
                            self.record_change("Eliminated unreachable code after exit statement in then branch")
                    else:
                        filtered_body.append(item)
                        # Check if this statement causes an exit
                        detector = UnreachableDetector()
                        detector.in_loop = self.in_loop
                        detector.visit(item)
                        if detector.always_exits:
                            found_exit_statement = True
                
                node.body = filtered_body
                
                # Check for unreachable code in the else branch
                found_exit_statement = False
                filtered_orelse = []
                for i, item in enumerate(node.orelse):
                    if found_exit_statement:
                        if isinstance(item, (ast.Return, ast.Raise)) or (isinstance(item, ast.Break) and self.in_loop) or (isinstance(item, ast.Continue) and self.in_loop):
                            self.record_change("Eliminated unreachable exit statement in else branch")
                        else:
                            self.record_change("Eliminated unreachable code after exit statement in else branch")
                    else:
                        filtered_orelse.append(item)
                        # Check if this statement causes an exit
                        detector = UnreachableDetector()
                        detector.in_loop = self.in_loop
                        detector.visit(item)
                        if detector.always_exits:
                            found_exit_statement = True
                
                node.orelse = filtered_orelse
                
                # If both branches are empty, eliminate the if statement
                if not node.body and not node.orelse:
                    self.record_change("Eliminated if statement with empty branches")
                    return ast.Pass()
                
                return node

            def visit_FunctionDef(self, node):
                # Process the function body
                node.body = [self.visit(item) for item in node.body if item is not None]
                node.body = [item for item in node.body if item is not None]
                
                # Check for unreachable code in the function body
                found_exit_statement = False
                filtered_body = []
                for i, item in enumerate(node.body):
                    if found_exit_statement:
                        if isinstance(item, (ast.Return, ast.Raise)):
                            self.record_change(f"Eliminated unreachable exit statement in function {node.name}")
                        else:
                            self.record_change(f"Eliminated unreachable code after return/raise in function {node.name}")
                    else:
                        filtered_body.append(item)
                        # Check if this statement causes an exit
                        detector = UnreachableDetector()
                        detector.visit(item)
                        if detector.always_exits:
                            found_exit_statement = True
                
                # Ensure there's at least one statement in the function body
                if not filtered_body:
                    filtered_body = [ast.Pass()]
                
                node.body = filtered_body
                return node

            def visit_Try(self, node):
                # Process the try block
                node.body = [self.visit(item) for item in node.body if item is not None]
                node.body = [item for item in node.body if item is not None]
                
                # Process the except handlers
                for handler in node.handlers:
                    handler.body = [self.visit(item) for item in handler.body if item is not None]
                    handler.body = [item for item in handler.body if item is not None]
                    
                    # Check for unreachable code in each except handler
                    found_exit_statement = False
                    filtered_body = []
                    for i, item in enumerate(handler.body):
                        if found_exit_statement:
                            if isinstance(item, (ast.Return, ast.Raise)) or (isinstance(item, ast.Break) and self.in_loop) or (isinstance(item, ast.Continue) and self.in_loop):
                                self.record_change("Eliminated unreachable exit statement in except handler")
                            else:
                                self.record_change("Eliminated unreachable code after exit statement in except handler")
                        else:
                            filtered_body.append(item)
                            # Check if this statement causes an exit
                            detector = UnreachableDetector()
                            detector.in_loop = self.in_loop
                            detector.visit(item)
                            if detector.always_exits:
                                found_exit_statement = True
                    
                    # Ensure there's at least one statement in the handler body
                    if not filtered_body:
                        filtered_body = [ast.Pass()]
                    
                    handler.body = filtered_body
                
                # Process the else block
                if node.orelse:
                    node.orelse = [self.visit(item) for item in node.orelse if item is not None]
                    node.orelse = [item for item in node.orelse if item is not None]
                    
                    # Check for unreachable code in the else block
                    found_exit_statement = False
                    filtered_orelse = []
                    for i, item in enumerate(node.orelse):
                        if found_exit_statement:
                            if isinstance(item, (ast.Return, ast.Raise)) or (isinstance(item, ast.Break) and self.in_loop) or (isinstance(item, ast.Continue) and self.in_loop):
                                self.record_change("Eliminated unreachable exit statement in try-else block")
                            else:
                                self.record_change("Eliminated unreachable code after exit statement in try-else block")
                        else:
                            filtered_orelse.append(item)
                            # Check if this statement causes an exit
                            detector = UnreachableDetector()
                            detector.in_loop = self.in_loop
                            detector.visit(item)
                            if detector.always_exits:
                                found_exit_statement = True
                    
                    node.orelse = filtered_orelse
                
                # Process the finally block
                if node.finalbody:
                    node.finalbody = [self.visit(item) for item in node.finalbody if item is not None]
                    node.finalbody = [item for item in node.finalbody if item is not None]
                    
                    # Check for unreachable code in the finally block
                    found_exit_statement = False
                    filtered_finalbody = []
                    for i, item in enumerate(node.finalbody):
                        if found_exit_statement:
                            if isinstance(item, (ast.Return, ast.Raise)) or (isinstance(item, ast.Break) and self.in_loop) or (isinstance(item, ast.Continue) and self.in_loop):
                                self.record_change("Eliminated unreachable exit statement in finally block")
                            else:
                                self.record_change("Eliminated unreachable code after exit statement in finally block")
                        else:
                            filtered_finalbody.append(item)
                            # Check if this statement causes an exit
                            detector = UnreachableDetector()
                            detector.in_loop = self.in_loop
                            detector.visit(item)
                            if detector.always_exits:
                                found_exit_statement = True
                    
                    node.finalbody = filtered_finalbody
                
                return node

            def visit_Module(self, node):
                node.body = [self.visit(item) for item in node.body if item is not None]
                node.body = [item for item in node.body if item is not None]
                return node

        # Apply dead code elimination
        eliminator = DeadCodeEliminator(self.changes)
        tree = eliminator.visit(tree)
        
        # Fix any missing location info
        ast.fix_missing_locations(tree)
        
        return tree 

class NestedLoopOptimizer(ast.NodeTransformer):
    """Optimizes nested loops for better performance."""
    
    def __init__(self, changes):
        self.changes = changes
        
    def record_change(self, node, description):
        self.changes.append({
            'type': 'nested_loop_optimization',
            'description': description,
            'category': 'optimization',
            'location': getattr(node, 'lineno', None)
        })
    
    def visit_FunctionDef(self, node):
        """Visit function definitions to optimize their nested loops."""
        self.generic_visit(node)
        
        # Find all nested loops and analyze computation patterns
        nested_loops = self._find_nested_loops(node)
        for outer_loop, inner_loop in nested_loops:
            # Check if we can extract invariant computations
            self._extract_invariant_computations(outer_loop, inner_loop)
            
            # Check if we can combine loops
            combined = self._try_combine_loops(outer_loop, inner_loop)
            if combined:
                self.record_change(outer_loop, "Combined nested loops")
        
        return node
    
    def _find_nested_loops(self, node):
        """Find all nested loops in the given node."""
        nested_loops = []
        
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.For):
                self._find_inner_loops(stmt, nested_loops)
        
        return nested_loops
    
    def _find_inner_loops(self, loop, results, parent=None):
        """Recursively find inner loops within the given loop."""
        for stmt in loop.body:
            if isinstance(stmt, ast.For):
                results.append((loop, stmt))
                # Continue searching for deeper nesting
                self._find_inner_loops(stmt, results, loop)
    
    def _extract_invariant_computations(self, outer_loop, inner_loop):
        """Extract computations that are invariant in the inner loop but needed in the outer loop."""
        invariant_exprs = self._find_invariant_expressions(outer_loop, inner_loop)
        if invariant_exprs:
            # Create assignments for invariant expressions before the inner loop
            for expr, name in invariant_exprs.items():
                assign = ast.Assign(
                    targets=[ast.Name(id=name, ctx=ast.Store())],
                    value=expr
                )
                
                # Find the position of the inner loop and insert before it
                for i, stmt in enumerate(outer_loop.body):
                    if stmt == inner_loop:
                        outer_loop.body.insert(i, assign)
                        break
                
                # Replace expressions in inner loop with the new variables
                class ExpressionReplacer(ast.NodeTransformer):
                    def visit(self, node):
                        if ast.unparse(node) == ast.unparse(expr):
                            return ast.Name(id=name, ctx=ast.Load())
                        return super().visit(node)
                
                replacer = ExpressionReplacer()
                for i, stmt in enumerate(inner_loop.body):
                    inner_loop.body[i] = replacer.visit(stmt)
                
                self.record_change(inner_loop, f"Extracted invariant computation to {name}")
    
    def _find_invariant_expressions(self, outer_loop, inner_loop):
        """Find expressions that are invariant in the inner loop."""
        invariant_exprs = {}
        
        # Collect variables that change in the inner loop
        inner_vars = set()
        
        class VarCollector(ast.NodeVisitor):
            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        inner_vars.add(target.id)
                self.generic_visit(node)
                
            def visit_AugAssign(self, node):
                if isinstance(node.target, ast.Name):
                    inner_vars.add(node.target.id)
                self.generic_visit(node)
        
        collector = VarCollector()
        collector.visit(inner_loop)
        
        # Find expressions that don't use inner loop variables
        class InvariantFinder(ast.NodeVisitor):
            def __init__(self, inner_vars, outer_var):
                self.inner_vars = inner_vars
                self.outer_var = outer_var
                self.invariants = {}
                self.count = 0
                
            def visit_Call(self, node):
                # Check if this is a potentially expensive call that doesn't depend on inner loop vars
                vars_used = set()
                self._collect_vars(node, vars_used)
                
                if not any(var in self.inner_vars for var in vars_used) and self.outer_var in vars_used:
                    expr_str = ast.unparse(node)
                    if expr_str not in self.invariants:
                        self.invariants[node] = f"invariant_{self.count}"
                        self.count += 1
                
                self.generic_visit(node)
                
            def visit_BinOp(self, node):
                # Check for expensive binary operations
                vars_used = set()
                self._collect_vars(node, vars_used)
                
                if not any(var in self.inner_vars for var in vars_used) and self.outer_var in vars_used:
                    expr_str = ast.unparse(node)
                    if expr_str not in self.invariants:
                        self.invariants[node] = f"invariant_{self.count}"
                        self.count += 1
                
                self.generic_visit(node)
            
            def _collect_vars(self, node, vars_used):
                """Collect all variable names used in an expression."""
                if isinstance(node, ast.Name):
                    vars_used.add(node.id)
                elif hasattr(node, 'iter') and hasattr(node.iter, 'id'):
                    vars_used.add(node.iter.id)
                
                for child in ast.iter_child_nodes(node):
                    self._collect_vars(child, vars_used)
        
        # Get the iterator variable from the outer loop
        outer_var = None
        if isinstance(outer_loop.target, ast.Name):
            outer_var = outer_loop.target.id
        
        if outer_var:
            finder = InvariantFinder(inner_vars, outer_var)
            finder.visit(inner_loop)
            return finder.invariants
        
        return {}
    
    def _try_combine_loops(self, outer_loop, inner_loop):
        """Try to combine nested loops if possible."""
        # Check if both loops iterate over ranges
        if (not self._is_range_loop(outer_loop) or 
            not self._is_range_loop(inner_loop) or
            len(outer_loop.body) > 1):  # Only inner loop should be in outer loop body
            return False
        
        # Check if inner loop makes a simple computation that can be vectorized
        if not self._is_simple_computation(inner_loop):
            return False
        
        # TODO: Implement actual loop combination logic
        # This is a complex transformation requiring careful analysis
        # of dependencies and would need more implementation
        
        return False
    
    def _is_range_loop(self, loop):
        """Check if a loop iterates over a range."""
        return (isinstance(loop.iter, ast.Call) and
                isinstance(loop.iter.func, ast.Name) and
                loop.iter.func.id == 'range')
    
    def _is_simple_computation(self, loop):
        """Check if a loop performs a simple computation that can be vectorized."""
        # Simple append pattern
        if (len(loop.body) == 1 and
            isinstance(loop.body[0], ast.Expr) and
            isinstance(loop.body[0].value, ast.Call) and
            isinstance(loop.body[0].value.func, ast.Attribute) and
            loop.body[0].value.func.attr == 'append'):
            return True
        
        # Simple assignment pattern
        if (len(loop.body) == 1 and
            isinstance(loop.body[0], ast.Assign) and
            isinstance(loop.body[0].targets[0], ast.Subscript)):
            return True
        
        return False

    def _optimize_code(self, tree):
        """Apply all optimizations to the AST."""
        # Apply in order of potential impact
        tree = self._fold_constants(tree)
        tree = self._eliminate_dead_code(tree)
        tree = self._remove_unused_variables(tree)
        tree = self._optimize_loops(tree)
        tree = self._eliminate_repeated_computations(tree)
        
        # Apply additional optimizations
        string_optimizer = StringJoinOptimizer(self.changes)
        tree = string_optimizer.visit(tree)
        
        optimizer = NestedLoopOptimizer(self.changes)
        tree = optimizer.visit(tree)
        
        # Algorithm detection should be last as it might replace entire functions
        tree = self._detect_algorithms(tree)
        
        return tree

class StringJoinOptimizer(ast.NodeTransformer):
    """Optimizes string concatenation operations by replacing them with more efficient join patterns."""
    
    def __init__(self, changes):
        self.changes = changes
        # Track string accumulation patterns
        self.string_accumulation = {}
    
    def record_change(self, node, description):
        """Record a change made during optimization."""
        self.changes.append({
            'type': 'string_optimization',
            'description': description,
            'category': 'optimization',
            'location': getattr(node, 'lineno', None)
        })
    
    def visit_FunctionDef(self, node):
        """Process function definitions and look for string concatenation patterns."""
        self.string_accumulation.clear()  # Reset for each function
        
        # First pass: identify string accumulation patterns
        self._identify_accumulation_patterns(node)
        
        # Second pass: replace with optimized join operations
        modified_node = self.generic_visit(node)
        
        return modified_node
    
    def _identify_accumulation_patterns(self, node):
        """Identify string accumulation patterns in the code."""
        for i, stmt in enumerate(node.body):
            # Look for string initialization
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                target = stmt.targets[0]
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Check for empty string initialization
                    if (isinstance(stmt.value, ast.Constant) and 
                        isinstance(stmt.value.value, str) and 
                        stmt.value.value == ""):
                        self.string_accumulation[var_name] = {
                            'init_pos': i,
                            'is_accumulation': False,
                            'append_positions': [],
                            'strings': []
                        }
        
        # Find append operations
        for i, stmt in enumerate(node.body):
            # Look for string concatenation with +=
            if isinstance(stmt, ast.AugAssign) and isinstance(stmt.op, ast.Add):
                target = stmt.target
                if isinstance(target, ast.Name) and target.id in self.string_accumulation:
                    var_info = self.string_accumulation[target.id]
                    var_info['is_accumulation'] = True
                    var_info['append_positions'].append(i)
                    
                    # Try to extract the string if it's a constant
                    if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                        var_info['strings'].append(stmt.value.value)
                    else:
                        var_info['strings'].append(None)  # Non-constant value
            
            # Look for reassignment with +
            elif isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                target = stmt.targets[0]
                if isinstance(target, ast.Name) and target.id in self.string_accumulation:
                    if isinstance(stmt.value, ast.BinOp) and isinstance(stmt.value.op, ast.Add):
                        left = stmt.value.left
                        right = stmt.value.right
                        
                        # Check if left side is the same variable
                        if isinstance(left, ast.Name) and left.id == target.id:
                            var_info = self.string_accumulation[target.id]
                            var_info['is_accumulation'] = True
                            var_info['append_positions'].append(i)
                            
                            # Try to extract the string if it's a constant
                            if isinstance(right, ast.Constant) and isinstance(right.value, str):
                                var_info['strings'].append(right.value)
                            else:
                                var_info['strings'].append(None)  # Non-constant value
    
    def visit_Assign(self, node):
        """Check assignments for string concatenation patterns that can be optimized."""
        self.generic_visit(node)
        
        # Look for multiple concatenations in a single assignment
        if isinstance(node.value, ast.BinOp):
            string_parts = []
            if self._collect_string_parts(node.value, string_parts):
                # If we have multiple string concatenations, replace with join
                if len(string_parts) > 2:  # Only worth optimizing if more than two strings
                    joined = ast.Call(
                        func=ast.Attribute(
                            value=ast.Constant(value=""),
                            attr='join',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.List(
                                elts=[],
                                ctx=ast.Load()
                            )
                        ],
                        keywords=[]
                    )
                else:
                    joined = node.value
                
                # Replace the original assignment with the optimized join operation
                new_assign = ast.Assign(
                    targets=[node.targets[0]],
                    value=joined
                )
                
                # Copy location information
                ast.copy_location(new_assign, node)
                
                return new_assign
        
        return node

class DeadCodeEliminator(ast.NodeTransformer):
    """Eliminates unreachable code nodes identified by UnreachableDetector."""
    
    def __init__(self, unreachable_nodes, changes):
        self.unreachable_nodes = unreachable_nodes
        self.changes = changes
        self.changes_made = False
    
    def visit(self, node):
        # Skip unreachable nodes
        if node in self.unreachable_nodes:
            if not self.changes_made:
                self.changes.append({
                    'type': 'dead_code_elimination',
                    'description': 'Eliminated unreachable code',
                    'category': 'performance'
                })
                self.changes_made = True
            return None
        
        # Continue normal traversal for reachable nodes
        return super().visit(node)

    def _eliminate_repeated_computations(self, tree):
        """Eliminate repeated computations by storing results in variables."""
        class RepeatedComputationEliminator(ast.NodeTransformer):
            def __init__(self, changes):
                self.changes = changes
                self.expressions = {}  # Maps expression string to (count, var_name)
                self.current_function = None
                self.next_var_id = 1
                self.changes_made = False
            
            def visit_FunctionDef(self, node):
                # Store the current function
                old_function = self.current_function
                self.current_function = node
                
                # Reset expressions for this function
                old_expressions = self.expressions
                self.expressions = {}
                
                # Process the function body
                self.generic_visit(node)
                
                # Insert new variables at the beginning of the function body (after docstring)
                new_assignments = []
                
                for expr_str, (count, var_name, expr_node) in self.expressions.items():
                    if count > 1:  # Only create temp vars for expressions used more than once
                        # Create a new assignment node
                        new_assignments.append(
                            ast.Assign(
                                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                                value=expr_node,
                                lineno=node.body[0].lineno if node.body else node.lineno,
                                col_offset=node.body[0].col_offset if node.body else node.col_offset
                            )
                        )
                
                # Insert after the docstring if present
                insert_pos = 0
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    insert_pos = 1
                
                node.body = node.body[:insert_pos] + new_assignments + node.body[insert_pos:]
                
                # Restore state
                self.expressions = old_expressions
                self.current_function = old_function
                
                return node
            
            def visit_Expr(self, node):
                """Skip docstrings for expression analysis."""
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    return node
                return self.generic_visit(node)
            
            def visit_Call(self, node):
                """Process function calls to identify repeated expensive computations."""
                self.generic_visit(node)
                
                # Skip simple calls or calls to builtins
                if isinstance(node.func, ast.Name) and node.func.id in {'len', 'print', 'str', 'int', 'float', 'bool'}:
                    return node
                
                # Try to get a string representation of the call
                try:
                    expr_str = ast.unparse(node)
                except (AttributeError, ValueError):
                    try:
                        expr_str = ast.dump(node)
                    except:
                        return node
                
                # Skip if this is already a variable reference
                if isinstance(node.func, ast.Name) and expr_str == node.func.id:
                    return node
                
                # Skip short expressions
                if len(expr_str) < 10:  # Arbitrary threshold to avoid creating vars for simple expressions
                    return node
                
                # Check if we've seen this expression before
                if expr_str in self.expressions:
                    count, var_name, _ = self.expressions[expr_str]
                    # Increment the count
                    self.expressions[expr_str] = (count + 1, var_name, node)
                    
                    # Replace with variable if this is a repeated expression
                    if count >= 1 and not self.changes_made:  # Only record the change once
                        self.changes.append({
                            'type': 'repeated_computation_elimination',
                            'description': f'Eliminated repeated computation of {expr_str}',
                            'category': 'performance'
                        })
                        self.changes_made = True
                    
                    # Replace with variable reference
                    return ast.Name(id=var_name, ctx=ast.Load())
                else:
                    # First time seeing this expression
                    temp_var = f"temp_var_{self.next_var_id}"
                    self.next_var_id += 1
                    self.expressions[expr_str] = (1, temp_var, node)
                    return node
                
            def visit_BinOp(self, node):
                """Process binary operations to identify repeated computations."""
                self.generic_visit(node)
                
                # Skip simple binary operations
                if isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name):
                    return node
                
                # Try to get a string representation of the operation
                try:
                    expr_str = ast.unparse(node)
                except (AttributeError, ValueError):
                    try:
                        expr_str = ast.dump(node)
                    except:
                        return node
                
                # Skip short expressions
                if len(expr_str) < 10:  # Arbitrary threshold to avoid creating vars for simple expressions
                    return node
                
                # Check if we've seen this expression before
                if expr_str in self.expressions:
                    count, var_name, _ = self.expressions[expr_str]
                    # Increment the count
                    self.expressions[expr_str] = (count + 1, var_name, node)
                    
                    # Replace with variable if this is a repeated expression
                    if count >= 1 and not self.changes_made:  # Only record the change once
                        self.changes.append({
                            'type': 'repeated_computation_elimination',
                            'description': f'Eliminated repeated computation of {expr_str}',
                            'category': 'performance'
                        })
                        self.changes_made = True
                    
                    # Replace with variable reference
                    return ast.Name(id=var_name, ctx=ast.Load())
                else:
                    # First time seeing this expression
                    temp_var = f"temp_var_{self.next_var_id}"
                    self.next_var_id += 1
                    self.expressions[expr_str] = (1, temp_var, node)
                    return node
        
        eliminator = RepeatedComputationEliminator(self.changes)
        tree = eliminator.visit(tree)
        
        # Fix any missing location info
        ast.fix_missing_locations(tree)
        
        return tree
