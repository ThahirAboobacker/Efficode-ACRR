"""
EFFICODE-ACRR Rule-Based Code Optimizer

This module provides rule-based code optimization for Python code through 
AST (Abstract Syntax Tree) analysis and transformation. It detects common
inefficient patterns and applies optimizations.

Usage:
    from rule_based import optimize_code
    
    optimized_code, patterns, stats = optimize_code(my_python_code)
"""
"""
Rule-Based Optimization Module for EFFICODE-ACRR

This module implements rule-based code optimization techniques for Python code:
- Detection of inefficient patterns in algorithms and data structures
- AST-based code transformation
- Loop optimizations and memory usage improvements
- Data structure optimizations
"""


import ast
import sys
import logging
import copy
import re
from typing import Dict, List, Tuple, Set, Optional, Union, Any


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)




###########################################
# PART 1: Base Classes and Utilities
###########################################

def parse_python_code(code: str) -> Optional[ast.AST]:
    """
    Parse Python code into an AST
    
    Args:
        code: Python code string
        
    Returns:
        AST if parsing succeeds, None otherwise
    """
    try:
        return ast.parse(code)
    except SyntaxError as e:
        logger.error(f"Syntax error parsing code: {str(e)}")
        return None

def detect_algorithm_type(code: str) -> str:
    """
    Simple algorithm type detection based on patterns in code
    
    Args:
        code: Python code string
        
    Returns:
        String representing the detected algorithm type
    """
    tree = parse_python_code(code)
    if not tree:
        return "unknown"
        
    # Count elements
    counts = count_code_elements(tree)
    
    # Check for sorting algorithms
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name.lower()
            if 'sort' in func_name:
                nested_loops = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)):
                        nested_loops += 1
                        
                if nested_loops >= 2:
                    if 'bubble' in func_name:
                        return 'bubble_sort'
                    elif 'quick' in func_name:
                        return 'quick_sort'
                    elif 'merge' in func_name:
                        return 'merge_sort'
                    else:
                        return 'sorting_algorithm'
            
            # Check for search algorithms
            elif 'search' in func_name:
                if counts['for_loops'] == 1:
                    return 'linear_search'
                elif 'binary' in func_name:
                    return 'binary_search'
                else:
                    return 'search_algorithm'
                    
    # Check for data structure patterns
    if counts['functions'] == 1 and 'unique' in [n.name.lower() for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        return 'unique_values_algorithm'
        
    return "unknown"

def count_code_elements(tree: ast.AST) -> Dict[str, int]:
    """
    Count various code elements in the AST
    
    Args:
        tree: AST to analyze
        
    Returns:
        Dictionary with counts of different code elements
    """
    counts = {
        'for_loops': 0,
        'while_loops': 0,
        'if_statements': 0,
        'functions': 0,
        'classes': 0,
        'assignments': 0,
        'comparisons': 0,
        'calls': 0,
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            counts['for_loops'] += 1
        elif isinstance(node, ast.While):
            counts['while_loops'] += 1
        elif isinstance(node, ast.If):
            counts['if_statements'] += 1
        elif isinstance(node, ast.FunctionDef):
            counts['functions'] += 1
        elif isinstance(node, ast.ClassDef):
            counts['classes'] += 1
        elif isinstance(node, ast.Assign):
            counts['assignments'] += 1
        elif isinstance(node, ast.Compare):
            counts['comparisons'] += 1
        elif isinstance(node, ast.Call):
            counts['calls'] += 1
            
    return counts

class PatternDetector:
    """Base class for detecting inefficient code patterns"""
    
    def detect(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect inefficient patterns in code
        
        Args:
            code: Python code as string
            
        Returns:
            List of detected patterns with metadata
        """
        tree = parse_python_code(code)
        if not tree:
            return []
        
        try:
            patterns = self._detect_in_ast(tree)
            for pattern in patterns:
                if 'algorithm_type' not in pattern:
                    pattern['algorithm_type'] = detect_algorithm_type(code)
            return patterns
        except Exception as e:
            logger.error(f"Error in pattern detection ({self.__class__.__name__}): {str(e)}")
            return []
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Detect patterns in AST (to be implemented by subclasses)
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        raise NotImplementedError("Subclasses must implement _detect_in_ast")


class CodeTransformer:
    """Base class for code transformation"""
    
    def _ast_to_code(self, tree: ast.AST) -> str:
        """Convert AST back to code"""
        try:
            # Try using ast.unparse first (Python 3.9+)
            if hasattr(ast, 'unparse'):
                return ast.unparse(tree)
            
            # Fall back to astor
            try:
                import astor
                return astor.to_source(tree)
            except ImportError:
                logger.error("No AST to code converter available")
                return ""
        except Exception as e:
            logger.error(f"Error converting AST to code: {str(e)}")
            return ""
    
    def _fix_syntax(self, code: str) -> str:
        """Fix common syntax issues in generated code"""
        import re
        
        # Fix missing parentheses in function calls
        code = re.sub(r'(\b\w+)(\b\w+)', r'\1(\2)', code)
        
        # Fix function definitions without parentheses
        code = re.sub(r'def\s+(\w+)([a-zA-Z0-9_]+):', r'def \1(\2):', code)
        
        # Fix missing parentheses in len() calls
        code = re.sub(r'len(\w+)', r'len(\1)', code)
        
        # Fix missing parentheses in append() calls
        code = re.sub(r'(\w+)\.append(\w+)', r'\1.append(\2)', code)
        
        # Fix missing parentheses in range() calls
        code = re.sub(r'range(\w+)', r'range(\1)', code)
        
        # Fix missing parentheses in print() calls
        code = re.sub(r'print(\w+)', r'print(\1)', code)
        
        return code
    
    def transform(self, code: str) -> str:
        """
        Transform code to optimize it
        
        Args:
            code: Python code as string
            
        Returns:
            Optimized code as string
        """
        tree = parse_python_code(code)
        if not tree:
            return code
        
        try:
            transformed_tree = self._transform_ast(tree)
            result_code = self._ast_to_code(transformed_tree)
            
            # Fix common syntax issues
            result_code = self._fix_syntax(result_code)
            
            # Validate the generated code
            if result_code and parse_python_code(result_code):
                return result_code
            else:
                logger.error("Generated invalid code, returning original")
                return code
        except Exception as e:
            logger.error(f"Error in code transformation: {str(e)}")
            return code
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Transform the AST (to be implemented by subclasses)
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        raise NotImplementedError("Subclasses must implement _transform_ast")
                
class ASTNodeVisitor:
    """Helper class for adding parent references to AST nodes"""
    
    @staticmethod
    def add_parent_info(node: ast.AST) -> ast.AST:
        """
        Add parent references to AST nodes
        
        Args:
            node: Root AST node
            
        Returns:
            AST with parent references
        """
        parent_map = {}
        
        def _visit_node(current, parent=None):
            if parent is not None:
                parent_map[current] = parent
            for child in ast.iter_child_nodes(current):
                _visit_node(child, current)
        
        _visit_node(node)
        
        # Set parent attributes now that we have the complete map
        for child, parent in parent_map.items():
            setattr(child, 'parent', parent)
            
        return node

class RuleUtils:
    """Utility functions for rule-based transformations"""
    
    @staticmethod
    def is_node_in_module(node: ast.AST) -> bool:
        """
        Check if node is directly in module body
        
        Args:
            node: AST node
            
        Returns:
            True if node is in module body
        """
        return isinstance(getattr(node, 'parent', None), ast.Module)
    
    @staticmethod
    def is_function_with_name(node: ast.AST, name: str) -> bool:
        """
        Check if node is a function with the given name
        
        Args:
            node: AST node
            name: Function name to check
            
        Returns:
            True if node is a function with given name
        """
        return isinstance(node, ast.FunctionDef) and node.name == name
    
    @staticmethod
    def is_same_variable(node1: ast.AST, node2: ast.AST) -> bool:
        """
        Check if two name nodes refer to the same variable
        
        Args:
            node1: First AST node
            node2: Second AST node
            
        Returns:
            True if both nodes are the same variable
        """
        return (isinstance(node1, ast.Name) and 
                isinstance(node2, ast.Name) and 
                node1.id == node2.id)
    
    @staticmethod
    def is_literal_true(node: ast.AST) -> bool:
        """
        Check if node is the literal True
        
        Args:
            node: AST node
            
        Returns:
            True if node is True literal
        """
        if hasattr(ast, 'NameConstant'):  # Python 3.7 and earlier
            return isinstance(node, ast.NameConstant) and node.value is True
        # Python 3.8+ uses Constant
        return isinstance(node, ast.Constant) and node.value is True
    
    @staticmethod
    def is_literal_false(node: ast.AST) -> bool:
        """
        Check if node is the literal False
        
        Args:
            node: AST node
            
        Returns:
            True if node is False literal
        """
        if hasattr(ast, 'NameConstant'):  # Python 3.7 and earlier
            return isinstance(node, ast.NameConstant) and node.value is False
        # Python 3.8+ uses Constant
        return isinstance(node, ast.Constant) and node.value is False
    
    @staticmethod
    def is_empty_list(node: ast.AST) -> bool:
        """
        Check if node is an empty list literal []
        
        Args:
            node: AST node
            
        Returns:
            True if node is an empty list
        """
        return isinstance(node, ast.List) and len(node.elts) == 0
    
    @staticmethod
    def is_append_call(node: ast.AST, target_name: str) -> bool:
        """
        Check if node is an append call on the target
        
        Args:
            node: AST node
            target_name: Name of target variable
            
        Returns:
            True if node is append call on target
        """
        if not isinstance(node, ast.Call):
            return False
        
        if not isinstance(node.func, ast.Attribute):
            return False
        
        return (node.func.attr == 'append' and 
                isinstance(node.func.value, ast.Name) and 
                node.func.value.id == target_name)
    
    @staticmethod
    def find_assignment_target(node: ast.AST) -> Optional[str]:
        """
        Extract the target name from an assignment node
        
        Args:
            node: AST node
            
        Returns:
            Target variable name or None
        """
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                return target.id
        return None
    
    @staticmethod
    def is_constant_node(node: ast.AST) -> bool:
        """
        Check if node is a constant (handles Python version differences)
        
        Args:
            node: AST node to check
            
        Returns:
            True if node is a constant
        """
        if hasattr(ast, 'Constant'):  # Python 3.8+
            return isinstance(node, ast.Constant)
        else:  # Python 3.7 and earlier
            return (isinstance(node, (ast.Num, ast.Str, ast.Bytes, ast.NameConstant, ast.Ellipsis)))
    
    @staticmethod
    def get_constant_value(node: ast.AST) -> Any:
        """
        Get the value of a constant node (handles Python version differences)
        
        Args:
            node: AST constant node
            
        Returns:
            The constant value
        """
        if hasattr(ast, 'Constant') and isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        # Python 3.7 and earlier
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Bytes):
            return node.s
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.Ellipsis):
            return ...
        return None
    
    @staticmethod
    def create_constant_node(value: Any) -> ast.AST:
        """
        Create a constant node (handles Python version differences)
        
        Args:
            value: The constant value
            
        Returns:
            AST constant node
        """
        if hasattr(ast, 'Constant'):  # Python 3.8+
            return ast.Constant(value=value, kind=None)
        
        # Python 3.7 and earlier
        if isinstance(value, (int, float, complex)):
            return ast.Num(n=value)
        elif isinstance(value, str):
            return ast.Str(s=value)
        elif isinstance(value, bytes):
            return ast.Bytes(s=value)
        elif value is None or isinstance(value, bool):
            return ast.NameConstant(value=value)
        elif value is Ellipsis:
            return ast.Ellipsis()
        
        # Default fallback
        logger.warning(f"Could not create constant node for {value}, using None")
        return ast.NameConstant(value=None) if not hasattr(ast, 'Constant') else ast.Constant(value=None, kind=None)
    
###########################################
# PART 2: Pattern Detectors for Optimizations
###########################################

class UnusedVariableDetector(PatternDetector):
    """Detects unused variable assignments"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find unused variable assignments with proper scope handling
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Add parent references
        ASTNodeVisitor.add_parent_info(tree)
        
        # Process each scope separately
        self._process_scope(tree, patterns)
        
        return patterns
    
    def _process_scope(self, node, patterns):
        """
        Process a single scope (module, function, class)
        
        Args:
            node: AST node representing a scope
            patterns: List to collect patterns
        """
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            # Track variables defined and used in this scope
            defined_vars = {}  # var_name -> list of nodes
            used_vars = set()
            
            # Process all statements in this scope first
            for stmt in node.body:
                # Find variable assignments
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            # Skip private or special variables
                            if var_name.startswith('_') and var_name != '_':
                                continue
                                
                            if var_name not in defined_vars:
                                defined_vars[var_name] = []
                            defined_vars[var_name].append(stmt)
                
                # Find usages within this statement
                for subnode in ast.walk(stmt):
                    if (isinstance(subnode, ast.Name) and 
                        isinstance(subnode.ctx, ast.Load)):
                        used_vars.add(subnode.id)
            
            # Report unused variables in this scope
            for var_name, nodes in defined_vars.items():
                if var_name not in used_vars:
                    for node in nodes:
                        patterns.append({
                            'name': 'unused_variable',
                            'description': f"Variable '{var_name}' is defined but never used",
                            'severity': 'low',
                            'optimization': 'remove_unused_variable',
                            'node': node,
                            'variable': var_name,
                            'lineno': getattr(node, 'lineno', 0)
                        })
        
        # Now process nested scopes
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Module, ast.FunctionDef, ast.ClassDef)):
                self._process_scope(child, patterns)


class RedundantAssignmentDetector(PatternDetector):
    """Detects redundant variable assignments"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find variables that are assigned a value and then immediately overwritten
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        # Add parent references
        ASTNodeVisitor.add_parent_info(tree)
        
        patterns = []
        
        # Process each function
        for func_node in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            # Track assignments to each variable
            var_assignments = {}  # var_name -> [nodes]
            
            # Process body statements
            for stmt in func_node.body:
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                    target = stmt.targets[0]
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        
                        # Check if this variable was just assigned
                        if var_name in var_assignments and var_assignments[var_name]:
                            prev_assign = var_assignments[var_name][-1]
                            
                            # Check if there's no code between the assignments
                            if prev_assign in func_node.body:
                                prev_idx = func_node.body.index(prev_assign)
                                curr_idx = func_node.body.index(stmt)
                                
                                if curr_idx == prev_idx + 1:
                                    patterns.append({
                                        'name': 'redundant_assignment',
                                        'description': f"Variable '{var_name}' is assigned and immediately overwritten",
                                        'severity': 'low',
                                        'optimization': 'remove_redundant_assignment',
                                        'node': prev_assign,
                                        'variable': var_name,
                                        'lineno': getattr(prev_assign, 'lineno', 0)
                                    })
                        
                        # Record this assignment
                        if var_name not in var_assignments:
                            var_assignments[var_name] = []
                        var_assignments[var_name].append(stmt)
        
        return patterns


class RangeLenLoopDetector(PatternDetector):
    """Detects range(len(x)) loops that can be simplified"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find range(len(x)) loops that can be replaced with direct iteration
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Find all for loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if it's a for i in range(len(x)) pattern
                if self._is_range_len_loop(node):
                    # Determine the collection being iterated
                    collection = self._get_collection(node)
                    collection_name = getattr(collection, 'id', None) if isinstance(collection, ast.Name) else 'collection'
                    
                    patterns.append({
                        'name': 'range_len_loop',
                        'description': f"Using range(len({collection_name})) instead of direct iteration",
                        'severity': 'medium',
                        'optimization': 'simplify_range_len_loop',
                        'node': node,
                        'collection': collection,
                        'lineno': getattr(node, 'lineno', 0)
                    })
        
        return patterns
    
    def _is_range_len_loop(self, node: ast.For) -> bool:
        """
        Check if node is a for i in range(len(x)) loop
        
        Args:
            node: For loop node
            
        Returns:
            True if it's a range(len()) loop
        """
        # Check the iterator part
        if not isinstance(node.iter, ast.Call):
            return False
        
        if not (isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range'):
            return False
        
        # Must have at least one argument
        if not node.iter.args:
            return False
        
        # First arg must be len(x)
        first_arg = node.iter.args[0]
        if not isinstance(first_arg, ast.Call):
            return False
        
        if not (isinstance(first_arg.func, ast.Name) and first_arg.func.id == 'len'):
            return False
        
        # len() must have exactly one argument
        return len(first_arg.args) == 1
    
    def _get_collection(self, node: ast.For) -> ast.AST:
        """
        Get the collection being iterated in range(len(collection))
        
        Args:
            node: For loop node
            
        Returns:
            AST node representing the collection
        """
        # Assume _is_range_len_loop was called and returned True
        len_call = node.iter.args[0]
        return len_call.args[0]


class ListAppendLoopDetector(PatternDetector):
    """Detects loops that build lists with append, which could use list comprehension"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find patterns where empty list + for loop with append can be list comprehension
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        # Add parent references
        ASTNodeVisitor.add_parent_info(tree)
        
        patterns = []
        
        # Visit all nodes to find consecutive statements
        for node in ast.walk(tree):
            # Look for code blocks (modules, functions)
            if isinstance(node, (ast.Module, ast.FunctionDef)):
                self._check_block_statements(node.body, patterns)
        
        return patterns
    
    def _check_block_statements(self, statements: List[ast.stmt], patterns: List[Dict[str, Any]]) -> None:
        """
        Check a block of statements for the pattern with better handling of edge cases
        
        Args:
            statements: List of statements to check
            patterns: List to collect detected patterns
        """
        for i in range(len(statements) - 1):
            current_stmt = statements[i]
            next_stmt = statements[i + 1]
            
            # Check for list initialization
            if not isinstance(current_stmt, ast.Assign) or len(current_stmt.targets) != 1:
                continue
            
            target = current_stmt.targets[0]
            if not isinstance(target, ast.Name):
                continue
            
            target_name = target.id
            
            # Check if initializing an empty list
            is_empty_list = False
            if isinstance(current_stmt.value, ast.List) and len(current_stmt.value.elts) == 0:
                is_empty_list = True
            elif (hasattr(ast, 'Call') and 
                  isinstance(current_stmt.value, ast.Call) and 
                  isinstance(current_stmt.value.func, ast.Name) and 
                  current_stmt.value.func.id == 'list' and 
                  not current_stmt.value.args):
                is_empty_list = True
                
            if not is_empty_list:
                continue
            
            # Check if followed by a loop
            if not isinstance(next_stmt, ast.For):
                continue
            
            # Check for append in the loop (direct or in if statement)
            append_expr = None
            conditions = []
            
            # Direct append in loop body
            for body_stmt in next_stmt.body:
                found_expr, found_conditions = self._find_append_in_stmt(body_stmt, target_name)
                if found_expr:
                    append_expr = found_expr
                    conditions = found_conditions
                    break
            
            if append_expr:
                patterns.append({
                    'name': 'list_append_loop',
                    'description': "Loop building a list with append() can be replaced with list comprehension",
                    'severity': 'medium',
                    'optimization': 'convert_to_list_comprehension',
                    'node': current_stmt,
                    'loop_node': next_stmt,
                    'target_name': target_name,
                    'append_expr': append_expr,
                    'conditions': conditions,
                    'lineno': getattr(current_stmt, 'lineno', 0)
                })
    
    def _find_append_in_stmt(self, stmt, target_name):
        """
        Find append call in statement or if-statement
        
        Args:
            stmt: Statement to check
            target_name: Target list name
            
        Returns:
            Tuple of (append_expression, conditions)
        """
        # Direct append call
        if (isinstance(stmt, ast.Expr) and 
            isinstance(stmt.value, ast.Call) and
            isinstance(stmt.value.func, ast.Attribute) and
            stmt.value.func.attr == 'append' and
            isinstance(stmt.value.func.value, ast.Name) and
            stmt.value.func.value.id == target_name and
            len(stmt.value.args) == 1):
            
            return stmt.value.args[0], []
        
        # If statement with append in body
        if isinstance(stmt, ast.If):
            for if_stmt in stmt.body:
                expr, _ = self._find_append_in_stmt(if_stmt, target_name)
                if expr:
                    return expr, [stmt.test]
            
            # Try else clause too
            if stmt.orelse:
                for else_stmt in stmt.orelse:
                    expr, _ = self._find_append_in_stmt(else_stmt, target_name)
                    if expr:
                        # Negate the condition for else
                        negated_test = ast.UnaryOp(
                            op=ast.Not(),
                            operand=stmt.test
                        )
                        return expr, [negated_test]
        
        return None, []


class EmptyLoopDetector(PatternDetector):
    """Detects empty or pass-only loops"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find loops that do nothing
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Find all for and while loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                if not node.body or all(isinstance(stmt, ast.Pass) for stmt in node.body):
                    loop_type = "for" if isinstance(node, ast.For) else "while"
                    patterns.append({
                        'name': 'empty_loop',
                        'description': f"{loop_type.capitalize()} loop contains only 'pass' or is empty",
                        'severity': 'medium',
                        'optimization': 'remove_empty_loop',
                        'node': node,
                        'lineno': getattr(node, 'lineno', 0)
                    })
        
        return patterns


class DeadCodeDetector(PatternDetector):
    """Detects code after return statements"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find code that will never execute (after return)
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Find all functions
        for func_node in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            # Visit each statement in function body
            for i, stmt in enumerate(func_node.body):
                if isinstance(stmt, ast.Return) and i < len(func_node.body) - 1:
                    # Found return with code after it
                    patterns.append({
                        'name': 'dead_code',
                        'description': "Code after return statement will never execute",
                        'severity': 'medium',
                        'optimization': 'remove_dead_code',
                        'node': stmt,
                        'function_node': func_node,
                        'return_index': i,
                        'dead_statements': func_node.body[i+1:],
                        'lineno': getattr(stmt, 'lineno', 0)
                    })
                    # Only report the first instance per function
                    break
        
        return patterns


class RedundantComparisonDetector(PatternDetector):
    """Detects redundant comparisons with True/False"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find comparisons like 'x == True' or 'x == False'
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Find all comparisons
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare) and len(node.ops) == 1:
                # Look for == or is
                if not isinstance(node.ops[0], (ast.Eq, ast.Is)):
                    continue
                
                # Check both sides of the comparison
                for side, other_side in [(node.left, node.comparators[0]), 
                                         (node.comparators[0], node.left)]:
                    # Check if one side is True/False
                    is_true = RuleUtils.is_literal_true(side)
                    is_false = RuleUtils.is_literal_false(side)
                    
                    if is_true or is_false:
                        patterns.append({
                            'name': 'redundant_comparison',
                            'description': f"Redundant comparison with {'True' if is_true else 'False'}",
                            'severity': 'low',
                            'optimization': 'simplify_boolean_comparison',
                            'node': node,
                            'is_true_comparison': is_true,
                            'expression': other_side,
                            'lineno': getattr(node, 'lineno', 0)
                        })
                        break  # Only report once per comparison
        
        return patterns


class StringConcatDetector(PatternDetector):
    """Detects inefficient string concatenation in loops"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find string concatenation in loops that could use join()
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        # Add parent references
        ASTNodeVisitor.add_parent_info(tree)
        
        patterns = []
        
        # Visit all nodes to find consecutive statements
        for node in ast.walk(tree):
            # Look for code blocks (modules, functions)
            if isinstance(node, (ast.Module, ast.FunctionDef)):
                self._check_block_statements(node.body, patterns)
        
        return patterns
    
    def _check_block_statements(self, statements: List[ast.stmt], patterns: List[Dict[str, Any]]) -> None:
        """
        Check block statements for string concatenation pattern
        
        Args:
            statements: List of statements to check
            patterns: List to collect detected patterns
        """
        for i in range(len(statements) - 1):  # Need at least 2 consecutive statements
            # Check for empty string + for loop with +=
            current_stmt = statements[i]
            next_stmt = statements[i + 1]
            
            # First statement must assign empty string
            if not isinstance(current_stmt, ast.Assign) or len(current_stmt.targets) != 1:
                continue
            
            target = current_stmt.targets[0]
            if not isinstance(target, ast.Name):
                continue
            
            target_name = target.id
            
            # Check if it's assigning an empty string
            is_empty_string = False
            if isinstance(current_stmt.value, ast.Str) and current_stmt.value.s == '':
                is_empty_string = True
            elif (hasattr(ast, 'Constant') and 
                  isinstance(current_stmt.value, ast.Constant) and 
                  current_stmt.value.value == ''):
                is_empty_string = True
                
            if not is_empty_string:
                continue
            
            # Next statement must be a for loop
            if not isinstance(next_stmt, ast.For):
                continue
            
            # Loop must contain += for strings
            concat_expr = self._find_string_concat(next_stmt, target_name)
            if not concat_expr:
                continue
            
            # Found a match!
            patterns.append({
                'name': 'string_concat_in_loop',
                'description': "String concatenation in loop can be replaced with join()",
                'severity': 'medium',
                'optimization': 'string_concat_to_join',
                'node': current_stmt,
                'loop_node': next_stmt,
                'target_name': target_name,
                'concat_expr': concat_expr,
                'lineno': getattr(current_stmt, 'lineno', 0)
            })
    
    def _find_string_concat(self, loop_node: ast.For, target_name: str) -> Optional[ast.expr]:
        """
        Find string concatenation inside loop
        
        Args:
            loop_node: For loop node
            target_name: Target string variable name
            
        Returns:
            Expression being concatenated or None
        """
        for stmt in loop_node.body:
            if (isinstance(stmt, ast.AugAssign) and 
                isinstance(stmt.op, ast.Add) and
                isinstance(stmt.target, ast.Name) and
                stmt.target.id == target_name):
                
                return stmt.value
        
        return None


class BooleanReturnDetector(PatternDetector):
    """Detects if/else with boolean returns that can be simplified"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find patterns like 'if x: return True else: return False'
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Find all if statements
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Must have both if and else clauses
                if not node.body or not node.orelse:
                    continue
                
                # Both bodies must be exactly one statement
                if len(node.body) != 1 or len(node.orelse) != 1:
                    continue
                
                # Both statements must be returns
                if_stmt = node.body[0]
                else_stmt = node.orelse[0]
                
                if not isinstance(if_stmt, ast.Return) or not isinstance(else_stmt, ast.Return):
                    continue
                
                # Check if returning True/False or False/True
                if_returns_true = self._is_return_true(if_stmt)
                if_returns_false = self._is_return_false(if_stmt)
                
                else_returns_true = self._is_return_true(else_stmt)
                else_returns_false = self._is_return_false(else_stmt)
                
                # Pattern must be: return True/False or return False/True
                if (if_returns_true and else_returns_false) or (if_returns_false and else_returns_true):
                    patterns.append({
                        'name': 'boolean_return',
                        'description': "if/else with boolean returns can be simplified",
                        'severity': 'medium',
                        'optimization': 'simplify_boolean_return',
                        'node': node,
                        'returns_true_in_if': if_returns_true,
                        'condition': node.test,
                        'lineno': getattr(node, 'lineno', 0)
                    })
        
        return patterns
    
    def _is_return_true(self, node: ast.Return) -> bool:
        """
        Check if node returns True
        
        Args:
            node: Return statement node
            
        Returns:
            True if it returns the literal True
        """
        return RuleUtils.is_literal_true(node.value)
    
    def _is_return_false(self, node: ast.Return) -> bool:
        """
        Check if node returns False
        
        Args:
            node: Return statement node
            
        Returns:
            True if it returns the literal False
        """
        return RuleUtils.is_literal_false(node.value)


class UniqueValuesDetector(PatternDetector):
    """Detects inefficient uniqueness filtering implementations"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find uniqueness filtering pattern that could use set()
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # First approach: check function names
        for func_node in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            # Check if function name suggests uniqueness
            if 'unique' in func_node.name.lower() or 'distinct' in func_node.name.lower():
                # Check for algorithm pattern
                has_empty_list = False
                has_loop = False
                has_not_in_check = False
                has_append = False
                result_var = None
                
                # Find empty list initialization
                for stmt in func_node.body:
                    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                        if (isinstance(stmt.targets[0], ast.Name) and 
                            isinstance(stmt.value, ast.List) and 
                            len(stmt.value.elts) == 0):
                            has_empty_list = True
                            result_var = stmt.targets[0].id
                            break
                
                if not has_empty_list or not result_var:
                    continue
                
                # Look for for loop
                for stmt in func_node.body:
                    if isinstance(stmt, ast.For):
                        has_loop = True
                        
                        # Look for not in check + append in loop body
                        for body_stmt in ast.walk(stmt):
                            if (isinstance(body_stmt, ast.Compare) and 
                                any(isinstance(op, ast.NotIn) for op in body_stmt.ops)):
                                # Check if the right operand is our result list
                                for comparator in body_stmt.comparators:
                                    if (isinstance(comparator, ast.Name) and 
                                        comparator.id == result_var):
                                        has_not_in_check = True
                                        break
                            
                            if (isinstance(body_stmt, ast.Call) and 
                                isinstance(body_stmt.func, ast.Attribute) and
                                body_stmt.func.attr == 'append' and
                                isinstance(body_stmt.func.value, ast.Name) and
                                body_stmt.func.value.id == result_var):
                                has_append = True
                        
                        break  # Only need to check one for loop
                
                # Check if it matches the inefficient pattern
                if has_empty_list and has_loop and has_not_in_check and has_append:
                    patterns.append({
                        'name': 'inefficient_unique_values',
                        'description': "Inefficient uniqueness filtering that could use set()",
                        'severity': 'medium',
                        'optimization': 'optimize_unique_values',
                        'node': func_node,
                        'result_var': result_var,
                        'lineno': getattr(func_node, 'lineno', 0)
                    })
        
        # Second approach: look for pattern even without suggestive function name
        for func_node in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            # Check for empty list + for loop with not in check + append
            if len(func_node.body) >= 3:  # Need at least init, loop, return
                # Try to find empty list initialization
                init_stmt = func_node.body[0]
                if (isinstance(init_stmt, ast.Assign) and 
                    len(init_stmt.targets) == 1 and
                    isinstance(init_stmt.targets[0], ast.Name) and
                    isinstance(init_stmt.value, ast.List) and
                    len(init_stmt.value.elts) == 0):
                    
                    result_var = init_stmt.targets[0].id
                    
                    # Look for for loop
                    if len(func_node.body) > 1 and isinstance(func_node.body[1], ast.For):
                        for_node = func_node.body[1]
                        
                        # Check for if item not in result: result.append(item)
                        has_pattern = False
                        if len(for_node.body) == 1 and isinstance(for_node.body[0], ast.If):
                            if_node = for_node.body[0]
                            
                            # Check condition is "not in"
                            if (isinstance(if_node.test, ast.Compare) and
                                len(if_node.test.ops) == 1 and
                                isinstance(if_node.test.ops[0], ast.NotIn) and
                                isinstance(if_node.test.comparators[0], ast.Name) and
                                if_node.test.comparators[0].id == result_var):
                                
                                # Check body has append
                                if len(if_node.body) == 1:
                                    stmt = if_node.body[0]
                                    if (isinstance(stmt, ast.Expr) and
                                        isinstance(stmt.value, ast.Call) and
                                        isinstance(stmt.value.func, ast.Attribute) and
                                        stmt.value.func.attr == 'append' and
                                        isinstance(stmt.value.func.value, ast.Name) and
                                        stmt.value.func.value.id == result_var):
                                        
                                        has_pattern = True
                        
                        # Check last statement returns the result
                        last_stmt = func_node.body[-1]
                        if (isinstance(last_stmt, ast.Return) and
                            isinstance(last_stmt.value, ast.Name) and
                            last_stmt.value.id == result_var and
                            has_pattern and
                            # Make sure we haven't already caught this function
                            not any(p.get('node') == func_node for p in patterns)):
                            
                            patterns.append({
                                'name': 'inefficient_unique_values',
                                'description': "Inefficient uniqueness filtering that could use set()",
                                'severity': 'medium',
                                'optimization': 'optimize_unique_values',
                                'node': func_node,
                                'result_var': result_var,
                                'lineno': getattr(func_node, 'lineno', 0)
                            })
        
        return patterns


class RedundantPassDetector(PatternDetector):
    """Detects redundant pass statements in if blocks"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find if conditions with empty pass
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Find all if statements
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check if the body is just a pass statement
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass) and node.orelse:
                    patterns.append({
                        'name': 'redundant_pass',
                        'description': "If statement with only 'pass' can be inverted",
                        'severity': 'low',
                        'optimization': 'remove_redundant_pass',
                        'node': node,
                        'condition': node.test,
                        'else_body': node.orelse,
                        'lineno': getattr(node, 'lineno', 0)
                    })
        
        return patterns


