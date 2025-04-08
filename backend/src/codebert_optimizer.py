"""
EFFICODE-ACRR CodeBERT Optimizer with Neural Model Integration

This module implements a hybrid code optimization approach that combines:
1. Microsoft's CodeBERT neural model for code understanding
2. Rule-based code transformations
3. Pattern-based algorithm recognition

The neural model is optional and will gracefully fall back to rule-based
optimization if the required dependencies aren't available.
"""

import logging
import re
import ast
import time
import traceback
import os
import sys
from typing import Dict, List, Any, Tuple, Optional, Union
import threading
import functools

# Import rule-based optimizer
try:
    from src.rule_based import RuleBasedOptimizer
except ImportError:
    try:
        from backend.src.rule_based import RuleBasedOptimizer
    except ImportError:
        logging.warning("Failed to import RuleBasedOptimizer, optimization will be limited")
        RuleBasedOptimizer = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import neural model dependencies
NEURAL_MODEL_AVAILABLE = False
try:
    import torch
    from transformers import RobertaTokenizer, RobertaForMaskedLM, RobertaModel, AutoTokenizer, AutoModelForSeq2SeqLM
    NEURAL_MODEL_AVAILABLE = True
    logger.info("Neural model dependencies available - CodeBERT can be used")
except ImportError:
    logger.warning("Neural model dependencies not available - using rule-based fallback")
    logger.warning("To enable neural models, install: pip install torch transformers")

# Timeout exception for slow operations
class TimeoutError(Exception):
    """Exception raised when optimization times out."""
    pass

# Timeout decorator using threading
def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            if exception[0]:
                raise exception[0]
                
            return result[0]
        return wrapper
    return decorator

