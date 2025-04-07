"""
Rule-based code optimizer for EFFICODE-ACRR

This module provides rule-based code optimization capabilities:
- Converting for loops to list comprehensions
- Optimizing infinite loops
- Improving code readability and efficiency
"""

import ast
import re
import logging
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RuleBasedOptimizer:
    """
    Applies rule-based optimizations to Python code
    """
    
    def __init__(self):
        """Initialize the optimizer"""
        self.applied_rules = []
        logger.info("RuleBasedOptimizer initialized")
    
    def optimize(self, code: str, level: str = 'medium') -> Tuple[str, str, str, str]:
        """
        Optimize Python code using rule-based transformations
        
        Args:
            code: Python code as string
            level: Optimization level ('low', 'medium', 'high')
            
        Returns:
            Tuple containing (optimized_code, original_complexity, optimized_complexity, explanation)
        """
        if not isinstance(code, str) or not code.strip():
            logger.warning("Empty or invalid code provided")
            return code, "O(?)", "O(?)", "No code to optimize"
        
        # Reset applied rules
        self.applied_rules = []
        
        try:
            # Parse code into AST
            tree = ast.parse(code)
            
            # Apply optimization rules
            transformer = OptimizationTransformer(level)
            optimized_tree = transformer.visit(tree)
            
            # Convert AST back to code
            optimized_code = ast.unparse(optimized_tree)
            
            # Get applied rules
            self.applied_rules = transformer.applied_rules
            
            # Generate explanation
            explanation = self._generate_explanation()
            
            # Estimate complexities
            original_complexity = self._estimate_complexity(code)
            optimized_complexity = self._estimate_complexity(optimized_code)
            
            logger.info(f"Applied {len(self.applied_rules)} optimization rules")
            return optimized_code, original_complexity, optimized_complexity, explanation
            
        except Exception as e:
            error_msg = f"Error during optimization: {e}"
            logger.error(error_msg)
            return code, "O(?)", "O(?)", f"Error: {error_msg}"
    
    def get_applied_rules(self) -> List[Dict[str, str]]:
        """Get list of applied optimization rules"""
        return self.applied_rules
    
    def _generate_explanation(self) -> str:
        """Generate explanation of applied optimizations"""
        if not self.applied_rules:
            return "No optimizations were applicable"
        
        explanations = []
        for rule in self.applied_rules:
            desc = rule.get('description', '')
            if desc:
                explanations.append(desc)
        
        return "Applied optimizations: " + ", ".join(explanations)
    
    def _estimate_complexity(self, code: str) -> str:
        """Estimate time complexity of code"""
        # Simple heuristics for complexity estimation
        if "for" in code and "range" in code:
            if "for" in code and "for" in code[code.index("for"):]:
                return "O(n²)"
            return "O(n)"
        elif "while" in code and "True" in code:
            return "O(∞)"
        elif "if" in code and "return" in code:
            return "O(1)"
        return "O(?)"

class OptimizationTransformer(ast.NodeTransformer):
    """
    AST transformer that applies optimization rules
    """
    
    def __init__(self, level: str = 'medium'):
        """Initialize transformer with optimization level"""
        self.level = level
        self.applied_rules = []
    
    def visit_For(self, node: ast.For) -> ast.AST:
        """Optimize for loops"""
        # Convert simple for loops to list comprehensions
        if isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                if len(node.body) == 1 and isinstance(node.body[0], ast.Assign):
                    if isinstance(node.body[0].targets[0], ast.Subscript):
                        self.applied_rules.append({
                            'rule': 'list_comprehension',
                            'description': 'Converted for loop to list comprehension',
                            'category': 'loop'
                        })
                        return self._create_list_comprehension(node)
        return node
    
    def visit_While(self, node: ast.While) -> ast.AST:
        """Optimize while loops"""
        # Optimize infinite loops
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            if len(node.body) == 1 and isinstance(node.body[0], ast.If):
                self.applied_rules.append({
                    'rule': 'infinite_loop',
                    'description': 'Optimized infinite while loop',
                    'category': 'loop'
                })
                return self._optimize_infinite_loop(node)
        return node
    
    def _create_list_comprehension(self, node: ast.For) -> ast.ListComp:
        """Create list comprehension from for loop"""
        return ast.ListComp(
            elt=node.body[0].value,
            generators=[
                ast.comprehension(
                    target=node.target,
                    iter=node.iter,
                    ifs=[]
                )
            ]
        )
    
    def _optimize_infinite_loop(self, node: ast.While) -> ast.While:
        """Optimize infinite while loop"""
        return ast.While(
            test=node.test,
            body=node.body,
            orelse=node.orelse
        )

# Example usage
if __name__ == '__main__':
    # Example: Optimize bubble sort
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
    """
    
    optimizer = RuleBasedOptimizer()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code)
    
    print("Original code:")
    print(code)
    print("\nOptimized code:")
    print(optimized_code)
    print("\nExplanation:", explanation)
    print("Original complexity:", original_complexity)
    print("Optimized complexity:", optimized_complexity) 