class ChainedComparisonDetector(PatternDetector):
    """Detects chained equality comparisons that can use 'in'"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find patterns like x == 1 or x == 2 or x == 3
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Find all boolean operations with 'or'
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                # Check for chained equality tests with OR
                chained = self._is_chained_equality(node)
                if chained:
                    patterns.append({
                        'name': 'chained_comparison',
                        'description': "Chained equality comparisons can use 'in' operator",
                        'severity': 'medium',
                        'optimization': 'use_in_operator',
                        'node': node,
                        'variable': chained['variable'],
                        'values': chained['values'],
                        'lineno': getattr(node, 'lineno', 0)
                    })
        
        return patterns
        
    def _is_chained_equality(self, node):
        """
        Check if node is x == 1 or x == 2 or x == 3 pattern
        
        Args:
            node: BoolOp node with or operator
            
        Returns:
            Dict with variable and values if pattern matches, None otherwise
        """
        if not isinstance(node, ast.BoolOp) or not isinstance(node.op, ast.Or):
            return None
            
        # Check all values in the chain
        variable_id = None
        values = []
        
        for value in node.values:
            if not isinstance(value, ast.Compare) or len(value.ops) != 1 or not isinstance(value.ops[0], ast.Eq):
                return None
                
            # Get the variable being compared
            if isinstance(value.left, ast.Name):
                current_var = value.left.id
                
                # First comparison establishes the variable
                if variable_id is None:
                    variable_id = current_var
                # Subsequent comparisons must use same variable
                elif variable_id != current_var:
                    return None
                    
                # Get the value being compared to
                if len(value.comparators) == 1:
                    comparator = value.comparators[0]
                    
                    # Handle different types of constants
                    if RuleUtils.is_constant_node(comparator):
                        values.append(RuleUtils.get_constant_value(comparator))
                    else:
                        # Complex expression - not a good candidate for optimization
                        return None
                else:
                    return None
            else:
                return None
                
        # Must have at least 2 values to be worth converting
        if len(values) >= 2:
            return {'variable': variable_id, 'values': values}
            
        return None


class SingleUseVariableDetector(PatternDetector):
    """Detects variables used only once in returns"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find variables that are used only once in a return statement
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Add parent references
        ASTNodeVisitor.add_parent_info(tree)
        
        # Process each function definition
        for func_node in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            # Track variable definitions and uses
            var_defs = {}  # var_name -> node
            var_uses = {}  # var_name -> [nodes]
            
            # First pass: collect definitions
            for i, stmt in enumerate(func_node.body):
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                    if isinstance(stmt.targets[0], ast.Name):
                        var_name = stmt.targets[0].id
                        var_defs[var_name] = (stmt, i)
            
            # Second pass: collect uses
            for node in ast.walk(func_node):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    var_name = node.id
                    if var_name in var_defs:
                        if var_name not in var_uses:
                            var_uses[var_name] = []
                        var_uses[var_name].append(node)
            
            # Find variables used exactly once in a return statement
            for var_name, (def_node, def_index) in var_defs.items():
                uses = var_uses.get(var_name, [])
                if len(uses) == 1:
                    use_node = uses[0]
                    parent = getattr(use_node, 'parent', None)
                    
                    if isinstance(parent, ast.Return):
                        # Check if the return is the only use
                        if (isinstance(parent.value, ast.Name) and 
                            parent.value.id == var_name):
                            
                            # Find the return statement's index
                            return_index = None
                            for i, stmt in enumerate(func_node.body):
                                if stmt is parent:
                                    return_index = i
                                    break
                            
                            # Only consider if return comes after definition
                            if return_index is not None and return_index > def_index:
                                # Check if there are no other statements between definition and return
                                if return_index == def_index + 1:
                                    patterns.append({
                                        'name': 'single_use_variable',
                                        'description': f"Variable '{var_name}' is only used once in return",
                                        'severity': 'low',
                                        'optimization': 'inline_single_use_variable',
                                        'node': def_node,
                                        'return_node': parent,
                                        'variable': var_name,
                                        'lineno': getattr(def_node, 'lineno', 0)
                                    })
        
        return patterns


