"""
Rule-Based Optimization Module for EFFICODE-ACRR

This module implements general rule-based code optimization strategies:
- Dead code elimination and unreachable code removal
- Unused variable and function removal
- Loop optimizations (redundant loops, loop merging)
- Conditional simplification and redundant conditionals removal
- Function inlining for small functions
- Memory usage optimization
- String concatenation optimization

These optimizations are applied using AST transformations to improve
code efficiency without changing its functionality.
"""

import ast
import re
import copy
import logging
from typing import Dict, List, Tuple, Set, Optional, Union, Any
from dataclasses import dataclass
import astor  # Required for AST to code conversion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dataclasses for optimization results
@dataclass
class OptimizationChange:
    """Record of a single optimization change."""
    description: str
    line_start: int
    line_end: int
    original_code: str
    optimized_code: str


@dataclass
class OptimizationResult:
    """Comprehensive result of code optimization."""
    original_code: str
    optimized_code: Optional[str]
    changes_made: List[str]
    detailed_changes: List[OptimizationChange]
    success: bool
    error: Optional[str]
    performance_impact: Dict[str, float] = None


class OptimizerConfig:
    """Configuration for the rule-based optimizer."""
    
    def __init__(self, 
                optimization_level: str = "medium",
                preserve_names: bool = True,
                preserve_comments: bool = True,
                inline_threshold: int = 3,
                enabled_optimizations: List[str] = None):
        """
        Initialize the optimizer configuration.
        
        Args:
            optimization_level: "low", "medium", or "aggressive"
            preserve_names: Whether to preserve variable/function names
            preserve_comments: Whether to preserve comments
            inline_threshold: Max line count for function inlining
            enabled_optimizations: List of specific optimizations to enable
        """
        self.optimization_level = optimization_level
        self.preserve_names = preserve_names
        self.preserve_comments = preserve_comments
        self.inline_threshold = inline_threshold
        
        # Default enabled optimizations
        self.enabled_optimizations = enabled_optimizations or [
            "dead_code", 
            "unused_code", 
            "unreachable_code",
            "constant_folding", 
            "redundant_code", 
            "conditional_simplification", 
            "function_inlining",
            "memory_optimization",
            "redundant_conditionals",
            "redundant_returns",
            "string_optimization"
        ]
        
        # Set threshold values based on optimization level
        if optimization_level == "low":
            self.inline_threshold = 2
        elif optimization_level == "aggressive":
            self.inline_threshold = 5
            
    def is_enabled(self, optimization: str) -> bool:
        """Check if a specific optimization is enabled."""
        return optimization in self.enabled_optimizations