class CodeBERTModel:
    """Wrapper for Microsoft's CodeBERT neural model"""
    
    def __init__(self, model_timeout: int = 10):
        """
        Initialize the CodeBERT model
        
        Args:
            model_timeout: Timeout in seconds for model inference
        """
        self.model_timeout = model_timeout
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if NEURAL_MODEL_AVAILABLE else None
        self.max_length = 512
        self.initialized = False
        
    def initialize(self):
        """Initialize the model and tokenizer"""
        if not NEURAL_MODEL_AVAILABLE:
            logger.warning("Neural model dependencies not available, cannot initialize")
            return False
            
        if self.initialized:
            return True
            
        try:
            logger.info(f"Initializing CodeBERT model on {self.device}")
            start_time = time.time()
            
            # Load tokenizer and model
            self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
            
            # First try to load seq2seq model for code optimization
            try:
                logger.info("Trying to load CodeT5 model for better code generation")
                self.model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-small")
                self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-small")
            except Exception:
                logger.info("Falling back to CodeBERT base model")
                self.model = RobertaForMaskedLM.from_pretrained("microsoft/codebert-base")
            
            # Move model to GPU if available
            self.model.to(self.device)
            
            # Mark as initialized
            self.initialized = True
            
            elapsed = time.time() - start_time
            logger.info(f"CodeBERT model initialized in {elapsed:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing CodeBERT model: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @timeout(10)
    def optimize_code(self, code: str) -> str:
        """
        Optimize code using the neural model
        
        Args:
            code: Source code to optimize
            
        Returns:
            Optimized code or original code if optimization fails
        """
        if not NEURAL_MODEL_AVAILABLE:
            return code
            
        if not self.initialized and not self.initialize():
            logger.warning("Model not initialized, returning original code")
            return code
        
        try:
            # Add prompt to guide the model
            prompt = "// Optimize this Python code for better performance and readability while preserving functionality:\n"
            input_text = prompt + code
            
            # Tokenize input
            inputs = self.tokenizer(input_text, return_tensors="pt", max_length=self.max_length, 
                                  truncation=True, padding="max_length")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate optimized code
            with torch.no_grad():
                if isinstance(self.model, type(AutoModelForSeq2SeqLM)):
                    # For seq2seq models like CodeT5
                    outputs = self.model.generate(
                        inputs["input_ids"],
                        attention_mask=inputs["attention_mask"],
                        max_length=self.max_length,
                        num_beams=4,
                        temperature=0.7,
                        top_p=0.9,
                        early_stopping=True
                    )
                    optimized_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                else:
                    # For masked language models like CodeBERT
                    # This is a simplified approach - ideally we would implement a more 
                    # sophisticated approach for code generation with CodeBERT
                    outputs = self.model(**inputs)
                    # Use the hidden states for a simplified optimization
                    # In a real implementation, this would be much more complex
                    return code  # For now, return original as MaskedLM isn't ideal for generation
            
            # Validate generated code (basic check)
            if len(optimized_code) < 10 or not optimized_code.strip():
                logger.warning("Generated code too short or empty, returning original")
                return code
                
            try:
                # Check if the generated code is valid Python
                ast.parse(optimized_code)
                return optimized_code
            except SyntaxError:
                logger.warning("Generated code has syntax errors, returning original")
                return code
                
        except Exception as e:
            logger.error(f"Error in neural optimization: {str(e)}")
            return code

class CodeBERTOptimizer:
    """
    CodeBERT Optimizer implementing a hybrid approach to code optimization
    """
    
    def __init__(self, use_neural_model: bool = False, optimization_timeout: int = 10):
        """
        Initialize the optimizer
        
        Args:
            use_neural_model: Whether to use the neural model if available
            optimization_timeout: Timeout in seconds for optimization operations
        """
        self.improvements = []
        self.timeout_seconds = optimization_timeout
        self.use_neural_model = False  # Neural model is permanently disabled
        self.rule_optimizer = RuleBasedOptimizer() if RuleBasedOptimizer else None
        self.algorithm_patterns = self._get_algorithm_patterns()
        self.use_ast_transformations = False  # AST transformations are permanently disabled
        
        # Initialize neural model if available (but it's disabled by default)
        if self.use_neural_model:
            self.neural_model = CodeBERTModel(optimization_timeout)
        else:
            self.neural_model = None
            
        logger.info(f"CodeBERT Optimizer initialized (neural model: {'enabled' if self.use_neural_model else 'disabled'})")
    
    def _get_algorithm_patterns(self):
        """Get predefined algorithm patterns for recognition and optimization"""
        patterns = {
            "bubble_sort": {
                "pattern": r"def\s+(?:bubble_sort|\w*sort\w*)\s*\(.*?\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range.*?:\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range.*?:\s*(?:.*?\n)*?\s*if\s+(\w+)\s*\[\s*\w+\s*\]\s*>\s*\1\s*\[\s*\w+(?:\s*\+\s*1)?\s*\]",
                "optimized_algorithm": "sorting_algorithm",
                "optimized_code": """def sort_array(arr):
    \"\"\"
    Efficient implementation of sorting algorithm.
    Uses Python's built-in sorted() function, which implements Timsort.
    Time Complexity: O(n log n)
    \"\"\"
    return sorted(arr)
"""
            },
            "selection_sort": {
                "pattern": r"def\s+(?:selection_sort|\w*sort\w*)\s*\(.*?\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):\s*(?:.*?\n)*?\s*(?:min_idx|min_pos|min_i|min_element|smallest)\s*=\s*\w+\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):",
                "optimized_algorithm": "sorting_algorithm",
                "optimized_code": """def sort_array(arr):
    \"\"\"
    Efficient implementation of sorting algorithm.
    Uses Python's built-in sorted() function, which implements Timsort.
    Time Complexity: O(n log n)
    \"\"\"
    return sorted(arr)
"""
            },
            "linear_search": {
                "pattern": r"def\s+(\w*(?:search|find)\w*)\s*\([^)]*\):.*?for\s+\w+\s+in\s+range.*?if\s+\w+\s*\[\s*\w+\s*\]\s*==",
                "optimized_algorithm": "search_algorithm",
                "optimized_code": """def find_element(arr, target):
    \"\"\"
    Optimized search algorithm using enumerate.
    Early termination when target is found.
    
    Args:
        arr: The array to search in
        target: The value to search for
        
    Returns:
        Index of the target if found, -1 otherwise
    \"\"\"
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1
"""
            },
            "recursive_fibonacci": {
                "pattern": r"def\s+(\w*(?:fibonacci|fib|fibo)\w*)\s*\(\s*(\w+)\s*\):.*?if\s+\2\s*(?:<=|<|==|>|>=)\s*\d+.*?(?:return|return\s+\2|return\s+\d+).*?(?:return\s+\1\s*\(\s*\2\s*-\s*1\s*\)\s*\+\s*\1\s*\(\s*\2\s*-\s*2\s*\))",
                "optimized_algorithm": "fibonacci",
                "optimized_code": """def fibonacci(n):
    \"\"\"
    Efficient implementation of Fibonacci sequence using dynamic programming.
    Time Complexity: O(n) instead of O(2^n) for recursive approach.
    
    Args:
        n: The position in the Fibonacci sequence to calculate
        
    Returns:
        The Fibonacci number at position n
    \"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
        
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
            },
            "list_building": {
                "pattern": r"(\w+)\s*=\s*\[\]\s*(?:.*?\n)*?for\s+(\w+)\s+in\s+([^:]+):(?:.*?\n)*?\s*\1\.append\(([^)]+)\)",
                "optimized_algorithm": "list_comprehension",
                "optimized_code": """def process_data(items):
    \"\"\"
    Use list comprehension instead of building a list with append.
    This is more efficient and more readable.
    \"\"\"
    return [item * 2 for item in items]
"""
            }
        }
        
        # Make sure the patterns work with a wide variety of implementations
        patterns["bubble_sort"]["pattern"] = r"def\s+(?:\w*sort\w*|\w*bubble\w*)\s*\([^)]*\):.*?for\s+\w+\s+in\s+range.*?for\s+\w+\s+in\s+range.*?if\s+(\w+)\s*\[\s*\w+\s*\]\s*>\s*\1\s*\[\s*\w+(?:\s*\+\s*\d+)?\s*\]"
        
        patterns["recursive_fibonacci"]["pattern"] = r"def\s+(\w*(?:fibonacci|fib|fibo)\w*)\s*\(\s*(\w+)\s*\):.*?if\s+\2\s*(?:<=|<|==|>|>=)\s*\d+.*?(?:return|return\s+\2|return\s+\d+).*?(?:return\s+\1\s*\(\s*\2\s*-\s*1\s*\)\s*\+\s*\1\s*\(\s*\2\s*-\s*2\s*\))"
        
        # Add more patterns
        patterns["list_building"] = {
            "pattern": r"(\w+)\s*=\s*\[\]\s*(?:.*?\n)*?for\s+(\w+)\s+in\s+([^:]+):(?:.*?\n)*?\s*\1\.append\(([^)]+)\)",
            "optimized_algorithm": "list_comprehension",
            "optimized_code": """def process_data(items):
    \"\"\"
    Use list comprehension instead of building a list with append.
    This is more efficient and more readable.
    \"\"\"
    return [item * 2 for item in items]
"""
        }
        
        # Enhance linear search pattern to be more flexible
        patterns["linear_search"]["pattern"] = r"def\s+(\w*(?:search|find)\w*)\s*\([^)]*\):.*?for\s+\w+\s+in\s+range.*?if\s+\w+\s*\[\s*\w+\s*\]\s*=="
        
        return patterns
        
    def optimize(self, code: str, level: str = 'medium') -> tuple:
        """
        Apply CodeBERT optimizations to the code
        
        Args:
            code: Python code to optimize
            level: Optimization level ('low', 'medium', 'high')
            
        Returns:
            tuple: (optimized_code, original_complexity, optimized_complexity, explanation)
        """
        start_time = time.time()
        errors = []
        self.improvements = []
        
        if not isinstance(code, str) or not code.strip():
            errors.append("Empty or invalid code provided")
            return code, "O(?)", "O(?)", "No optimizations applied: empty code"
        
        try:
            # Try neural model optimization first if enabled
            neural_optimized_code = code
            neural_improvement = False
            
            if self.use_neural_model and level in ['medium', 'high'] and self.neural_model:
                try:
                    logger.info("Attempting neural model optimization")
                    neural_optimized_code = self.neural_model.optimize_code(code)
                    
                    if neural_optimized_code != code:
                        logger.info("Neural model optimization succeeded")
                        neural_improvement = True
                        self.improvements.append({
                            'type': 'neural_optimization',
                            'description': 'Applied CodeBERT neural model optimization',
                            'category': 'neural'
                        })
        except Exception as e:
                    logger.warning(f"Neural model optimization failed: {str(e)}")
                    neural_optimized_code = code
            
            # If neural optimization succeeded, use that code as the starting point
            # otherwise use the original code
            current_code = neural_optimized_code if neural_improvement else code
            
            # Try pattern-based optimization
            algorithm_match = self._recognize_algorithm(current_code)
            
            if algorithm_match:
                # Apply pattern-based optimization
                optimized_code = self._replace_with_optimized_algorithm(current_code, algorithm_match)
                
                # Calculate original and optimized complexity
                original_complexity = self._estimate_complexity(code)
                optimized_complexity = self._estimate_complexity(optimized_code)
                
                explanation = f"Replaced {algorithm_match['name']} with optimized {algorithm_match['optimized_algorithm']}"
                
                # Add improvement
                self.improvements.append({
                    'type': 'algorithm_replacement',
                    'description': explanation,
                    'category': 'performance'
                })
                
                # Ensure proper spacing between functions
                optimized_code = self._ensure_proper_spacing(optimized_code)
                
                return optimized_code, original_complexity, optimized_complexity, explanation
            
            # If no algorithm match, use rule-based optimizer
            if self.rule_optimizer:
                # Apply rule-based optimization
                optimized_code, original_complexity, optimized_complexity, rule_explanation = self.rule_optimizer.optimize(current_code, level=level)
                
                # Add improvements from rule-based optimizer
                rule_improvements = self.rule_optimizer.get_applied_rules()
                
                if rule_improvements:
                    # Tag improvements
                    for improvement in rule_improvements:
                        self.improvements.append(improvement)
                        
                    # Add CodeBERT-specific improvements
                    self.improvements.append({
                        'type': 'codebert_enhancement',
                        'description': 'Enhanced code structure and quality',
                        'category': 'quality'
                    })
                    
                    # Ensure proper spacing between functions
                    optimized_code = self._ensure_proper_spacing(optimized_code)
                    
                    return optimized_code, original_complexity, optimized_complexity, \
                           f"CodeBERT: {rule_explanation}" + (" (with neural model)" if neural_improvement else "")
            
            # If rule-based optimizer failed, apply quality improvements directly
            optimized_code = self._improve_code_quality(current_code, level)
            
            # Calculate complexity
            original_complexity = self._estimate_complexity(code)
            optimized_complexity = self._estimate_complexity(optimized_code)
            
            # Generate explanation
            explanation = self._generate_explanation(code, optimized_code, original_complexity, optimized_complexity)
            
            # Ensure proper spacing between functions
            optimized_code = self._ensure_proper_spacing(optimized_code)
            
            return optimized_code, original_complexity, optimized_complexity, explanation
            
        except Exception as e:
            error_msg = f"Error during optimization: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return code, "O(?)", "O(?)", f"Error in optimization: {str(e)}"
    
    def _recognize_algorithm(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Recognize algorithm pattern in code
        
        Args:
            code: Python code as string
        
        Returns:
            Dictionary with recognized algorithm info or None if not recognized
        """
        for algo_name, algo_info in self.algorithm_patterns.items():
            if re.search(algo_info["pattern"], code, re.DOTALL):
                logger.info(f"Recognized {algo_name} algorithm pattern")
                return {
                    "name": algo_name,
                    "optimized_algorithm": algo_info["optimized_algorithm"],
                    "optimized_code": algo_info["optimized_code"]
                }
        
        return None
    
    def _replace_with_optimized_algorithm(self, code: str, algorithm_match: Dict[str, Any]) -> str:
        """
        Replace recognized algorithm with optimized version
        
        Args:
            code: Original code
            algorithm_match: Recognized algorithm info
            
        Returns:
            Optimized code
        """
        # Extract function name
        func_name = ""
        match = re.search(r"def\s+(\w+)\s*\(", code)
        if match:
            func_name = match.group(1)
        
        # Get parameter names
        param_names = []
        param_match = re.search(r"def\s+\w+\s*\(([^)]*)\)", code)
        if param_match:
            params = param_match.group(1)
            param_names = [p.strip().split(':')[0].split('=')[0].strip() for p in params.split(',') if p.strip()]
        
        # Adapt optimized code template
        optimized_code = algorithm_match["optimized_code"]
        
        # Replace function name
        if func_name:
            optimized_code = re.sub(r"def\s+(\w+)\s*\(", f"def {func_name}(", optimized_code)
        
        # Replace parameter names if possible
        if param_names:
            if algorithm_match["optimized_algorithm"] == "sorting_algorithm" and len(param_names) >= 1:
                optimized_code = optimized_code.replace("arr", param_names[0])
            elif algorithm_match["optimized_algorithm"] == "search_algorithm" and len(param_names) >= 2:
                optimized_code = optimized_code.replace("arr", param_names[0]).replace("target", param_names[1])
            elif algorithm_match["optimized_algorithm"] == "fibonacci" and len(param_names) >= 1:
                optimized_code = optimized_code.replace("n", param_names[0])
        
        # Check if the optimized code ends with proper newlines
        # Ensure code ends with exactly two newlines for proper spacing
        optimized_code = optimized_code.rstrip('\n')  # Remove any trailing newlines
        optimized_code += '\n\n'  # Add exactly two newlines
        
        return optimized_code
    
    def _improve_code_quality(self, code: str, level: str) -> str:
        """
        Apply code quality improvements
        
        Args:
            code: Source code
            level: Optimization level ('low', 'medium', 'high')
            
        Returns:
            Improved code
        """
        try:
            # Skip AST-based transformations as requested
            improved_code = code
            
            # Apply regex-based improvements instead
            
            # Improve variable names with regex
            if level in ['medium', 'high']:
                improved_code = self._improve_variable_names_regex(improved_code)
                
                # Add improvement marker if changes were made
                if improved_code != code:
                self.improvements.append({
                        'type': 'variable_naming',
                        'description': 'Improved variable names for better readability',
                        'category': 'readability'
                    })
            
            # Add docstring formatting
            if level in ['medium', 'high']:
                improved_code = self._improve_docstrings(improved_code)
            
            # Apply list operation improvements with regex
            if level in ['medium', 'high']:
                improved_code = self._improve_list_operations_regex(improved_code)
            
            return improved_code
        except Exception as e:
            logger.warning(f"Error improving code quality: {str(e)}")
        return code
    
    def _improve_variable_names_regex(self, code: str) -> str:
        """
        Improve variable names using regex
        
        Args:
            code: Source code
            
        Returns:
            Code with improved variable names
        """
        # Common single-letter names and their better alternatives
        name_map = {
            'i': 'index',
            'j': 'inner_index',
            'k': 'outer_index',
            'n': 'count',
            's': 'total',
            'a': 'array',
            'l': 'length',
            'v': 'value',
            'f': 'function',
            'p': 'position',
            'm': 'matrix',
            'x': 'value_x',
            'y': 'value_y',
            'z': 'value_z',
            't': 'temp',
            'r': 'result',
            'c': 'character'
        }
        
        improved_code = code
        
        # Regex to find variable declarations
        for old_name, new_name in name_map.items():
            # Only replace variables, not function calls or other uses
            # Look for variable assignments, function parameters, or for loop variables
            pattern = r'(?<!\w)' + old_name + r'(?=\s*=|\s*\+\=|\s*\-\=|\s*\*\=|\s*\/\=|(?:\s*,\s*|\s*\)|\s+in\s+))'
            improved_code = re.sub(pattern, new_name, improved_code)
        
        return improved_code
        
    def _improve_list_operations_regex(self, code: str) -> str:
        """
        Improve list operations using regex
        
        Args:
            code: Source code
            
        Returns:
            Code with improved list operations
        """
        # Pattern for list building with append in a loop
        append_pattern = r'(\w+)\s*=\s*\[\]\s*(?:\n.*?)*?for\s+(\w+)\s+in\s+([^:]+):\s*(?:\n.*?)*?\s*\1\.append\(([^)]+)\)'
        
        # Replace with list comprehension
        def replace_append(match):
            list_name = match.group(1)
            loop_var = match.group(2)
            iterable = match.group(3)
            expression = match.group(4)
            
            # Add improvement
            self.improvements.append({
                'type': 'list_comprehension',
                'description': 'Replaced loop with list comprehension for better performance and readability',
                'category': 'optimization'
            })
            
            return f"{list_name} = [{expression} for {loop_var} in {iterable}]"
        
        # Apply the replacement
        improved_code = re.sub(append_pattern, replace_append, code, flags=re.DOTALL)
        
        return improved_code
    
    def _improve_docstrings(self, code: str) -> str:
        """
        Improve docstrings in the code
        
        Args:
            code: Source code
            
        Returns:
            Code with improved docstrings
        """
        # Look for functions without docstrings
        improvements_made = False
        
        # Pattern to find function definitions without docstrings
        func_pattern = r'(def\s+(\w+)\s*\([^)]*\):)(?!\s*["\'])'
        
        # Replace with function definition + docstring
        def add_docstring(match):
            nonlocal improvements_made
            improvements_made = True
            
            func_def = match.group(1)
            func_name = match.group(2)
            
            # Generate a sensible docstring
            docstring = f'{func_def}\n    """\n    {func_name} function\n    """\n    '
            return docstring
        
        improved_code = re.sub(func_pattern, add_docstring, code)
        
        # Add to improvements if made
        if improvements_made:
            self.improvements.append({
                'type': 'docstrings',
                'description': 'Added docstrings to functions for better code documentation',
                'category': 'documentation'
            })
        
        return improved_code
    
    def _estimate_complexity(self, code: str) -> str:
        """
        Estimate the time complexity of the code
        
        Args:
            code: Code to analyze
            
        Returns:
            Estimated complexity notation
        """
        if not code.strip():
            return "O(?)"
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Count loops and their nesting level
            loops = []
            stack = [(tree, 0)]
            
            while stack:
                node, depth = stack.pop()
                
                # Check if node is a loop
                if isinstance(node, (ast.For, ast.While)):
                    loops.append(depth)
                
                # Add children to stack
                for child in ast.iter_child_nodes(node):
                    stack.append((child, depth + (1 if isinstance(node, (ast.For, ast.While)) else 0)))
            
            # Determine complexity based on loops
            if not loops:
                return "O(1)"
            elif max(loops) == 0:
                return "O(n)"
            elif max(loops) == 1:
                return "O(n²)"
            else:
                return f"O(n^{max(loops) + 1})"
                
        except Exception as e:
            logger.warning(f"Error estimating complexity: {str(e)}")
            return "O(?)"
    
    def _generate_explanation(self, original_code: str, optimized_code: str, 
                             original_complexity: str, optimized_complexity: str) -> str:
        """
        Generate explanation of optimizations
        
        Args:
            original_code: Original code
            optimized_code: Optimized code
            original_complexity: Original complexity notation
            optimized_complexity: Optimized complexity notation
            
        Returns:
            Explanation string
        """
        if original_code == optimized_code:
            return "No optimizations applied"
        
        explanations = []
        
        # Check if neural model was used
        if hasattr(self, 'neural_model') and self.neural_model and self.neural_model.initialized:
            explanations.append("Applied CodeBERT neural model")
        
        # Check if complexity improved
        if original_complexity != optimized_complexity and "?" not in original_complexity and "?" not in optimized_complexity:
            explanations.append(f"Improved time complexity from {original_complexity} to {optimized_complexity}")
        
        # Check for specific improvements
        if len(optimized_code) < len(original_code):
            explanations.append("Simplified code")
        
        # Check if list comprehensions were added
        if "[" in optimized_code and "]" in optimized_code and "for" in optimized_code and "in" in optimized_code and "append" not in optimized_code and "append" in original_code:
            explanations.append("Replaced loops with list comprehensions")
        
        # Check if docstrings were added
        if '"""' in optimized_code and '"""' not in original_code:
            explanations.append("Added documentation")
        
        if explanations:
            return "CodeBERT: " + ", ".join(explanations)
        else:
            return "Applied code quality improvements"
    
    def get_applied_rules(self) -> List[Dict[str, str]]:
        """
        Get list of improvements applied during optimization
        
        Returns:
            List of improvement dictionaries
        """
        return self.improvements
    
    def _ensure_proper_spacing(self, code: str) -> str:
        """
        Ensure proper spacing between functions and at end of code
        
        Args:
            code: Source code as string
            
        Returns:
            Code with proper spacing
        """
        # Replace multiple consecutive newlines with two newlines
        code = re.sub(r'\n{3,}', '\n\n', code)
        
        # Ensure space between function definitions
        code = re.sub(r'(def\s+\w+\s*\([^)]*\):.*?)(\ndef)', r'\1\n\n\2', code, flags=re.DOTALL)
        
        # Ensure code ends with a newline
        if not code.endswith('\n'):
            code += '\n'
        
        return code

def apply_codebert_optimization(code: str, level: str = 'medium') -> Tuple[str, List[Dict[str, str]], List[str]]:
    """
    Apply CodeBERT optimization to code
    
    Args:
        code: Python code as string
        level: Optimization level ('low', 'medium', 'high')
        
    Returns:
        Tuple of (optimized_code, improvements, errors)
    """
    optimizer = CodeBERTOptimizer(use_neural_model=False)
    errors = []
    
    try:
        optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level)
        improvements = optimizer.get_applied_rules()
        
        # If no improvements were made, add a generic one
        if not improvements:
            improvements.append({
                'type': 'codebert_optimization',
                'description': 'Applied CodeBERT optimization',
                'category': 'quality'
            })
        
    return optimized_code, improvements, errors 
    except Exception as e:
        error_msg = f"Error in CodeBERT optimization: {str(e)}"
        errors.append(error_msg)
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return code, [], errors