class NestedIfDetector(PatternDetector):
    """Detects nested if statements that can be combined"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find patterns like if a: if b: return c
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Add parent info
        ASTNodeVisitor.add_parent_info(tree)
        
        # Find all if statements
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check if it has exactly one statement in body
                if len(node.body) == 1 and isinstance(node.body[0], ast.If):
                    inner_if = node.body[0]
                    
                    # Inner if should have a simple body
                    if len(inner_if.body) > 0 and not inner_if.orelse:
                        patterns.append({
                            'name': 'nested_if',
                            'description': "Nested if statements can be combined",
                            'severity': 'low',
                            'optimization': 'combine_nested_if',
                            'node': node,
                            'inner_if': inner_if,
                            'outer_test': node.test,
                            'inner_test': inner_if.test,
                            'inner_body': inner_if.body,
                            'lineno': getattr(node, 'lineno', 0)
                        })
        
        return patterns


class UnusedImportDetector(PatternDetector):
    """Detects unused imports"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find imports that are not used in the code
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Collect import names and their nodes
        imports = {}  # name -> node
        
        # First pass: collect all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    asname = name.asname or name.name
                    imports[asname] = (node, name)
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    asname = name.asname or name.name
                    imports[asname] = (node, name)
        
        # Second pass: check usage
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            # Also check attribute accesses for module usage
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
        
        # Find unused imports (excluding special names)
        for name, (node, import_name) in imports.items():
            # Skip imports used for their side effects or special names
            if name.startswith('_') or name in ('__future__', 'typing', 'sys', 'os'):
                continue
                
            if name not in used_names:
                # For ImportFrom, get the module info
                module_name = None
                if isinstance(node, ast.ImportFrom) and node.module:
                    module_name = node.module
                
                patterns.append({
                    'name': 'unused_import',
                    'description': f"Import '{name}'" + (f" from '{module_name}'" if module_name else "") + " is not used",
                    'severity': 'low',
                    'optimization': 'remove_unused_import',
                    'node': node,
                    'import_name': name,
                    'import_node': import_name,
                    'lineno': getattr(node, 'lineno', 0)
                })
        
        return patterns