class RuleBasedOptimizer:
    """Rule-based code optimizer using general optimization techniques."""
    
    def __init__(self, config: OptimizerConfig = None):
        """
        Initialize the optimizer with configuration.
        
        Args:
            config: Optimizer configuration, default if None
        """
        self.config = config or OptimizerConfig()
        
        # Initialize transformers
        self._init_transformers()

    def optimize(self, code: str) -> OptimizationResult:
        """
        Optimize code using rule-based transformations.
        
        Args:
            code: Source code to optimize
            
        Returns:
            OptimizationResult: Comprehensive optimization result
        """
        if not isinstance(code, str) or not code.strip():
            return OptimizationResult(
                original_code=code,
                optimized_code=None,
                changes_made=[],
                detailed_changes=[],
                success=False,
                error="Invalid input code"
            )
            
        try:
            # Make backup of original code
            original_code = code
            
            # Clean code while preserving comments if configured
            cleaned_code = self._clean_code(code)
            if not cleaned_code:
                return OptimizationResult(
                    original_code=original_code,
                    optimized_code=None,
                    changes_made=[],
                    detailed_changes=[],
                    success=False,
                    error="Code cleaning failed"
                )

            # Validate syntax
            if not self._validate_syntax(cleaned_code):
                return OptimizationResult(
                    original_code=original_code,
                    optimized_code=None,
                    changes_made=[],
                    detailed_changes=[],
                    success=False,
                    error="Invalid Python syntax"
                )

            # Start tracking changes
            all_changes = []
            detailed_changes = []
            optimized_code = cleaned_code
            performance_impact = {
                "time_complexity": 0.0,
                "space_complexity": 0.0,
                "optimizations_applied": 0
            }

            # Parse the code into an AST for general optimizations
            try:
                tree = ast.parse(optimized_code)
            except Exception as e:
                logger.error(f"Failed to parse code: {str(e)}")
                return OptimizationResult(
                    original_code=original_code,
                    optimized_code=cleaned_code,
                    changes_made=all_changes,
                    detailed_changes=detailed_changes,
                    success=True,
                    error=f"AST parsing failed: {str(e)}"
                )

            # Apply general optimizations in sequence
            try:
                optimized_tree, general_changes, general_detailed_changes = self._apply_all_optimizations(tree, optimized_code)
                all_changes.extend(general_changes)
                detailed_changes.extend(general_detailed_changes)
                
                # Unparse tree back to code
                optimized_code = astor.to_source(optimized_tree)
            except Exception as e:
                logger.warning(f"General optimization failed: {str(e)}")
                # Fall back to the cleaned code
                optimized_code = cleaned_code
            
            # Final validation
            if not self._validate_syntax(optimized_code):
                logger.warning("Optimized code failed validation, reverting to original")
                return OptimizationResult(
                    original_code=original_code,
                    optimized_code=cleaned_code,
                    changes_made=["Optimization reverted due to validation failure"],
                    detailed_changes=[],
                    success=True,
                    error="Generated code failed validation"
                )
                
            # Check if optimizations actually improved the code
            if optimized_code == original_code:
                all_changes.append("No effective changes were made")

            # Calculate performance impact (approximate)
            performance_impact["optimizations_applied"] = len(all_changes)
            
            return OptimizationResult(
                original_code=original_code,
                optimized_code=optimized_code,
                changes_made=all_changes,
                detailed_changes=detailed_changes,
                success=True,
                error=None,
                performance_impact=performance_impact
            )

        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            return OptimizationResult(
                original_code=original_code,
                optimized_code=None,
                changes_made=[],
                detailed_changes=[],
                success=False,
                error=str(e)
            )

    def _clean_code(self, code: str) -> Optional[str]:
        """Clean and normalize code while preserving comments if needed."""
        if not isinstance(code, str) or not code.strip():
            return None

        try:
            # Remove BOM and normalize line endings
            code = code.replace('\ufeff', '')
            code = code.replace('\r\n', '\n').replace('\r', '\n')

            if not self.config.preserve_comments:
                # Remove comments and empty lines
                lines = []
                for line in code.splitlines():
                    line = re.sub(r'#.*$', '', line)
                    if line.strip():
                        lines.append(line)
                code = '\n'.join(lines)
            
            # Normalize whitespace (but preserve indentation)
            lines = code.splitlines()
            code = '\n'.join(line.rstrip() for line in lines)
            
            return code.strip()

        except Exception as e:
            logger.error(f"Code cleaning failed: {str(e)}")
            return None

    def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return True
        except Exception as e:
            logger.error(f"Syntax validation failed: {str(e)}")
            return False

    def _apply_all_optimizations(self, tree: ast.AST, source_code: str) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """
        Apply all enabled optimizations to the AST.
        
        Args:
            tree: AST to optimize
            source_code: Original source code for reference
            
        Returns:
            Tuple of (optimized_tree, changes, detailed_changes)
        """
        changes = []
        detailed_changes = []
        
        # Store original AST for comparison
        original_tree = copy.deepcopy(tree)
        
        # Apply optimizations in the most effective order
        optimization_sequence = [
            # First phase: Analysis and simplification
            ("dead_code", self._dead_code_elimination),
            ("unused_code", self._unused_code_removal),
            ("unreachable_code", self._unreachable_code_removal),
            ("constant_folding", self._constant_folding),
            
            # Second phase: Structural optimizations
            ("conditional_simplification", self._simplify_conditionals),
            ("redundant_conditionals", self._remove_redundant_conditionals),
            ("redundant_code", self._remove_redundancies),
            ("redundant_returns", self._remove_redundant_returns),
            
            # Third phase: Function optimizations
            ("function_inlining", self._inline_functions),
            
            # Fourth phase: Memory and advanced optimizations
            ("memory_optimization", self._optimize_memory),
            ("string_optimization", self._optimize_string_concat)
        ]
        
        # Apply each optimization if enabled
        for opt_name, opt_func in optimization_sequence:
            if self.config.is_enabled(opt_name):
                try:
                    # Get source lines as they currently are
                    current_source = astor.to_source(tree)
                    
                    # Apply the optimization
                    tree, opt_changes, opt_detailed = opt_func(tree)
                    
                    if opt_changes:
                        changes.extend(opt_changes)
                        detailed_changes.extend(opt_detailed)
                        
                        # Validate the tree after each transformation
                        try:
                            test_code = astor.to_source(tree)
                            ast.parse(test_code)  # Attempt to parse to validate
                        except Exception as e:
                            # Revert this optimization if it produced invalid code
                            logger.warning(f"Optimization {opt_name} produced invalid code: {str(e)}")
                            tree = ast.parse(current_source)  # Revert to previous valid state
                            if changes and changes[-1].startswith(opt_name):
                                changes.pop()  # Remove the failed optimization from changes
                except Exception as e:
                    logger.warning(f"Error during {opt_name}: {str(e)}")
        
        return tree, changes, detailed_changes

    def _init_transformers(self):
        """Initialize all AST transformer classes."""
        
        # Dead Code Elimination Transformer
        class DeadCodeEliminator(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_If(self, node):
                # Check for constant conditions
                if isinstance(node.test, ast.Constant):
                    if node.test.value:  # True condition
                        self.changes.append("Removed dead 'else' branch")
                        change = OptimizationChange(
                            description="Removed unreachable 'else' branch",
                            line_start=node.lineno,
                            line_end=getattr(node.orelse[-1], 'end_lineno', node.lineno) if node.orelse else node.lineno,
                            original_code=astor.to_source(node),
                            optimized_code=astor.to_source(ast.If(node.test, node.body, []))
                        )
                        self.detailed_changes.append(change)
                        return ast.If(node.test, self.generic_visit_list(node.body), [])
                    else:  # False condition
                        if node.orelse:
                            self.changes.append("Removed dead 'if' branch")
                            change = OptimizationChange(
                                description="Removed unreachable 'if' branch",
                                line_start=node.lineno,
                                line_end=getattr(node.orelse[-1], 'end_lineno', node.lineno),
                                original_code=astor.to_source(node),
                                optimized_code=astor.to_source(ast.Module(node.orelse, type_ignores=[]))
                            )
                            self.detailed_changes.append(change)
                            return self.generic_visit_list(node.orelse)
                        else:
                            self.changes.append("Removed dead 'if' statement")
                            return None  # Remove the if statement entirely

                # Process normally
                self.generic_visit(node)
                return node
                
            def visit_While(self, node):
                # Check for constant conditions
                if isinstance(node.test, ast.Constant):
                    if not node.test.value:  # False condition
                        self.changes.append("Removed dead 'while' loop")
                        return None  # Remove the while loop entirely
                
                # Process normally
                self.generic_visit(node)
                return node
                
            def visit_Return(self, node):
                # No need to process further statements after a return
                return node
                
            def generic_visit_list(self, nodes):
                """Visit a list of nodes and handle returns."""
                result = []
                for i, node in enumerate(nodes):
                    # Skip processing after a return/break/continue
                    if i > 0 and isinstance(nodes[i-1], (ast.Return, ast.Break, ast.Continue)):
                        self.changes.append("Removed unreachable code after control flow statement")
                        break
                    
                    visited = self.visit(node)
                    if visited is not None:
                        if isinstance(visited, list):
                            result.extend(visited)
                        else:
                            result.append(visited)
                return result
                
            def visit_Module(self, node):
                node.body = self.generic_visit_list(node.body)
                return node
                
            def visit_FunctionDef(self, node):
                node.body = self.generic_visit_list(node.body)
                return node
        
        # Store the transformers as attributes
        self.dead_code_eliminator = DeadCodeEliminator

        # Unreachable Code Removal Transformer
        class UnreachableCodeRemover(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_Module(self, node):
                node.body = self._process_body(node.body)
                return node
                
            def visit_FunctionDef(self, node):
                node.body = self._process_body(node.body)
                return node
                
            def visit_ClassDef(self, node):
                node.body = self._process_body(node.body)
                return node
                
            def visit_If(self, node):
                node.body = self._process_body(node.body)
                node.orelse = self._process_body(node.orelse)
                return node
                
            def visit_For(self, node):
                node.body = self._process_body(node.body)
                node.orelse = self._process_body(node.orelse)
                return node
                
            def visit_While(self, node):
                node.body = self._process_body(node.body)
                node.orelse = self._process_body(node.orelse)
                return node
                
            def visit_Try(self, node):
                node.body = self._process_body(node.body)
                node.orelse = self._process_body(node.orelse)
                node.finalbody = self._process_body(node.finalbody)
                for handler in node.handlers:
                    handler.body = self._process_body(handler.body)
                return node
                
            def _process_body(self, body):
                """Process a list of statements, removing unreachable code."""
                if not body:
                    return body
                    
                result = []
                has_return = False
                has_break = False
                has_continue = False
                
                for i, node in enumerate(body):
                    if has_return or has_break or has_continue:
                        # This node is unreachable
                        self.changes.append("Removed unreachable code after control flow statement")
                        description = f"Removed unreachable code after {'return' if has_return else 'break' if has_break else 'continue'}"
                        
                        # Get the original code snippet
                        try:
                            original_code = astor.to_source(ast.Module(body[i:], type_ignores=[]))
                        except:
                            original_code = "# Unreachable code"
                            
                        change = OptimizationChange(
                            description=description,
                            line_start=getattr(node, 'lineno', 0),
                            line_end=getattr(node, 'end_lineno', 0),
                            original_code=original_code,
                            optimized_code="# Removed unreachable code"
                        )
                        self.detailed_changes.append(change)
                        break
                    
                    # Add this node to the result
                    result.append(self.visit(node))
                    
                    # Check if this is a control flow statement that makes the next statements unreachable
                    if isinstance(node, ast.Return):
                        has_return = True
                    elif isinstance(node, ast.Break):
                        has_break = True
                    elif isinstance(node, ast.Continue):
                        has_continue = True
                    elif isinstance(node, ast.Raise):
                        # In most cases, raise makes the following code unreachable
                        # but there can be try-except blocks, so this is a simple approximation
                        has_return = True
                        
                return result
                
        self.unreachable_code_remover = UnreachableCodeRemover

    def _dead_code_elimination(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """
        Eliminate dead code from the AST.
        
        Args:
            tree: AST to optimize
            
        Returns:
            Tuple of (optimized_tree, changes, detailed_changes)
        """
        eliminator = self.dead_code_eliminator()
        optimized_tree = eliminator.visit(copy.deepcopy(tree))
        
        return optimized_tree, eliminator.changes, eliminator.detailed_changes
        
    def _unreachable_code_removal(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """
        Remove unreachable code after return, break, or continue statements.
        
        Args:
            tree: AST to optimize
            
        Returns:
            Tuple of (optimized_tree, changes, detailed_changes)
        """
        remover = self.unreachable_code_remover()
        optimized_tree = remover.visit(copy.deepcopy(tree))
        
        return optimized_tree, remover.changes, remover.detailed_changes
        
    def _unused_code_removal(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Remove unused variables, imports, and functions."""
        # Implement unused variable detection
        class UnusedVariableFinder(ast.NodeVisitor):
            def __init__(self):
                self.defined = set()
                self.used = set()
                self.current_scope = []
                self.functions = set()
                self.called_functions = set()
                self.imports = set()
                self.used_imports = set()
                self.imported_modules = set()
                self.used_modules = set()
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    # Variable definition
                    self.defined.add((node.id, tuple(self.current_scope)))
                elif isinstance(node.ctx, ast.Load):
                    # Variable usage
                    self.used.add((node.id, tuple(self.current_scope)))
                    # Also mark as used in parent scopes
                    for i in range(len(self.current_scope)):
                        self.used.add((node.id, tuple(self.current_scope[:i])))
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                # Track function definitions
                self.functions.add(node.name)
                prev_scope = self.current_scope
                self.current_scope = self.current_scope + [node.name]
                self.generic_visit(node)
                self.current_scope = prev_scope
                
            def visit_ClassDef(self, node):
                # Track class definitions similar to functions
                prev_scope = self.current_scope
                self.current_scope = self.current_scope + [node.name]
                self.generic_visit(node)
                self.current_scope = prev_scope
                
            def visit_Call(self, node):
                # Track function calls
                if isinstance(node.func, ast.Name):
                    self.called_functions.add(node.func.id)
                elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    # Record module usage for import tracking
                    self.used_modules.add(node.func.value.id)
                self.generic_visit(node)
                
            def visit_Import(self, node):
                # Track imports
                for name in node.names:
                    if name.asname:
                        self.imports.add(name.asname)
                        self.imported_modules.add(name.asname)
                    else:
                        self.imports.add(name.name)
                        self.imported_modules.add(name.name)
                self.generic_visit(node)
                
            def visit_ImportFrom(self, node):
                # Track from imports
                if node.module:
                    for name in node.names:
                        if name.name == '*':
                            # Wildcard imports are hard to track, consider everything as used
                            continue
                        imported_name = name.asname if name.asname else name.name
                        self.imports.add(imported_name)
                self.generic_visit(node)
                
            def visit_Attribute(self, node):
                # Track attribute access for import tracking
                if isinstance(node.value, ast.Name):
                    self.used_modules.add(node.value.id)
                self.generic_visit(node)
                
            def get_unused_variables(self):
                """Get variables that are defined but not used."""
                return self.defined - self.used
                
            def get_unused_functions(self):
                """Get functions that are defined but not called."""
                # Don't include "main" function as unused, since it might be an entry point
                main_funcs = {"main", "__main__"}
                return self.functions - self.called_functions - main_funcs
                
            def get_unused_imports(self):
                """Get imports that are not used."""
                # Modules might be used via attributes
                active_modules = self.used_modules
                return self.imports - self.used - active_modules
        
        # Create a transformer to remove unused code
        class UnusedCodeRemover(ast.NodeTransformer):
            def __init__(self, unused_vars, unused_funcs, unused_imports):
                self.unused_vars = unused_vars
                self.unused_funcs = unused_funcs
                self.unused_imports = unused_imports
                self.changes = []
                self.detailed_changes = []
                self.current_scope = []
                
            def visit_Assign(self, node):
                # Check if all targets are unused variables
                all_unused = all(
                    isinstance(target, ast.Name) and 
                    (target.id, tuple(self.current_scope)) in self.unused_vars
                    for target in node.targets
                )
                
                if all_unused:
                    # Remove assignment if all targets are unused
                    self.changes.append(f"Removed unused variable assignment")
                    return None
                    
                return self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                # Check if function is unused
                if node.name in self.unused_funcs:
                    self.changes.append(f"Removed unused function {node.name}")
                    return None
                    
                # Process function body
                prev_scope = self.current_scope
                self.current_scope = self.current_scope + [node.name]
                self.generic_visit(node)
                self.current_scope = prev_scope
                return node
                
            def visit_Import(self, node):
                # Filter out unused imports
                new_names = []
                for name in node.names:
                    module_name = name.asname if name.asname else name.name
                    if module_name not in self.unused_imports:
                        new_names.append(name)
                    else:
                        self.changes.append(f"Removed unused import {module_name}")
                
                if not new_names:
                    return None
                    
                node.names = new_names
                return node
                
            def visit_ImportFrom(self, node):
                # Filter out unused from imports
                new_names = []
                for name in node.names:
                    if name.name == '*':
                        # Don't remove wildcard imports
                        new_names.append(name)
                        continue
                        
                    import_name = name.asname if name.asname else name.name
                    if import_name not in self.unused_imports:
                        new_names.append(name)
                    else:
                        self.changes.append(f"Removed unused import {import_name}")
                
                if not new_names:
                    return None
                    
                node.names = new_names
                return node
        
        # Find unused code
        finder = UnusedVariableFinder()
        finder.visit(tree)
        
        unused_vars = finder.get_unused_variables()
        unused_funcs = finder.get_unused_functions()
        unused_imports = finder.get_unused_imports()
        
        # Remove unused code
        remover = UnusedCodeRemover(unused_vars, unused_funcs, unused_imports)
        optimized_tree = remover.visit(copy.deepcopy(tree))
        
        return optimized_tree, remover.changes, remover.detailed_changes
    
    def _constant_folding(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Perform constant folding and propagation."""
        class ConstantFolder(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                self.constants = {}  # Maps variable names to constant values
                self.scope_stack = []  # Stack of scopes for constant tracking
                self.scope_constants = [{}]  # Constants for each scope
                
            def visit_Module(self, node):
                self.scope_stack.append('module')
                self.scope_constants.append({})
                result = self.generic_visit(node)
                self.scope_stack.pop()
                self.scope_constants.pop()
                return result
                
            def visit_FunctionDef(self, node):
                # Enter a new scope
                self.scope_stack.append(node.name)
                self.scope_constants.append({})
                # Process the function body
                new_node = ast.FunctionDef(
                    name=node.name,
                    args=node.args,
                    body=[self.visit(stmt) for stmt in node.body],
                    decorator_list=node.decorator_list,
                    returns=node.returns
                )
                # Exit the scope
                self.scope_stack.pop()
                self.scope_constants.pop()
                return new_node
                
            def visit_BinOp(self, node):
                # Visit operands first
                self.generic_visit(node)
                
                # If both operands are constants, compute the result
                if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
                    try:
                        # Compute the operation
                        if isinstance(node.op, ast.Add):
                            result = node.left.value + node.right.value
                        elif isinstance(node.op, ast.Sub):
                            result = node.left.value - node.right.value
                        elif isinstance(node.op, ast.Mult):
                            result = node.left.value * node.right.value
                        elif isinstance(node.op, ast.Div):
                            result = node.left.value / node.right.value
                        elif isinstance(node.op, ast.FloorDiv):
                            result = node.left.value // node.right.value
                        elif isinstance(node.op, ast.Mod):
                            result = node.left.value % node.right.value
                        elif isinstance(node.op, ast.Pow):
                            result = node.left.value ** node.right.value
                        elif isinstance(node.op, ast.LShift):
                            result = node.left.value << node.right.value
                        elif isinstance(node.op, ast.RShift):
                            result = node.left.value >> node.right.value
                        elif isinstance(node.op, ast.BitOr):
                            result = node.left.value | node.right.value
                        elif isinstance(node.op, ast.BitXor):
                            result = node.left.value ^ node.right.value
                        elif isinstance(node.op, ast.BitAnd):
                            result = node.left.value & node.right.value
                        else:
                            return node  # Unsupported operation
                            
                        self.changes.append("Constant folding applied")
                        
                        # Create change record
                        change = OptimizationChange(
                            description=f"Constant folding: {node.left.value} op {node.right.value} -> {result}",
                            line_start=getattr(node, 'lineno', 0),
                            line_end=getattr(node, 'end_lineno', 0),
                            original_code=astor.to_source(node),
                            optimized_code=str(result)
                        )
                        self.detailed_changes.append(change)
                        
                        return ast.Constant(value=result)
                    except Exception as e:
                        # Operation failed (e.g., division by zero)
                        return node
                        
                return node
                
            def visit_Assign(self, node):
                # Visit right side first
                node.value = self.visit(node.value)
                
                # If right side is a constant, track it for propagation
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant):
                    var_name = node.targets[0].id
                    self.scope_constants[-1][var_name] = node.value.value
                    
                return node
                
            def visit_Name(self, node):
                # Replace variable references with known constants
                if isinstance(node.ctx, ast.Load):
                    # Check current scope first, then outer scopes
                    for scope in reversed(self.scope_constants):
                        if node.id in scope:
                            self.changes.append(f"Propagated constant for {node.id}")
                            
                            # Create change record
                            change = OptimizationChange(
                                description=f"Constant propagation: {node.id} -> {scope[node.id]}",
                                line_start=getattr(node, 'lineno', 0),
                                line_end=getattr(node, 'end_lineno', 0),
                                original_code=node.id,
                                optimized_code=str(scope[node.id])
                            )
                            self.detailed_changes.append(change)
                            
                            return ast.Constant(value=scope[node.id])
                    
                return node
                
            def visit_UnaryOp(self, node):
                # Process operand first
                node.operand = self.visit(node.operand)
                
                # Compute constant unary operations
                if isinstance(node.operand, ast.Constant):
                    try:
                        if isinstance(node.op, ast.UAdd):
                            result = +node.operand.value
                        elif isinstance(node.op, ast.USub):
                            result = -node.operand.value
                        elif isinstance(node.op, ast.Not):
                            result = not node.operand.value
                        elif isinstance(node.op, ast.Invert):
                            result = ~node.operand.value
                        else:
                            return node  # Unsupported operation
                            
                        self.changes.append("Constant folding applied to unary operation")
                        return ast.Constant(value=result)
                    except:
                        # Operation failed
                        return node
                
                return node
                
            def visit_Compare(self, node):
                # Process left side and comparators
                node.left = self.visit(node.left)
                node.comparators = [self.visit(comparator) for comparator in node.comparators]
                
                # If all values are constants, compute the result
                if isinstance(node.left, ast.Constant) and all(isinstance(comp, ast.Constant) for comp in node.comparators):
                    try:
                        # Save the left value
                        left_val = node.left.value
                        result = True
                        
                        # Process each comparison operation in sequence
                        for i, (op, right_val) in enumerate(zip(node.ops, node.comparators)):
                            right_val = right_val.value
                            
                            # Perform the comparison
                            if isinstance(op, ast.Eq):
                                result = result and (left_val == right_val)
                            elif isinstance(op, ast.NotEq):
                                result = result and (left_val != right_val)
                            elif isinstance(op, ast.Lt):
                                result = result and (left_val < right_val)
                            elif isinstance(op, ast.LtE):
                                result = result and (left_val <= right_val)
                            elif isinstance(op, ast.Gt):
                                result = result and (left_val > right_val)
                            elif isinstance(op, ast.GtE):
                                result = result and (left_val >= right_val)
                            elif isinstance(op, ast.Is):
                                result = result and (left_val is right_val)
                            elif isinstance(op, ast.IsNot):
                                result = result and (left_val is not right_val)
                            elif isinstance(op, ast.In):
                                result = result and (left_val in right_val)
                            elif isinstance(op, ast.NotIn):
                                result = result and (left_val not in right_val)
                            else:
                                # Unsupported operation
                                return node
                                
                            # For chained comparison (a < b < c), left_val becomes the right_val
                            left_val = right_val
                            
                            # Short-circuit if we know the result is False
                            if not result:
                                break
                                
                        self.changes.append("Constant folding applied to comparison")
                        return ast.Constant(value=result)
                    except:
                        # Operation failed
                        return node
                    
                return node
        
        # Apply constant folding
        folder = ConstantFolder()
        optimized_tree = folder.visit(copy.deepcopy(tree))
        
        return optimized_tree, folder.changes, folder.detailed_changes
    
    def _simplify_conditionals(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Simplify conditional expressions and nested if statements."""
        class ConditionalSimplifier(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_If(self, node):
                # Process children first
                self.generic_visit(node)
                
                # Simplify boolean expressions
                if isinstance(node.test, ast.Compare):
                    # Simplify comparisons like "if x == True" to "if x"
                    if (len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq) and
                            isinstance(node.test.comparators[0], ast.Constant) and 
                            node.test.comparators[0].value is True):
                        
                        self.changes.append("Simplified 'if x == True' to 'if x'")
                        
                        # Create change record
                        change = OptimizationChange(
                            description="Simplified comparison with True constant",
                            line_start=getattr(node, 'lineno', 0),
                            line_end=getattr(node, 'end_lineno', 0),
                            original_code=astor.to_source(node.test),
                            optimized_code=astor.to_source(node.test.left)
                        )
                        self.detailed_changes.append(change)
                        
                        node.test = node.test.left
                        
                    # Simplify comparisons like "if x == False" to "if not x"
                    elif (len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq) and
                          isinstance(node.test.comparators[0], ast.Constant) and 
                          node.test.comparators[0].value is False):
                        
                        self.changes.append("Simplified 'if x == False' to 'if not x'")
                        
                        # Create change record
                        change = OptimizationChange(
                            description="Simplified comparison with False constant",
                            line_start=getattr(node, 'lineno', 0),
                            line_end=getattr(node, 'end_lineno', 0),
                            original_code=astor.to_source(node.test),
                            optimized_code=f"not {astor.to_source(node.test.left).strip()}"
                        )
                        self.detailed_changes.append(change)
                        
                        node.test = ast.UnaryOp(op=ast.Not(), operand=node.test.left)
                
                # Simplify nested if-statements with no else clauses
                if (len(node.body) == 1 and isinstance(node.body[0], ast.If) and 
                    not node.orelse and not node.body[0].orelse):
                    
                    inner_if = node.body[0]
                    # Combine conditions: if a: if b: c ==> if a and b: c
                    combined_test = ast.BoolOp(
                        op=ast.And(),
                        values=[node.test, inner_if.test]
                    )
                    
                    self.changes.append("Combined nested if statements with AND")
                    
                    # Create change record
                    change = OptimizationChange(
                        description="Combined nested if statements",
                        line_start=getattr(node, 'lineno', 0),
                        line_end=getattr(inner_if, 'end_lineno', 0),
                        original_code=astor.to_source(node),
                        optimized_code=f"if {astor.to_source(node.test).strip()} and {astor.to_source(inner_if.test).strip()}:\n    # Combined nested conditionals"
                    )
                    self.detailed_changes.append(change)
                    
                    return ast.If(
                        test=combined_test,
                        body=inner_if.body,
                        orelse=[]
                    )
                    
                return node
                
            def visit_BoolOp(self, node):
                # Process children first
                self.generic_visit(node)
                
                # Simplify redundant boolean operations
                if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
                    # Remove duplicate conditions
                    unique_values = []
                    seen = set()
                    
                    for value in node.values:
                        value_str = ast.dump(value)
                        if value_str not in seen:
                            unique_values.append(value)
                            seen.add(value_str)
                    
                    if len(unique_values) < len(node.values):
                        self.changes.append("Removed duplicate conditions in boolean expression")
                        
                        # Create change record
                        change = OptimizationChange(
                            description="Removed duplicate conditions",
                            line_start=getattr(node, 'lineno', 0),
                            line_end=getattr(node, 'end_lineno', 0),
                            original_code=astor.to_source(node),
                            optimized_code="# Removed duplicate conditions"
                        )
                        self.detailed_changes.append(change)
                        
                        node.values = unique_values
                
                return node
                
            def visit_UnaryOp(self, node):
                # Process operand first
                self.generic_visit(node)
                
                # Simplify double negation: not (not x) => x
                if isinstance(node.op, ast.Not) and isinstance(node.operand, ast.UnaryOp) and isinstance(node.operand.op, ast.Not):
                    self.changes.append("Removed double negation")
                    
                    # Create change record
                    change = OptimizationChange(
                        description="Removed double negation",
                        line_start=getattr(node, 'lineno', 0),
                        line_end=getattr(node, 'end_lineno', 0),
                        original_code=astor.to_source(node),
                        optimized_code=astor.to_source(node.operand.operand)
                    )
                    self.detailed_changes.append(change)
                    
                    return node.operand.operand
                    
                return node
        
        # Apply conditional simplification
        simplifier = ConditionalSimplifier()
        optimized_tree = simplifier.visit(copy.deepcopy(tree))
        
        return optimized_tree, simplifier.changes, simplifier.detailed_changes
    
    def _remove_redundant_conditionals(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Remove redundant conditional statements and simplify if-else chains."""
        class RedundantConditionalRemover(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_If(self, node):
                # Process nested conditions first
                self.generic_visit(node)
                
                # Check for identical if/else branches
                if (node.orelse and len(node.body) == len(node.orelse) and
                    all(ast.dump(node.body[i]) == ast.dump(node.orelse[i]) for i in range(len(node.body)))):
                    
                    self.changes.append("Removed redundant conditional with identical branches")
                    
                    # Create change record
                    change = OptimizationChange(
                        description="Removed if/else with identical branches",
                        line_start=getattr(node, 'lineno', 0),
                        line_end=getattr(node, 'end_lineno', 0) if hasattr(node, 'end_lineno') else 0,
                        original_code=astor.to_source(node),
                        optimized_code="# Removed redundant if/else with identical branches"
                    )
                    self.detailed_changes.append(change)
                    
                    # Just return the body statements since both branches are identical
                    return node.body
                
                # Check for empty branches
                if not node.body:
                    if not node.orelse:
                        # If both branches are empty, remove the entire if statement
                        self.changes.append("Removed empty if statement")
                        return None
                    else:
                        # If the if branch is empty, negate the condition and use the else branch
                        self.changes.append("Simplified if-else with empty if branch")
                        negated_test = ast.UnaryOp(op=ast.Not(), operand=node.test)
                        return ast.If(test=negated_test, body=node.orelse, orelse=[])
                elif not node.orelse:
                    # If the else branch is empty, keep the if as is
                    return node
                
                return node
                
            def visit_BoolOp(self, node):
                # Process operands first
                self.generic_visit(node)
                
                # Check for redundant boolean operations
                if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
                    # Remove duplicate operands
                    unique_values = []
                    seen_dumps = set()
                    
                    for value in node.values:
                        dump = ast.dump(value)
                        if dump not in seen_dumps:
                            unique_values.append(value)
                            seen_dumps.add(dump)
                    
                    if len(unique_values) < len(node.values):
                        self.changes.append("Removed duplicate conditions in boolean expression")
                        
                        if len(unique_values) == 1:
                            # If only one unique value left, return it directly
                            return unique_values[0]
                        
                        node.values = unique_values
                
                return node
        
        # Apply redundant conditional removal
        remover = RedundantConditionalRemover()
        optimized_tree = remover.visit(copy.deepcopy(tree))
        
        return optimized_tree, remover.changes, remover.detailed_changes
    
    def _remove_redundancies(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Remove redundant code patterns and expressions."""
        class RedundancyRemover(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_Expr(self, node):
                # Remove no-op expressions like string literals that aren't docstrings
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    # Keep only if it could be a docstring
                    parent = getattr(node, 'parent', None)
                    is_docstring = (parent and isinstance(parent, (ast.Module, ast.ClassDef, ast.FunctionDef)) and 
                                   parent.body and parent.body[0] is node)
                    if not is_docstring:
                        self.changes.append("Removed standalone string literal")
                        
                        # Create change record
                        change = OptimizationChange(
                            description="Removed unused string literal",
                            line_start=getattr(node, 'lineno', 0),
                            line_end=getattr(node, 'end_lineno', 0) if hasattr(node, 'end_lineno') else 0,
                            original_code=astor.to_source(node),
                            optimized_code="# Removed unused string literal"
                        )
                        self.detailed_changes.append(change)
                        
                        return None
                
                return self.generic_visit(node)
                
            def visit_Assign(self, node):
                # Check for self-assignments: x = x
                if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and 
                    isinstance(node.value, ast.Name) and node.targets[0].id == node.value.id):
                    
                    self.changes.append(f"Removed self-assignment: {node.targets[0].id} = {node.value.id}")
                    
                    # Create change record
                    change = OptimizationChange(
                        description=f"Removed self-assignment",
                        line_start=getattr(node, 'lineno', 0),
                        line_end=getattr(node, 'end_lineno', 0) if hasattr(node, 'end_lineno') else 0,
                        original_code=astor.to_source(node),
                        optimized_code=f"# Removed self-assignment: {node.targets[0].id} = {node.value.id}"
                    )
                    self.detailed_changes.append(change)
                    
                    return None
                    
                return self.generic_visit(node)
                
            def visit_BinOp(self, node):
                # Process operands first
                self.generic_visit(node)
                
                # Optimize x + 0, x * 1, etc.
                if isinstance(node.right, ast.Constant):
                    # Addition with 0
                    if isinstance(node.op, ast.Add) and node.right.value == 0:
                        self.changes.append("Removed addition with 0")
                        return node.left
                        
                    # Subtraction with 0
                    if isinstance(node.op, ast.Sub) and node.right.value == 0:
                        self.changes.append("Removed subtraction with 0")
                        return node.left
                        
                    # Multiplication with 1
                    if isinstance(node.op, ast.Mult) and node.right.value == 1:
                        self.changes.append("Removed multiplication with 1")
                        return node.left
                        
                    # Division by 1
                    if isinstance(node.op, ast.Div) and node.right.value == 1:
                        self.changes.append("Removed division by 1")
                        return node.left
                        
                # Check the left operand too for commutative operations
                if isinstance(node.left, ast.Constant):
                    # Addition with 0
                    if isinstance(node.op, ast.Add) and node.left.value == 0:
                        self.changes.append("Removed addition with 0")
                        return node.right
                        
                    # Multiplication with 1
                    if isinstance(node.op, ast.Mult) and node.left.value == 1:
                        self.changes.append("Removed multiplication with 1")
                        return node.right
                        
                    # Multiplication with 0 (returns 0)
                    if isinstance(node.op, ast.Mult) and node.left.value == 0:
                        self.changes.append("Simplified multiplication with 0")
                        return ast.Constant(value=0)
                        
                return node
                
            def visit_Call(self, node):
                # Process function call arguments
                self.generic_visit(node)
                
                # Remove redundant str() calls on string literals
                if (isinstance(node.func, ast.Name) and node.func.id == 'str' and 
                    len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and 
                    isinstance(node.args[0].value, str)):
                    
                    self.changes.append("Removed redundant str() call on string literal")
                    return node.args[0]
                    
                # Remove redundant list() calls on list literals
                if (isinstance(node.func, ast.Name) and node.func.id == 'list' and 
                    len(node.args) == 1 and isinstance(node.args[0], ast.List)):
                    
                    self.changes.append("Removed redundant list() call on list literal")
                    return node.args[0]
                    
                # Remove redundant int() calls on integer literals
                if (isinstance(node.func, ast.Name) and node.func.id == 'int' and 
                    len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and 
                    isinstance(node.args[0].value, int)):
                    
                    self.changes.append("Removed redundant int() call on integer literal")
                    return node.args[0]
                    
                return node
        
        # Apply redundancy removal
        remover = RedundancyRemover()
        optimized_tree = remover.visit(copy.deepcopy(tree))
        
        return optimized_tree, remover.changes, remover.detailed_changes
    
    def _remove_redundant_returns(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Remove redundant return statements and simplify returns."""
        class ReturnSimplifier(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_FunctionDef(self, node):
                # Process function body first
                self.generic_visit(node)
                
                if not node.body:
                    # Empty function body - add a default return None
                    node.body = [ast.Return(value=None)]
                    return node
                
                # Check if the last statement is a return
                last_stmt = node.body[-1]
                if not isinstance(last_stmt, ast.Return):
                    # Add implicit return None at the end of function
                    # This is technically not needed but makes the code more explicit
                    node.body.append(ast.Return(value=None))
                    
                return node
                
            def visit_Return(self, node):
                # Simplify return statements with redundant expressions
                if node.value is None:
                    # Leave "return None" as is
                    return node
                    
                # Simplify expressions in return statements using constant folding
                # This could be expanded based on specific use cases
                    
                return node
        
        # Apply return simplification
        simplifier = ReturnSimplifier()
        optimized_tree = simplifier.visit(copy.deepcopy(tree))
        
        return optimized_tree, simplifier.changes, simplifier.detailed_changes
    
    def _inline_functions(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Inline small functions for performance improvement."""
        class FunctionInliner(ast.NodeTransformer):
            def __init__(self, config):
                self.changes = []
                self.detailed_changes = []
                self.functions = {}  # Maps function names to AST nodes
                self.config = config
                
            def visit_Module(self, node):
                # First pass: collect all function definitions
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        self.functions[item.name] = item
                
                # Second pass: inline function calls
                self.generic_visit(node)
                return node
                
            def visit_FunctionDef(self, node):
                # Skip the function body if this is a function we might inline
                if node.name in self.functions:
                    return node
                
                # Otherwise, process the function body normally
                self.generic_visit(node)
                return node
                
            def visit_Call(self, node):
                # Process the arguments first
                self.generic_visit(node)
                
                # Check if this is a call to a function we know
                if isinstance(node.func, ast.Name) and node.func.id in self.functions:
                    func_def = self.functions[node.func.id]
                    
                    # Only inline if the function is small enough
                    if self._is_inlinable(func_def):
                        # Create inlined version of the function
                        try:
                            inlined = self._inline_function(func_def, node.args, node.keywords)
                            if inlined:
                                self.changes.append(f"Inlined function call: {func_def.name}")
                                
                                # Create change record
                                change = OptimizationChange(
                                    description=f"Inlined function call: {func_def.name}",
                                    line_start=getattr(node, 'lineno', 0),
                                    line_end=getattr(node, 'end_lineno', 0) if hasattr(node, 'end_lineno') else 0,
                                    original_code=astor.to_source(node),
                                    optimized_code="# Inlined function call"
                                )
                                self.detailed_changes.append(change)
                                
                                return inlined
                        except Exception as e:
                            # If inlining fails, keep the original call
                            pass
                
                return node
                
            def _is_inlinable(self, func_def):
                """Check if a function is small enough to inline."""
                # Count statements in function body
                statement_count = len(func_def.body)
                
                # Functions with one or very few statements are good candidates
                return statement_count <= self.config.inline_threshold
                
            def _inline_function(self, func_def, args, keywords):
                """Create an inlined version of a function call."""
                # Map arguments to parameters
                if len(func_def.args.args) != len(args) and not func_def.args.defaults:
                    # Can't inline if argument counts don't match
                    return None
                
                # Create a mapping of parameter names to argument values
                param_map = {}
                for i, arg_node in enumerate(func_def.args.args):
                    if i < len(args):
                        param_map[arg_node.arg] = args[i]
                    elif i - len(args) < len(func_def.args.defaults):
                        # Use default value
                        default_index = i - len(args)
                        param_map[arg_node.arg] = func_def.args.defaults[default_index]
                    else:
                        # Missing argument with no default
                        return None
                
                # Handle keyword arguments
                for kw in keywords:
                    param_map[kw.arg] = kw.value
                
                # Substitute parameters in the function body
                class ParameterSubstitutor(ast.NodeTransformer):
                    def __init__(self, param_map):
                        self.param_map = param_map
                        
                    def visit_Name(self, node):
                        if isinstance(node.ctx, ast.Load) and node.id in self.param_map:
                            return self.param_map[node.id]
                        return node
                        
                    def visit_Return(self, node):
                        # Replace return statements with their value
                        if node.value:
                            return self.visit(node.value)
                        return ast.Constant(value=None)
                
                # Apply substitution for each statement
                substitutor = ParameterSubstitutor(param_map)
                inlined_body = []
                
                for stmt in func_def.body[:-1]:  # All but the last statement
                    inlined_stmt = substitutor.visit(copy.deepcopy(stmt))
                    inlined_body.append(inlined_stmt)
                
                # Handle the last statement (might be a return)
                last_stmt = func_def.body[-1]
                if isinstance(last_stmt, ast.Return):
                    inlined_result = substitutor.visit(copy.deepcopy(last_stmt.value)) if last_stmt.value else ast.Constant(value=None)
                    return inlined_result
                else:
                    inlined_body.append(substitutor.visit(copy.deepcopy(last_stmt)))
                    # If no return, the function returns None
                    return ast.Constant(value=None)
                
                # This should not be reached, but just in case
                return None
        
        # Apply function inlining
        inliner = FunctionInliner(self.config)
        optimized_tree = inliner.visit(copy.deepcopy(tree))
        
        return optimized_tree, inliner.changes, inliner.detailed_changes
    
    def _optimize_memory(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Optimize memory usage in code."""
        class MemoryOptimizer(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_ListComp(self, node):
                """Convert list comprehensions to generator expressions where appropriate."""
                # Only convert if this is not already a starred assignment target
                parent = getattr(node, 'parent', None)
                
                # Don't convert if it's being unpacked
                if isinstance(parent, ast.Assign) and any(
                    isinstance(target, ast.Starred) for target in parent.targets
                ):
                    return self.generic_visit(node)
                
                # Check if the list comp is used immediately in a for loop
                if isinstance(parent, ast.For) and parent.iter is node:
                    # Convert to generator expression
                    gen_exp = ast.GeneratorExp(
                        elt=node.elt,
                        generators=node.generators
                    )
                    
                    self.changes.append("Converted list comprehension to generator expression")
                    
                    # Create change record
                    change = OptimizationChange(
                        description="Converted list comprehension to generator expression",
                        line_start=getattr(node, 'lineno', 0),
                        line_end=getattr(node, 'end_lineno', 0) if hasattr(node, 'end_lineno') else 0,
                        original_code=astor.to_source(node),
                        optimized_code=astor.to_source(gen_exp)
                    )
                    self.detailed_changes.append(change)
                    
                    return gen_exp
                
                return self.generic_visit(node)
                
            def visit_Compare(self, node):
                """Replace list with set for membership testing."""
                # Check for "in" operations on lists that could be sets
                if len(node.ops) == 1 and isinstance(node.ops[0], (ast.In, ast.NotIn)):
                    comparator = node.comparators[0]
                    
                    # If comparing against a list literal, consider converting to set
                    if isinstance(comparator, ast.List) and len(comparator.elts) > 5:
                        # Convert list to set for faster lookups
                        set_comp = ast.Set(elts=comparator.elts)
                        
                        self.changes.append("Replaced list with set for membership testing")
                        
                        # Create change record
                        change = OptimizationChange(
                            description="Replaced list with set for faster lookups",
                            line_start=getattr(comparator, 'lineno', 0),
                            line_end=getattr(comparator, 'end_lineno', 0) if hasattr(comparator, 'end_lineno') else 0,
                            original_code=astor.to_source(comparator),
                            optimized_code=astor.to_source(set_comp)
                        )
                        self.detailed_changes.append(change)
                        
                        node.comparators[0] = set_comp
                
                return self.generic_visit(node)
        
        # Apply memory optimization
        optimizer = MemoryOptimizer()
        optimized_tree = optimizer.visit(copy.deepcopy(tree))
        
        return optimized_tree, optimizer.changes, optimizer.detailed_changes
    
    def _optimize_string_concat(self, tree: ast.AST) -> Tuple[ast.AST, List[str], List[OptimizationChange]]:
        """Optimize string concatenation operations."""
        class StringConcatOptimizer(ast.NodeTransformer):
            def __init__(self):
                self.changes = []
                self.detailed_changes = []
                
            def visit_For(self, node):
                """Look for string concatenation in loops."""
                # Process the body first
                self.generic_visit(node)
                
                # Look for string concatenation pattern in loops
                string_concat_assigns = []
                
                for stmt in node.body:
                    if isinstance(stmt, ast.AugAssign) and isinstance(stmt.op, ast.Add):
                        # Check if we're concatenating to a string
                        if isinstance(stmt.target, ast.Name):
                            string_concat_assigns.append(stmt)
                
                # If we found string concatenation in the loop, suggest using join
                if string_concat_assigns:
                    self.changes.append("Detected string concatenation in loop (consider using join instead)")
                    
                    # Create change record
                    change = OptimizationChange(
                        description="Suggested replacing string concatenation with join method",
                        line_start=getattr(node, 'lineno', 0),
                        line_end=getattr(node, 'end_lineno', 0) if hasattr(node, 'end_lineno') else 0,
                        original_code=astor.to_source(node),
                        optimized_code="# Consider using ''.join() instead of += for string concatenation in loops"
                    )
                    self.detailed_changes.append(change)
                
                return node
                
            def visit_BinOp(self, node):
                """Optimize string concatenation with + operator."""
                # Process operands first
                self.generic_visit(node)
                
                # Check for chain of string concatenations
                if isinstance(node.op, ast.Add):
                    # Count the number of string concatenations in a chain
                    strings = self._count_string_chain(node)
                    
                    if strings > 3:
                        self.changes.append(f"Detected chain of {strings} string concatenations (consider using join)")
                        
                        # Create change record
                        change = OptimizationChange(
                            description=f"Suggested replacing string concatenation chain with join",
                            line_start=getattr(node, 'lineno', 0),
                            line_end=getattr(node, 'end_lineno', 0) if hasattr(node, 'end_lineno') else 0,
                            original_code=astor.to_source(node),
                            optimized_code="# Consider using ''.join() instead of + for multiple string concatenations"
                        )
                        self.detailed_changes.append(change)
                
                return node
                
            def _count_string_chain(self, node, count=1):
                """Count the number of strings in a concatenation chain."""
                if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
                    return count
                
                # Check if either operand is a string constant
                left_is_str = isinstance(node.left, ast.Constant) and isinstance(node.left.value, str)
                right_is_str = isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)
                
                # Increment count if either operand is a string
                if left_is_str or right_is_str:
                    count += 1
                
                # Recursively check if left or right operand is also a concatenation
                if isinstance(node.left, ast.BinOp):
                    count = self._count_string_chain(node.left, count)
                if isinstance(node.right, ast.BinOp):
                    count = self._count_string_chain(node.right, count)
                
                return count
        
        # Apply string concatenation optimization
        optimizer = StringConcatOptimizer()
        optimized_tree = optimizer.visit(copy.deepcopy(tree))
        
        return optimized_tree, optimizer.changes, optimizer.detailed_changes

# Public interface functions

def detect_inefficient_patterns(code: str) -> List[Dict[str, Any]]:
    """
    Detect inefficient code patterns without modifying the code.
    
    Args:
        code: Python code as string
        
    Returns:
        List of detected inefficiencies with line numbers and descriptions
    """
    patterns = []
    
    try:
        # Parse the code
        tree = ast.parse(code)
        
        # Use a visitor to detect inefficiencies
        class InefficiencyDetector(ast.NodeVisitor):
            def __init__(self):
                self.inefficiencies = []
                
            def visit_For(self, node):
                # Check for inefficient loops
                if isinstance(node.iter, ast.Call):
                    call = node.iter
                    if isinstance(call.func, ast.Name) and call.func.id == 'range':
                        # Check for range(len(x)) instead of enumerate(x)
                        if (len(call.args) == 1 and isinstance(call.args[0], ast.Call) and 
                            isinstance(call.args[0].func, ast.Name) and call.args[0].func.id == 'len'):
                            self.inefficiencies.append({
                                'line': node.lineno,
                                'type': 'inefficient_loop',
                                'description': 'Use enumerate() instead of range(len())'
                            })
                self.generic_visit(node)
                
            def visit_BinOp(self, node):
                # Check for string concatenation in a loop
                if isinstance(node.op, ast.Add):
                    # Check if either operand is a string
                    left_is_str = (isinstance(node.left, ast.Constant) and isinstance(node.left.value, str))
                    right_is_str = (isinstance(node.right, ast.Constant) and isinstance(node.right.value, str))
                    
                    if left_is_str or right_is_str:
                        # Find if this is in a loop
                        parent = getattr(node, 'parent', None)
                        in_loop = False
                        while parent:
                            if isinstance(parent, (ast.For, ast.While)):
                                in_loop = True
                                break
                            parent = getattr(parent, 'parent', None)
                            
                        if in_loop:
                            self.inefficiencies.append({
                                'line': node.lineno,
                                'type': 'string_concat_in_loop',
                                'description': 'String concatenation in loop; use join() or list comprehension instead'
                            })
                self.generic_visit(node)
                
            def visit_Compare(self, node):
                # Check for inefficient comparisons
                for i, op in enumerate(node.ops):
                    if isinstance(op, ast.In) and isinstance(node.comparators[i], ast.List):
                        # Check for "x in [...]" instead of "x in {...}" (set)
                        if len(node.comparators[i].elts) > 3:
                            self.inefficiencies.append({
                                'line': node.lineno,
                                'type': 'list_membership',
                                'description': 'Use a set for membership testing instead of a list'
                            })
                self.generic_visit(node)
        
        # Run the detector
        detector = InefficiencyDetector()
        detector.visit(tree)
        patterns = detector.inefficiencies
    except Exception as e:
        # If parsing fails, return empty list
        logger.error(f"Error detecting inefficient patterns: {str(e)}")
    
    return patterns

def apply_optimization_rules(code: str, optimization_level="medium") -> Tuple[str, List[str]]:
    """
    Apply rule-based optimizations to Python code.
    
    Args:
        code: Python code as string
        optimization_level: Level of optimization to apply ("low", "medium", "aggressive")
        
    Returns:
        Tuple of (optimized_code, changes_made)
    """
    # Create optimizer with specified level
    optimizer = RuleBasedOptimizer(OptimizerConfig(optimization_level=optimization_level))
    
    # Apply optimizations
    result = optimizer.optimize(code)
    
    if result.success:
        return result.optimized_code, result.changes_made
    else:
        # Return original code if optimization failed
        return code, [f"Optimization failed: {result.error}"]

# Main execution for testing
if __name__ == "__main__":
    # Example usage
    test_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
    """
    
    # Detect inefficient patterns
    inefficiencies = detect_inefficient_patterns(test_code)
    print("Inefficient patterns detected:")
    for issue in inefficiencies:
        print(f"Line {issue['line']}: {issue['description']}")
    
    # Apply optimizations
    optimized_code, changes = apply_optimization_rules(test_code)
    
    print("\nOptimized code:")
    print(optimized_code)
    
    print("\nChanges made:")
    for change in changes:
        print(f"- {change}")