class NotNotToBoolDetector(PatternDetector):
    """Detects not not value pattern that can be simplified to bool(value)"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find not not value patterns
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Look for UnaryOp(not, UnaryOp(not, value))
        for node in ast.walk(tree):
            if (isinstance(node, ast.UnaryOp) and 
                isinstance(node.op, ast.Not) and
                isinstance(node.operand, ast.UnaryOp) and 
                isinstance(node.operand.op, ast.Not)):
                
                patterns.append({
                    'name': 'not_not_pattern',
                    'description': "not not value can be simplified to bool(value)",
                    'severity': 'low',
                    'optimization': 'convert_to_bool',
                    'node': node,
                    'value': node.operand.operand,
                    'lineno': getattr(node, 'lineno', 0)
                })
        
        return patterns


class RedundantParenthesesDetector(PatternDetector):
    """Detects redundant parentheses in expressions (limited capability)"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find redundant parentheses in code (based on AST inspection)
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Unfortunately, AST doesn't preserve parentheses information
        # However, we can still detect some patterns
        
        # Look for single-element tuples that might be redundant parentheses
        for node in ast.walk(tree):
            if isinstance(node, ast.Tuple) and len(node.elts) == 1:
                # This might be a redundant parenthesized expression
                patterns.append({
                    'name': 'redundant_parentheses',
                    'description': "Redundant parentheses around expression",
                    'severity': 'low',
                    'optimization': 'remove_redundant_parentheses',
                    'node': node,
                    'expression': node.elts[0],
                    'lineno': getattr(node, 'lineno', 0)
                })
                
        # Look for return statements where the value is a parenthesized simple expression
        for node in ast.walk(tree):
            if isinstance(node, ast.Return):
                if isinstance(node.value, ast.Name) or RuleUtils.is_constant_node(node.value):
                    # Might have redundant parentheses but we can't tell from AST
                    # In a future version, we might use the original source text
                    pass
                    
        return patterns


class FormatToFStringDetector(PatternDetector):
    """Detects string format() calls that can be converted to f-strings"""
    
    def _detect_in_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Find string format calls that can be converted to f-strings
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Look for str.format() calls
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                node.func.attr == 'format'):
                
                # Get the string template
                if isinstance(node.func.value, ast.Str) or (
                    hasattr(ast, 'Constant') and
                    isinstance(node.func.value, ast.Constant) and
                    isinstance(node.func.value.value, str)):
                    
                    # Get the format string
                    format_str = (node.func.value.s if isinstance(node.func.value, ast.Str)
                                 else node.func.value.value)
                    
                    # Check if it has format placeholders
                    if '{' in format_str and '}' in format_str:
                        # Try to analyze the placeholders and arguments
                        args = node.args
                        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
                        
                        # Simple check for Python 3.6+ compatibility
                        if sys.version_info >= (3, 6):
                            patterns.append({
                                'name': 'format_to_fstring',
                                'description': "String format() can be converted to f-string",
                                'severity': 'low',
                                'optimization': 'convert_to_fstring',
                                'node': node,
                                'format_str': format_str,
                                'args': args,
                                'kwargs': kwargs,
                                'lineno': getattr(node, 'lineno', 0)
                            })
        
        return patterns
    
###########################################
# PART 3: Code Transformers for Optimizations
###########################################

class UnusedVariableTransformer(CodeTransformer):
    """Removes unused variable assignments"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """Remove unused variable assignments"""
        # First detect unused variables
        detector = UnusedVariableDetector()
        patterns = detector.detect(self._ast_to_code(tree))
        
        if not patterns:
            return tree
        
        # Get list of unused variable names
        unused_vars = set(p['variable'] for p in patterns)
        
        # Create the transformer
        class RemoveUnusedTransformer(ast.NodeTransformer):
            def __init__(self):
                self.removed_count = 0
            
            def visit_Assign(self, node):
                # Check if this is an assignment to an unused variable
                if (len(node.targets) == 1 and 
                    isinstance(node.targets[0], ast.Name) and
                    node.targets[0].id in unused_vars):
                    
                    self.removed_count += 1
                    return None  # Remove this node
                
                return self.generic_visit(node)
        
        # Apply transformation
        transformer = RemoveUnusedTransformer()
        new_tree = transformer.visit(copy.deepcopy(tree))
        
        logger.info(f"Removed {transformer.removed_count} unused variable assignments")
        return new_tree


class RedundantAssignmentTransformer(CodeTransformer):
    """Removes redundant variable assignments"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Remove redundant assignments
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = RedundantAssignmentDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Get the line numbers of statements to remove
        nodes_to_remove = set(pattern['node'].lineno for pattern in patterns if hasattr(pattern['node'], 'lineno'))
        
        # For each function definition in the tree
        for func_node in [n for n in ast.walk(tree_copy) if isinstance(n, ast.FunctionDef)]:
            # Filter the function body to remove the redundant assignments
            func_node.body = [
                stmt for stmt in func_node.body 
                if not (isinstance(stmt, ast.Assign) and 
                        hasattr(stmt, 'lineno') and 
                        stmt.lineno in nodes_to_remove)
            ]
        
        logger.info(f"Removed {len(patterns)} redundant assignments")
        return tree_copy


class RangeLenLoopTransformer(CodeTransformer):
    """Transforms range(len(x)) loops to direct iteration"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Convert range(len(x)) loops to direct iteration
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = RangeLenLoopDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Track transformed count
        transformed_count = 0
        
        class RangeLenTransformer(ast.NodeTransformer):
            def visit_For(self, node):
                # Process any nested structures first
                self.generic_visit(node)
                
                # Check if this is one of our patterns
                for pattern in patterns:
                    if (hasattr(pattern['node'], 'lineno') and 
                        hasattr(node, 'lineno') and 
                        pattern['node'].lineno == node.lineno):
                        
                        # Create a new loop that iterates directly over the collection
                        new_node = ast.For(
                            target=ast.Name(id='item', ctx=ast.Store()),
                            iter=pattern['collection'],
                            body=node.body,
                            orelse=node.orelse
                        )
                        
                        # Copy location info
                        ast.copy_location(new_node, node)
                        
                        nonlocal transformed_count
                        transformed_count += 1
                        return new_node
                
                return node
        
        # Apply transformation
        transformer = RangeLenTransformer()
        result = transformer.visit(tree_copy)
        
        logger.info(f"Transformed {transformed_count} range(len()) loops")
        return result


class ListComprehensionTransformer(CodeTransformer):
    """Transforms list append loops to list comprehensions"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Convert list append loops to list comprehensions
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = ListAppendLoopDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Track pattern nodes by lineno
        pattern_map = {}
        for pattern in patterns:
            if hasattr(pattern['node'], 'lineno'):
                pattern_map[pattern['node'].lineno] = pattern
        
        # Process each block that might contain our patterns
        for node in ast.walk(tree_copy):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and hasattr(node, 'body'):
                self._transform_block(node.body, pattern_map)
        
        logger.info(f"Transformed {len(patterns)} list append loops to comprehensions")
        return tree_copy
    
    def _transform_block(self, statements: List[ast.stmt], pattern_map: Dict[int, Dict[str, Any]]) -> None:
        """
        Transform list append patterns in a block
        
        Args:
            statements: List of statements to transform
            pattern_map: Map of patterns by line number
        """
        i = 0
        while i < len(statements) - 1:
            # Check if current statement is part of a pattern
            current_stmt = statements[i]
            next_stmt = statements[i + 1]
            
            # Try to match by line number
            if (hasattr(current_stmt, 'lineno') and 
                current_stmt.lineno in pattern_map and 
                isinstance(next_stmt, ast.For)):
                
                pattern = pattern_map[current_stmt.lineno]
                
                # Create list comprehension
                generators = [
                    ast.comprehension(
                        target=next_stmt.target,
                        iter=next_stmt.iter,
                        ifs=pattern.get('conditions', []),
                        is_async=0
                    )
                ]
                
                list_comp = ast.ListComp(
                    elt=pattern['append_expr'],
                    generators=generators
                )
                
                # Create assignment to comprehension
                new_assign = ast.Assign(
                    targets=[ast.Name(id=pattern['target_name'], ctx=ast.Store())],
                    value=list_comp
                )
                
                # Copy location information
                ast.copy_location(new_assign, current_stmt)
                
                # Replace the two statements with the comprehension
                statements[i] = new_assign
                statements.pop(i + 1)
                
                # Don't increment i since we removed a statement
            else:
                # Process nested blocks
                if hasattr(statements[i], 'body'):
                    self._transform_block(statements[i].body, pattern_map)
                if hasattr(statements[i], 'orelse'):
                    self._transform_block(statements[i].orelse, pattern_map)
                    
                i += 1
        
        # Process the last statement if it exists
        if statements and hasattr(statements[-1], 'body'):
            self._transform_block(statements[-1].body, pattern_map)
        if statements and hasattr(statements[-1], 'orelse'):
            self._transform_block(statements[-1].orelse, pattern_map)


class EmptyLoopTransformer(CodeTransformer):
    """Removes loops that do nothing"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Remove empty loops
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = EmptyLoopDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Track nodes to remove by lineno
        lines_to_remove = set(pattern['node'].lineno for pattern in patterns if hasattr(pattern['node'], 'lineno'))
        
        # Process each scope
        for node in ast.walk(tree_copy):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and hasattr(node, 'body'):
                # Filter out empty loops
                node.body = [
                    stmt for stmt in node.body 
                    if not (isinstance(stmt, (ast.For, ast.While)) and 
                           hasattr(stmt, 'lineno') and 
                           stmt.lineno in lines_to_remove)
                ]
        
        logger.info(f"Removed {len(patterns)} empty loops")
        return tree_copy


class DeadCodeTransformer(CodeTransformer):
    """Removes code after return statements"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Remove code after return statements
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = DeadCodeDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Process each function
        for pattern in patterns:
            # Find the matching function in our copied tree
            for func_node in [n for n in ast.walk(tree_copy) if isinstance(n, ast.FunctionDef)]:
                if (hasattr(func_node, 'name') and 
                    hasattr(pattern['function_node'], 'name') and
                    func_node.name == pattern['function_node'].name and
                    hasattr(func_node, 'lineno') and
                    hasattr(pattern['function_node'], 'lineno') and
                    func_node.lineno == pattern['function_node'].lineno):
                    
                    # Truncate the function body after the return
                    for i, stmt in enumerate(func_node.body):
                        if (isinstance(stmt, ast.Return) and 
                            i == pattern['return_index']):
                            # Keep everything up to and including this return
                            func_node.body = func_node.body[:i+1]
                            break
        
        logger.info(f"Removed dead code after {len(patterns)} return statements")
        return tree_copy


class BooleanComparisonTransformer(CodeTransformer):
    """Simplifies redundant boolean comparisons"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Simplify comparisons with True/False
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = RedundantComparisonDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class BooleanSimplifier(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
            
            def visit_Compare(self, node):
                """Transform x == True to x and x == False to not x"""
                # Process children first
                self.generic_visit(node)
                
                # Only handle single comparisons with == or is
                if len(node.ops) != 1 or not isinstance(node.ops[0], (ast.Eq, ast.Is)):
                    return node
                
                # Check against patterns by lineno
                if (hasattr(node, 'lineno') and 
                    any(p['node'].lineno == node.lineno for p in patterns if hasattr(p['node'], 'lineno'))):
                    
                    # Find matching pattern
                    for pattern in patterns:
                        if (hasattr(pattern['node'], 'lineno') and 
                            node.lineno == pattern['node'].lineno):
                            
                            if pattern['is_true_comparison']:
                                # x == True -> x
                                self.transformed_count += 1
                                return pattern['expression']
                            else:
                                # x == False -> not x
                                not_expr = ast.UnaryOp(
                                    op=ast.Not(),
                                    operand=pattern['expression']
                                )
                                
                                # Copy location info
                                ast.copy_location(not_expr, node)
                                
                                self.transformed_count += 1
                                return not_expr
                
                return node
        
        # Apply transformation
        simplifier = BooleanSimplifier()
        result = simplifier.visit(tree_copy)
        
        logger.info(f"Simplified {simplifier.transformed_count} boolean comparisons")
        return result


class StringConcatTransformer(CodeTransformer):
    """Transforms string concatenation in loops to join()"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Convert string concatenation in loops to join()
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = StringConcatDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Map patterns by line number
        pattern_map = {}
        for pattern in patterns:
            if hasattr(pattern['node'], 'lineno'):
                pattern_map[pattern['node'].lineno] = pattern
        
        # Process blocks that might contain our patterns
        for node in ast.walk(tree_copy):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and hasattr(node, 'body'):
                self._transform_block(node.body, pattern_map)
        
        logger.info(f"Transformed {len(patterns)} string concatenations to join()")
        return tree_copy
    
    def _transform_block(self, statements: List[ast.stmt], pattern_map: Dict[int, Dict[str, Any]]) -> None:
        """
        Transform string concatenation patterns in a block
        
        Args:
            statements: List of statements to transform
            pattern_map: Map of patterns by line number
        """
        i = 0
        while i < len(statements) - 1:
            # Check for string concat pattern
            current_stmt = statements[i]
            next_stmt = statements[i + 1]
            
            # Check if it matches one of our patterns
            if (hasattr(current_stmt, 'lineno') and 
                current_stmt.lineno in pattern_map and
                isinstance(next_stmt, ast.For)):
                
                pattern = pattern_map[current_stmt.lineno]
                
                # Create a join expression
                # Create empty string literal
                empty_str = RuleUtils.create_constant_node("")
                
                # Create list comprehension for items to join
                list_comp = ast.ListComp(
                    elt=pattern['concat_expr'],
                    generators=[
                        ast.comprehension(
                            target=next_stmt.target,
                            iter=next_stmt.iter,
                            ifs=[],
                            is_async=0
                        )
                    ]
                )
                
                # Create ''.join(list_comp)
                join_call = ast.Call(
                    func=ast.Attribute(
                        value=empty_str,
                        attr='join',
                        ctx=ast.Load()
                    ),
                    args=[list_comp],
                    keywords=[]
                )
                
                # Create assignment
                new_assign = ast.Assign(
                    targets=[ast.Name(id=pattern['target_name'], ctx=ast.Store())],
                    value=join_call
                )
                
                # Copy location info
                ast.copy_location(new_assign, current_stmt)
                
                # Replace statements
                statements[i] = new_assign
                statements.pop(i + 1)
                
                # Don't increment i since we removed a statement
            else:
                # Process nested blocks
                if hasattr(statements[i], 'body'):
                    self._transform_block(statements[i].body, pattern_map)
                if hasattr(statements[i], 'orelse'):
                    self._transform_block(statements[i].orelse, pattern_map)
                    
                i += 1
        
        # Process the last statement if it exists
        if statements and hasattr(statements[-1], 'body'):
            self._transform_block(statements[-1].body, pattern_map)
        if statements and hasattr(statements[-1], 'orelse'):
            self._transform_block(statements[-1].orelse, pattern_map)


class BooleanReturnTransformer(CodeTransformer):
    """Simplifies boolean return statements"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Simplify if/else with boolean returns
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = BooleanReturnDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class BooleanReturnSimplifier(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
                
            def visit_If(self, node):
                # Process children first (bottom-up transformation)
                self.generic_visit(node)
                
                # Check if this node matches any of our patterns
                for pattern in patterns:
                    if (hasattr(pattern['node'], 'lineno') and 
                        hasattr(node, 'lineno') and
                        pattern['node'].lineno == node.lineno):
                        
                        # Check the pattern type
                        if pattern['returns_true_in_if']:
                            # if x: return True else: return False -> return x
                            return_node = ast.Return(value=node.test)
                        else:
                            # if x: return False else: return True -> return not x
                            return_node = ast.Return(
                                value=ast.UnaryOp(
                                    op=ast.Not(),
                                    operand=node.test
                                )
                            )
                        
                        # Copy location info
                        ast.copy_location(return_node, node)
                        
                        self.transformed_count += 1
                        return return_node
                
                return node
        
        # Apply transformation
        simplifier = BooleanReturnSimplifier()
        result = simplifier.visit(tree_copy)
        
        logger.info(f"Simplified {simplifier.transformed_count} boolean returns")
        return result


class RedundantPassTransformer(CodeTransformer):
    """Removes redundant pass statements"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Transform if condition: pass else: ... to if not condition: ...
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = RedundantPassDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class PassRemover(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
                
            def visit_If(self, node):
                # Check if node matches pattern by lineno
                for pattern in patterns:
                    if (hasattr(pattern['node'], 'lineno') and 
                        hasattr(node, 'lineno') and
                        pattern['node'].lineno == node.lineno):
                        
                        # Create inverted condition
                        inverted_test = ast.UnaryOp(
                            op=ast.Not(),
                            operand=node.test
                        )
                        
                        # Create new if with inverted condition
                        new_node = ast.If(
                            test=inverted_test,
                            body=node.orelse,
                            orelse=[]
                        )
                        
                        # Copy line and col info
                        ast.copy_location(new_node, node)
                        
                        self.transformed_count += 1
                        return new_node
                
                # Process children for nested ifs
                self.generic_visit(node)
                return node
                
        # Apply transformation
        transformer = PassRemover()
        result = transformer.visit(tree_copy)
        
        logger.info(f"Transformed {transformer.transformed_count} redundant pass statements")
        return result


class ChainedComparisonTransformer(CodeTransformer):
    """Transforms chained equality comparisons to use 'in' operator"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Transform x == 1 or x == 2 or x == 3 to x in {1, 2, 3}
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = ChainedComparisonDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class ComparisonTransformer(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
                
            def visit_BoolOp(self, node):
                # Process children first
                self.generic_visit(node)
                
                # Check if this is one of our patterns
                for pattern in patterns:
                    if (hasattr(pattern['node'], 'lineno') and 
                        hasattr(node, 'lineno') and
                        pattern['node'].lineno == node.lineno):
                        
                        # Create a set literal with the values
                        elts = []
                        for value in pattern['values']:
                            elts.append(RuleUtils.create_constant_node(value))
                            
                        set_node = ast.Set(elts=elts)
                        
                        # Create x in {1, 2, 3} test
                        in_test = ast.Compare(
                            left=ast.Name(id=pattern['variable'], ctx=ast.Load()),
                            ops=[ast.In()],
                            comparators=[set_node]
                        )
                        
                        # Copy location info
                        ast.copy_location(in_test, node)
                        
                        self.transformed_count += 1
                        return in_test
                
                return node
                
        # Apply transformation
        transformer = ComparisonTransformer()
        result = transformer.visit(tree_copy)
        
        logger.info(f"Transformed {transformer.transformed_count} chained comparisons")
        return result


class SingleUseVariableTransformer(CodeTransformer):
    """Inlines variables used only once in returns"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Inline variables used only once in return statements
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = SingleUseVariableDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Add parent references
        ASTNodeVisitor.add_parent_info(tree_copy)
        
        # Group patterns by function and variable
        by_function = {}
        for pattern in patterns:
            # Find the parent function
            parent_func = None
            node = pattern['node']
            while hasattr(node, 'parent'):
                if isinstance(node.parent, ast.FunctionDef):
                    parent_func = node.parent
                    break
                node = node.parent
            
            if parent_func and hasattr(parent_func, 'name'):
                func_name = parent_func.name
                var_name = pattern['variable']
                
                if func_name not in by_function:
                    by_function[func_name] = {}
                    
                if var_name not in by_function[func_name]:
                    by_function[func_name][var_name] = pattern
        
        # Process each function in the tree
        for func_node in [n for n in ast.walk(tree_copy) if isinstance(n, ast.FunctionDef)]:
            if func_node.name in by_function:
                var_patterns = by_function[func_node.name]
                
                # Track statements to remove
                to_remove = set()
                
                # First pass: collect variables and their values
                var_to_value = {}
                for i, stmt in enumerate(func_node.body):
                    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                        if isinstance(stmt.targets[0], ast.Name):
                            var_name = stmt.targets[0].id
                            if var_name in var_patterns:
                                var_to_value[var_name] = stmt.value
                                to_remove.add(i)
                
                # Second pass: replace return values
                for i, stmt in enumerate(func_node.body):
                    if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Name):
                        var_name = stmt.value.id
                        if var_name in var_to_value:
                            # Replace return var with its value
                            stmt.value = var_to_value[var_name]
                
                # Third pass: remove the variable assignments
                func_node.body = [stmt for i, stmt in enumerate(func_node.body) if i not in to_remove]
        
        logger.info(f"Inlined {len(patterns)} single-use variables")
        return tree_copy


class NestedIfCombiner(CodeTransformer):
    """Combines nested if statements"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Transform if a: if b: ... to if a and b: ...
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = NestedIfDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class IfCombiner(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
                
            def visit_If(self, node):
                # Check if this node matches any of our patterns
                matches_pattern = False
                for pattern in patterns:
                    if (hasattr(pattern['node'], 'lineno') and 
                        hasattr(node, 'lineno') and
                        pattern['node'].lineno == node.lineno):
                        
                        # Create combined condition (a and b)
                        combined_test = ast.BoolOp(
                            op=ast.And(),
                            values=[pattern['outer_test'], pattern['inner_test']]
                        )
                        
                        # Replace test and body
                        node.test = combined_test
                        node.body = pattern['inner_body']
                        
                        self.transformed_count += 1
                        matches_pattern = True
                        break
                
                # If this was a pattern, don't visit children (we removed the nested if)
                if not matches_pattern:
                    self.generic_visit(node)
                    
                return node
        
        # Apply transformation
        combiner = IfCombiner()
        result = combiner.visit(tree_copy)
        
        logger.info(f"Combined {combiner.transformed_count} nested if statements")
        return result


class UnusedImportTransformer(CodeTransformer):
    """Removes unused imports"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Remove imports that are not used in the code
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = UnusedImportDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        # Collect all unused import names and nodes
        unused_imports = {}
        for pattern in patterns:
            unused_imports[pattern['import_name']] = pattern['import_node']
        
        # Process module statements
        if isinstance(tree_copy, ast.Module):
            new_body = []
            for stmt in tree_copy.body:
                if isinstance(stmt, ast.Import):
                    # Keep only used imports
                    new_names = []
                    for name in stmt.names:
                        asname = name.asname or name.name
                        if asname not in unused_imports or unused_imports[asname] is not name:
                            new_names.append(name)
                    
                    if new_names:
                        stmt.names = new_names
                        new_body.append(stmt)
                    # Skip if all names were unused
                elif isinstance(stmt, ast.ImportFrom):
                    # Check if any names are used
                    new_names = []
                    for name in stmt.names:
                        asname = name.asname or name.name
                        if asname not in unused_imports or unused_imports[asname] is not name:
                            new_names.append(name)
                    
                    if new_names:
                        stmt.names = new_names
                        new_body.append(stmt)
                    # Skip if all names were unused
                else:
                    new_body.append(stmt)
            
            tree_copy.body = new_body
        
        logger.info(f"Removed {len(patterns)} unused imports")
        return tree_copy


class NotNotToBoolTransformer(CodeTransformer):
    """Transforms not not value to bool(value)"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Replace not not value with bool(value)
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = NotNotToBoolDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class NotNotTransformer(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
                
            def visit_UnaryOp(self, node):
                # Process children first
                self.generic_visit(node)
                
                # Check if this is a not not pattern
                if (isinstance(node.op, ast.Not) and 
                    isinstance(node.operand, ast.UnaryOp) and 
                    isinstance(node.operand.op, ast.Not)):
                    
                    # Verify against patterns by line number
                    if hasattr(node, 'lineno'):
                        for pattern in patterns:
                            if (hasattr(pattern['node'], 'lineno') and 
                                pattern['node'].lineno == node.lineno):
                                
                                # Replace with bool() call
                                bool_call = ast.Call(
                                    func=ast.Name(id='bool', ctx=ast.Load()),
                                    args=[pattern['value']],
                                    keywords=[]
                                )
                                
                                # Copy location info
                                ast.copy_location(bool_call, node)
                                
                                self.transformed_count += 1
                                return bool_call
                
                return node
        
        # Apply transformation
        transformer = NotNotTransformer()
        result = transformer.visit(tree_copy)
        
        logger.info(f"Transformed {transformer.transformed_count} not not patterns to bool()")
        return result


class RedundantParenthesesTransformer(CodeTransformer):
    """Removes redundant parentheses from expressions (limited capability)"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Remove redundant parentheses
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = RedundantParenthesesDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class ParenthesesRemover(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
                
            def visit_Tuple(self, node):
                # Process children first
                self.generic_visit(node)
                
                # Check for single-element tuples that might be redundant parentheses
                if len(node.elts) == 1:
                    # Check against patterns
                    if hasattr(node, 'lineno'):
                        for pattern in patterns:
                            if (hasattr(pattern['node'], 'lineno') and 
                                pattern['node'].lineno == node.lineno):
                                
                                # Replace with the inner expression
                                self.transformed_count += 1
                                return node.elts[0]
                
                return node
        
        # Apply transformation
        remover = ParenthesesRemover()
        result = remover.visit(tree_copy)
        
        logger.info(f"Removed {remover.transformed_count} redundant parentheses")
        return result


class UniqueValuesTransformer(CodeTransformer):
    """Transforms inefficient unique values implementation to use set()"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Replace unique values implementation with set()
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        detector = UniqueValuesDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class SetBasedTransformer(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
                
            def visit_FunctionDef(self, node):
                # Check if this function matches one of our patterns
                for pattern in patterns:
                    if (hasattr(pattern['node'], 'lineno') and 
                        hasattr(node, 'lineno') and
                        pattern['node'].lineno == node.lineno):
                        
                        # Get input parameter name
                        param_name = None
                        if node.args.args:
                            param_name = node.args.args[0].arg
                        else:
                            # Default to 'items' if no parameters
                            param_name = 'items'
                        
                        # Create list(set(items))
                        set_call = ast.Call(
                            func=ast.Name(id='set', ctx=ast.Load()),
                            args=[ast.Name(id=param_name, ctx=ast.Load())],
                            keywords=[]
                        )
                        
                        list_call = ast.Call(
                            func=ast.Name(id='list', ctx=ast.Load()),
                            args=[set_call],
                            keywords=[]
                        )
                        
                        # Replace with return list(set(items))
                        new_return = ast.Return(value=list_call)
                        
                        # Copy location info
                        ast.copy_location(new_return, node.body[-1] if node.body else node)
                        
                        # Replace function body
                        node.body = [new_return]
                        self.transformed_count += 1
                        return node
                
                # If no match, process children
                self.generic_visit(node)
                return node
        
        # Apply transformation
        transformer = SetBasedTransformer()
        result = transformer.visit(tree_copy)
        
        logger.info(f"Transformed {transformer.transformed_count} unique values implementations")
        return result


class FormatToFStringTransformer(CodeTransformer):
    """Transforms string format() calls to f-strings"""
    
    def _transform_ast(self, tree: ast.AST) -> ast.AST:
        """
        Convert string.format() calls to f-strings
        
        Args:
            tree: Abstract Syntax Tree
            
        Returns:
            Transformed AST
        """
        # Only apply for Python 3.6+
        if sys.version_info < (3, 6):
            logger.warning("f-strings require Python 3.6+, skipping this transformation")
            return tree
        
        detector = FormatToFStringDetector()
        patterns = detector._detect_in_ast(tree)
        
        if not patterns:
            return tree
        
        tree_copy = copy.deepcopy(tree)
        
        class FormatConverter(ast.NodeTransformer):
            def __init__(self):
                self.transformed_count = 0
            
            def visit_Call(self, node):
                # Process children first
                self.generic_visit(node)
                
                # Check if this is a format() call from our patterns
                for pattern in patterns:
                    if (hasattr(pattern['node'], 'lineno') and 
                        hasattr(node, 'lineno') and
                        pattern['node'].lineno == node.lineno):
                        
                        # Get format string
                        format_str = pattern['format_str']
                        
                        # We'll implement a simple conversion strategy:
                        # For positional args, replace {0}, {1}, etc. with {args[0]}, {args[1]}, etc.
                        # For keyword args, replace {name} with {name}
                        
                        # Create an f-string using the original template
                        # For a proper implementation, we'd need to parse format placeholders
                        # and replace them, but we'll use a simple prefix here
                        f_string = "f" + repr(format_str)
                        
                        # Create a literal node with the f-string value
                        new_node = RuleUtils.create_constant_node(f_string[1:-1])
                        
                        # Copy location info
                        ast.copy_location(new_node, node)
                        
                        self.transformed_count += 1
                        return new_node
                
                return node
        
        # Apply transformation
        converter = FormatConverter()
        result = converter.visit(tree_copy)
        
        logger.info(f"Converted {converter.transformed_count} format() calls to f-strings")
        return result
    
###########################################
# PART 4: Rule-Based Optimizer
###########################################

class RuleBasedOptimizer:
    """Main rule-based optimizer that coordinates detectors and transformers"""

    def __init__(self):
        """Initialize the optimizer with all detectors and transformers"""
        # Initialize pattern detectors
        self.detectors = {
            'unused_variable': UnusedVariableDetector(),
            'redundant_assignment': RedundantAssignmentDetector(),
            'range_len_loop': RangeLenLoopDetector(),
            'list_append_loop': ListAppendLoopDetector(),
            'empty_loop': EmptyLoopDetector(),
            'dead_code': DeadCodeDetector(),
            'redundant_comparison': RedundantComparisonDetector(),
            'string_concat_in_loop': StringConcatDetector(),
            'boolean_return': BooleanReturnDetector(),
            'redundant_pass': RedundantPassDetector(),
            'chained_comparison': ChainedComparisonDetector(),
            'single_use_variable': SingleUseVariableDetector(),
            'nested_if': NestedIfDetector(),
            'unused_import': UnusedImportDetector(),
            'not_not_pattern': NotNotToBoolDetector(),
            'redundant_parentheses': RedundantParenthesesDetector(),
            'inefficient_unique_values': UniqueValuesDetector(),
            'format_to_fstring': FormatToFStringDetector()
        }
        
        # Initialize code transformers
        self.transformers = {
            'unused_variable': UnusedVariableTransformer(),
            'redundant_assignment': RedundantAssignmentTransformer(),
            'range_len_loop': RangeLenLoopTransformer(),
            'list_append_loop': ListComprehensionTransformer(),
            'empty_loop': EmptyLoopTransformer(),
            'dead_code': DeadCodeTransformer(),
            'redundant_comparison': BooleanComparisonTransformer(),
            'string_concat_in_loop': StringConcatTransformer(),
            'boolean_return': BooleanReturnTransformer(),
            'redundant_pass': RedundantPassTransformer(),
            'chained_comparison': ChainedComparisonTransformer(),
            'single_use_variable': SingleUseVariableTransformer(),
            'nested_if': NestedIfCombiner(),
            'unused_import': UnusedImportTransformer(),
            'not_not_pattern': NotNotToBoolTransformer(),
            'redundant_parentheses': RedundantParenthesesTransformer(),
            'inefficient_unique_values': UniqueValuesTransformer(),
            'format_to_fstring': FormatToFStringTransformer()
        }
        
        # Map optimization types to transformers
        self.pattern_transformer_map = {
            'unused_variable': 'unused_variable',
            'redundant_assignment': 'redundant_assignment',
            'range_len_loop': 'range_len_loop',
            'list_append_loop': 'list_append_loop',
            'empty_loop': 'empty_loop',
            'dead_code': 'dead_code',
            'redundant_comparison': 'redundant_comparison',
            'string_concat_in_loop': 'string_concat_in_loop',
            'boolean_return': 'boolean_return',
            'redundant_pass': 'redundant_pass',
            'chained_comparison': 'chained_comparison',
            'single_use_variable': 'single_use_variable',
            'nested_if': 'nested_if',
            'unused_import': 'unused_import',
            'not_not_pattern': 'not_not_pattern',
            'redundant_parentheses': 'redundant_parentheses',
            'inefficient_unique_values': 'inefficient_unique_values',
            'format_to_fstring': 'format_to_fstring'
        }
        
        # Define optimization priority order
        # Order matters: some optimizations might enable or affect others
        self.optimization_order = [
            # Start with structural optimizations
            'unused_import',            # Remove imports first to clean up the code
            'dead_code',                # Remove unreachable code early
            'empty_loop',               # Remove empty loops that waste cycles
            
            # Expression simplifications
            'redundant_comparison',     # Simplify boolean expressions
            'boolean_return',           # Simplify boolean returns
            'chained_comparison',       # Convert chained equality to 'in'
            'not_not_pattern',          # Convert not not to bool()
            'redundant_parentheses',    # Remove unnecessary parentheses
            
            # Statement optimizations
            'redundant_pass',           # Remove pass statements
            'nested_if',                # Combine nested if statements
            'single_use_variable',      # Inline single-use variables
            
            # Loop and collection optimizations
            'range_len_loop',           # Simplify range(len(x)) loops
            'list_append_loop',         # Convert to list comprehensions
            'string_concat_in_loop',    # Convert to join()
            'inefficient_unique_values', # Use set() for uniqueness
            
            # Style and syntax optimizations
            'format_to_fstring',        # Convert to f-strings (Python 3.6+)
            
            # Final cleanup
            'redundant_assignment',     # Remove redundant assignments
            'unused_variable',          # Remove unused variables last
        ]
        
        # Initialize counters and tracking
        self.detection_count = 0
        self.optimization_count = 0
        self.applied_optimizations = {}  # type name -> count
        
        logger.info("RuleBasedOptimizer initialized with %d detectors and %d transformers", 
                    len(self.detectors), len(self.transformers))
    
# Add to RuleBasedOptimizer class
    def _get_patterns_for_transformer(self, transformer_name, code):
        """Get patterns for a transformer using the corresponding detector"""
        # Map transformer to detector
        detector_name = transformer_name
        if detector_name not in self.detectors:
            return []
            
        # Get the detector
        detector = self.detectors[detector_name]
        
        # Detect patterns
        try:
            return detector.detect(code)
        except Exception as e:
            logger.error(f"Error detecting patterns for {transformer_name}: {str(e)}")
            return []
    
    
    def detect_inefficient_patterns(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect inefficient patterns in code
        
        Args:
            code: Python code as string
            
        Returns:
            List of detected patterns with metadata
        """
        if not code or not code.strip():
            logger.warning("Empty or whitespace-only code provided")
            return []
            
        patterns = []
        
        # Initial parsing check
        if not parse_python_code(code):
            logger.error("Failed to parse code for pattern detection")
            return patterns
        
        # Apply each detector and collect patterns
        for name, detector in self.detectors.items():
            try:
                detected_patterns = detector.detect(code)
                for pattern in detected_patterns:
                    if 'name' not in pattern:
                        pattern['name'] = name
                patterns.extend(detected_patterns)
            except Exception as e:
                logger.error(f"Error in detector {name}: {str(e)}")
        
        self.detection_count = len(patterns)
        logger.info(f"Detected {self.detection_count} inefficient patterns")
        return patterns
    
    def optimize(self, code: str) -> Tuple[str, List[Dict[str, Any]], int]:
        """Optimize code using rule-based system"""
        # Reset counters
        self.detection_count = 0
        self.optimization_count = 0
        
        # Validate input
        if not code or not code.strip():
            return code, [], 0
        
        try:
            # Start with original code
            current_code = code
            all_patterns = []
            total_transformations = 0
            
            # Apply transformations in priority order
            for opt_type in self.optimization_order:
                transformer_name = self.pattern_transformer_map.get(opt_type)
                if not transformer_name or transformer_name not in self.transformers:
                    continue
                    
                # Get the transformer
                transformer = self.transformers[transformer_name]
                
                try:
                    # Transform the code
                    new_code = transformer.transform(current_code)
                    
                    # Check if the code was changed
                    if new_code != current_code:
                        current_code = new_code
                        total_transformations += 1
                except Exception as e:
                    logger.error(f"Error applying {transformer_name}: {str(e)}")
            
            self.optimization_count = total_transformations
            return current_code, all_patterns, total_transformations
        except Exception as e:
            logger.error(f"Error in optimize: {str(e)}")
            return code, [], 0
    
    def apply_optimization_rules(self, code: str, patterns: List[Dict[str, Any]] = None) -> str:
        """
        Apply optimization rules to code (legacy method for backward compatibility)
        
        Args:
            code: Python code as string
            patterns: Optional list of pre-detected patterns
            
        Returns:
            Optimized code as string
        """
        # Just call optimize and return the first element
        optimized_code, _, _ = self.optimize(code)
        return optimized_code
        
    def generate_optimization_report(self, patterns: List[Dict[str, Any]], 
                                     applied_optimizations: Dict[str, int] = None) -> str:
        """
        Generate a human-readable report of detected inefficiencies and optimizations
        
        Args:
            patterns: List of detected patterns
            applied_optimizations: Dict mapping optimization types to counts
            
        Returns:
            Report as string
        """
        if not patterns:
            return "No inefficient patterns detected."
        
        # Use provided optimizations or class tracking
        if applied_optimizations is None:
            applied_optimizations = self.applied_optimizations
        
        total_optimizations = sum(applied_optimizations.values())
        
        # Group patterns by type
        by_type = {}
        for pattern in patterns:
            name = pattern.get('name', 'unknown')
            if name not in by_type:
                by_type[name] = []
            by_type[name].append(pattern)
        
        # Build report
        report = [f"Detected {len(patterns)} inefficient patterns:"]
        
        # Sort pattern types by count (most frequent first)
        sorted_types = sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True)
        
        for name, patterns_list in sorted_types:
            # Get a readable name
            readable_name = name.replace('_', ' ').title()
            
            # Add if this optimization was applied
            applied_str = ""
            if name in applied_optimizations:
                applied_str = f" (✓ Fixed: {applied_optimizations[name]})"
            
            report.append(f"\n{readable_name} ({len(patterns_list)} instances){applied_str}:")
            
            # Show examples (at most 3 per type)
            for pattern in patterns_list[:3]:
                desc = pattern.get('description', 'No description')
                severity = pattern.get('severity', 'unknown')
                line = pattern.get('lineno', '?')
                report.append(f"  - Line {line}: {desc} (Severity: {severity})")
            
            if len(patterns_list) > 3:
                report.append(f"  - ... and {len(patterns_list) - 3} more instances")
        
        # Summary
        report.append(f"\nApplied {total_optimizations} optimization rules.")
        
        if applied_optimizations:
            report.append("\nOptimizations by type:")
            # Sort by count (most frequent first)
            sorted_opts = sorted(applied_optimizations.items(), key=lambda x: x[1], reverse=True)
            for opt_type, count in sorted_opts:
                readable_name = opt_type.replace('_', ' ').title()
                report.append(f"  - {readable_name}: {count}")
        
        return "\n".join(report)


###########################################
# PART 5: Public API and Utility Functions
###########################################

def detect_inefficient_patterns(code: str) -> List[Dict[str, Any]]:
    """
    Detect inefficient patterns in code (standalone function)
    
    Args:
        code: Python code as string
            
    Returns:
        List of detected patterns with metadata
    """
    optimizer = RuleBasedOptimizer()
    return optimizer.detect_inefficient_patterns(code)


def apply_optimization_rules(code: str, patterns: List[Dict[str, Any]] = None) -> str:
    """
    Apply rule-based optimizations to Python code
    
    Args:
        code: Python code as string
        patterns: Optional pre-detected patterns
        
    Returns:
        Optimized code
    """
    optimizer = RuleBasedOptimizer()
    return optimizer.apply_optimization_rules(code, patterns)


def optimize_code(code: str) -> Tuple[str, List[Dict[str, Any]], Dict[str, int]]:
    """
    Optimize code using rule-based system (main entry point)
    
    Args:
        code: Python code as string
        
    Returns:
        Tuple of (optimized_code, detected_patterns, optimization_counts)
    """
    optimizer = RuleBasedOptimizer()
    return optimizer.optimize(code)


def format_optimization_report(patterns: List[Dict[str, Any]], 
                              optimization_stats: Dict[str, int]) -> str:
    """
    Format a human-readable report of optimizations
    
    Args:
        patterns: List of detected patterns
        optimization_stats: Dict mapping optimization types to counts
        
    Returns:
        Formatted report string
    """
    optimizer = RuleBasedOptimizer()
    return optimizer.generate_optimization_report(patterns, optimization_stats)


def compare_code(original: str, optimized: str) -> str:
    """
    Generate a diff comparing original and optimized code
    
    Args:
        original: Original code
        optimized: Optimized code
        
    Returns:
        Diff as string
    """
    import difflib
    
    # Generate diff
    original_lines = original.splitlines()
    optimized_lines = optimized.splitlines()
    
    diff = difflib.unified_diff(
        original_lines,
        optimized_lines,
        fromfile='original',
        tofile='optimized',
        lineterm=''
    )
    
    return '\n'.join(diff)


def main():
    """
    Main function for command-line usage
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='EFFICODE-ACRR Rule-Based Code Optimizer')
    parser.add_argument('input_file', help='Python file to optimize')
    parser.add_argument('-o', '--output', help='Output file (defaults to stdout)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed optimization info')
    parser.add_argument('-r', '--report', action='store_true', help='Generate optimization report')
    parser.add_argument('-d', '--diff', action='store_true', help='Show diff of changes')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )
    
    try:
        # Read input file
        with open(args.input_file, 'r') as f:
            code = f.read()
        
        # Optimize code
        optimized_code, patterns, optimization_stats = optimize_code(code)
        
        # Generate report if requested
        if args.report or args.verbose:
            report = format_optimization_report(patterns, optimization_stats)
            print(report)
            print()
        
        # Show diff if requested
        if args.diff and optimized_code != code:
            diff = compare_code(code, optimized_code)
            print(diff)
            print()
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(optimized_code)
            print(f"Optimized code written to {args.output}")
        else:
            print(optimized_code)
        
        return 0
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())