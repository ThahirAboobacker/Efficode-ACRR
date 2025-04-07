"""
Feature Extraction Module for EFFICODE-ACRR

This module extracts features from Python code snippets for algorithm optimization:
- Syntactic features (code length, tokens, structure)
- Algorithmic features (loops, conditions, recursion, etc.)
- Data structure usage
- Complexity indicators

These features are used for training ML models to predict and optimize algorithms.
"""

import ast
import re
import io
import tokenize
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from collections import Counter, defaultdict

# Local imports
from utils import (
    parse_python_code, 
    count_code_elements, 
    detect_algorithm_type, 
    is_recursive, 
    identify_data_structures as utils_identify_data_structures
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """
    Extracts features from code for analysis
    """
    
    def __init__(self):
        """Initialize the feature extractor"""
        logger.info("FeatureExtractor initialized")
        
    def extract_features(self, code: str) -> Dict[str, Any]:
        """
        Extract features from code
        
        Args:
            code: The Python code to analyze
            
        Returns:
            Dictionary of extracted features
        """
        features = {
            'num_lines': 0,
            'num_functions': 0,
            'num_classes': 0,
            'num_loops': 0,
            'max_loop_depth': 0,
            'num_conditionals': 0,
            'uses_comprehensions': False,
            'uses_recursion': False
        }
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Count lines
            features['num_lines'] = len(code.splitlines())
            
            # Count functions and classes
            features['num_functions'] = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            features['num_classes'] = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            
            # Count loops
            features['num_loops'] = sum(1 for node in ast.walk(tree) 
                                     if isinstance(node, (ast.For, ast.While)))
            
            # Check for list/dict/set comprehensions
            features['uses_comprehensions'] = any(
                isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp))
                for node in ast.walk(tree)
            )
            
            # Check for conditionals
            features['num_conditionals'] = sum(1 for node in ast.walk(tree)
                                           if isinstance(node, ast.If))
            
            # Analyze loop depth
            features['max_loop_depth'] = self._calculate_max_loop_depth(tree)
            
            # Check for recursion
            function_calls = {}
            self._find_function_calls(tree, function_calls)
            features['uses_recursion'] = self._check_recursion(function_calls)
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            
        return features
    
    def _calculate_max_loop_depth(self, tree: ast.AST) -> int:
        """Calculate the maximum loop nesting depth in the code"""
        max_depth = 0
        
        class LoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_depth = 0
                self.max_depth = 0
                
            def visit_For(self, node):
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                # Visit children
                self.generic_visit(node)
                self.current_depth -= 1
                
            def visit_While(self, node):
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                # Visit children
                self.generic_visit(node)
                self.current_depth -= 1
        
        visitor = LoopVisitor()
        visitor.visit(tree)
        return visitor.max_depth
    
    def _find_function_calls(self, tree: ast.AST, function_calls: Dict[str, List[str]]) -> None:
        """Find all function calls in the code"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name
                calls = []
                
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name):
                        calls.append(subnode.func.id)
                
                function_calls[function_name] = calls
    
    def _check_recursion(self, function_calls: Dict[str, List[str]]) -> bool:
        """Check if the code contains recursive function calls"""
        for func_name, calls in function_calls.items():
            if func_name in calls:
                return True
        return False

    def extract_code_features(self, code: str) -> Dict[str, Any]:
        """
        Extract comprehensive features from a code snippet
        
        Args:
            code: Python code as string
            
        Returns:
            Dictionary of extracted features
        """
        self.processed_samples += 1
        
        # Basic validation
        if not isinstance(code, str) or not code.strip():
            logger.debug("Empty or invalid code provided")
            return self._get_default_features()
        
        try:
            # Parse code into AST
            parsed_ast = parse_python_code(code)
            
            if parsed_ast is None:
                self.parse_errors += 1
                # Fall back to regex-based extraction
                return self._extract_features_regex(code)
            
            # Extract AST-based features
            ast_features = self._extract_ast_features(parsed_ast, code)
            
            # Extract token-based features
            token_features = self._extract_token_features(code)
            
            # Extract complexity indicators
            complexity_features = self._extract_complexity_indicators(parsed_ast, code)
            
            # Extract code metrics using utility function
            code_metrics = count_code_elements(code)
            
            # Combine all features
            features = {
                **ast_features,
                **token_features,
                **complexity_features,
                'code_lines': code_metrics['lines'],
                'code_chars': code_metrics['chars'],
                'imports': code_metrics['imports'],
                'parse_error': False
            }
            
            return features
            
        except Exception as e:
            self.parse_errors += 1
            logger.debug(f"Error in extract_code_features: {str(e)}")
            # Fall back to regex-based extraction
            return self._extract_features_regex(code)
    
    def _extract_ast_features(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """
        Extract features from AST
        
        Args:
            tree: AST of the code
            code: Original code string
            
        Returns:
            Dictionary of AST-based features
        """
        # Initialize counters
        node_counts = {feature: 0 for node_type, feature in self.tracked_nodes.items()}
        
        # Additional metrics
        max_depth = self._measure_ast_depth(tree)
        function_names = []
        
        # Track recursion information
        recursion_detected = False
        
        # Process AST nodes
        for node in ast.walk(tree):
            # Count node types we're tracking
            for node_type, feature in self.tracked_nodes.items():
                if isinstance(node, node_type):
                    node_counts[feature] += 1
            
            # Extract function names
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)
        
        # Check for recursion using utility function
        is_recursive_code = is_recursive(code)
        
        # Measure loop nesting
        loop_nesting = self._measure_loop_nesting(tree)
        
        # Data structures used - using the imported utility function
        data_structures = utils_identify_data_structures(code)
        
        # Create feature dictionary
        features = {
            'ast_node_count': sum(node_counts.values()),
            'max_ast_depth': max_depth,
            'loop_count': node_counts['for_loops'] + node_counts['while_loops'],
            'for_loop_count': node_counts['for_loops'],
            'while_loop_count': node_counts['while_loops'],
            'function_count': node_counts['function_defs'],
            'class_count': node_counts['class_defs'],
            'loop_nesting_depth': loop_nesting,
            'if_count': node_counts['if_statements'],
            'comprehension_count': (
                node_counts['list_comprehensions'] + 
                node_counts['dict_comprehensions'] + 
                node_counts['set_comprehensions']
            ),
            'has_recursion': 1 if is_recursive_code else 0,
            'data_structures': ','.join(data_structures)
        }
        
        # Add one-hot encoded data structure features
        for ds in ['list', 'dict', 'set', 'tuple', 'queue/stack', 'heap']:
            features[f'uses_{ds}'] = 1 if ds in data_structures else 0
        
        return features
    
    def _extract_token_features(self, code: str) -> Dict[str, Any]:
        """
        Extract features based on code tokenization
        
        Args:
            code: Python code string
            
        Returns:
            Dictionary of token-based features
        """
        try:
            # Tokenize the code
            tokens = []
            code_io = io.BytesIO(code.encode('utf-8'))
            
            for tok in tokenize.tokenize(code_io.readline):
                # Skip comments, newlines and indentation
                if tok.type not in (tokenize.COMMENT, tokenize.NEWLINE, tokenize.NL, 
                                  tokenize.INDENT, tokenize.DEDENT):
                    tokens.append(tok.string)
            
            # Calculate token statistics
            token_count = len(tokens)
            unique_tokens = len(set(tokens))
            avg_token_length = sum(len(t) for t in tokens) / max(1, token_count)
            
            # Count comments
            comment_count = code.count('#') + code.count('"""') + code.count("'''")
            
            # Count operators
            operators = ['+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=', 'and', 'or', 'not']
            operator_count = sum(tokens.count(op) for op in operators)
            
            # Get tokens by type
            token_types = Counter()
            code_io = io.BytesIO(code.encode('utf-8'))
            
            for tok in tokenize.tokenize(code_io.readline):
                token_types[tokenize.tok_name[tok.type]] += 1
            
            return {
                'token_count': token_count,
                'unique_token_count': unique_tokens,
                'avg_token_length': avg_token_length,
                'comment_count': comment_count,
                'operator_count': operator_count,
                'name_token_count': token_types.get('NAME', 0),
                'op_token_count': token_types.get('OP', 0),
                'num_token_count': token_types.get('NUMBER', 0)
            }
            
        except Exception as e:
            logger.debug(f"Error in token extraction: {str(e)}")
            # Return default values
            return {
                'token_count': 0,
                'unique_token_count': 0,
                'avg_token_length': 0,
                'comment_count': 0,
                'operator_count': 0,
                'name_token_count': 0,
                'op_token_count': 0,
                'num_token_count': 0
            }
    
    def _extract_complexity_indicators(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """
        Extract indicators of algorithmic complexity
        
        Args:
            tree: AST of the code
            code: Original code string
            
        Returns:
            Dictionary of complexity indicators
        """
        # Initialize indicators
        has_nested_loops = False
        has_divide_conquer = False
        algorithm_type = detect_algorithm_type(code)
        
        # Count loops
        for_loops = [node for node in ast.walk(tree) if isinstance(node, ast.For)]
        while_loops = [node for node in ast.walk(tree) if isinstance(node, ast.While)]
        
        # Check for nested loops
        loop_nesting = self._measure_loop_nesting(tree)
        has_nested_loops = loop_nesting > 1
        
        # Check for recursion
        has_recursion = is_recursive(code)
        
        # Identify algorithmic pattern
        if has_nested_loops:
            pattern = 'iterative_nested'
        elif has_recursion:
            # Check for divide and conquer pattern
            divide_conquer_indicators = 0
            
            # Look for recursion with splitting of input
            for func in [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]:
                for node in ast.walk(func):
                    # Look for operations that divide input size
                    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv)):
                        divide_conquer_indicators += 1
                    
                    # Look for slicing
                    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
                        divide_conquer_indicators += 1
            
            # If we found splitting operations in a recursive function
            if divide_conquer_indicators > 0:
                pattern = 'recursive_divide_conquer'
                has_divide_conquer = True
            else:
                pattern = 'recursive'
        elif for_loops or while_loops:
            pattern = 'iterative_simple'
        else:
            pattern = 'constant'
        
        # Check for binary search pattern (log n complexity)
        if 'search' in algorithm_type and 'binary' in code.lower():
            pattern = 'logarithmic'
        
        return {
            'has_nested_loops': 1 if has_nested_loops else 0,
            'has_divide_conquer': 1 if has_divide_conquer else 0,
            'algorithm_pattern': pattern,
            'complexity_class': self.complexity_patterns.get(pattern, 'Unknown'),
            'algorithm_type': algorithm_type
        }
    
    def _measure_ast_depth(self, node: ast.AST) -> int:
        """
        Measure the maximum depth of the AST
        
        Args:
            node: AST node to measure
            
        Returns:
            Maximum depth
        """
        if not hasattr(node, 'body'):
            return 0
        
        max_child_depth = 0
        for child in ast.iter_child_nodes(node):
            child_depth = self._measure_ast_depth(child)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth + 1
    
    def _measure_loop_nesting(self, tree: ast.AST) -> int:
        """
        Measure the maximum nesting depth of loops
        
        Args:
            tree: AST to analyze
            
        Returns:
            Maximum loop nesting depth
        """
        max_depth = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # Start with depth 1 for this loop
                current_depth = 1
                
                # Check for nested loops
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child != node:
                        current_depth += 1
                
                max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    def _extract_features_regex(self, code: str) -> Dict[str, Any]:
        """
        Extract features using regex when AST parsing fails
        
        Args:
            code: Python code string
            
        Returns:
            Dictionary of extracted features
        """
        # Count loops
        for_loops = len(re.findall(r'\bfor\b', code))
        while_loops = len(re.findall(r'\bwhile\b', code))
        
        # Count functions and classes
        functions = len(re.findall(r'\bdef\s+\w+\s*\(', code))
        classes = len(re.findall(r'\bclass\s+\w+', code))
        
        # Count if statements
        if_statements = len(re.findall(r'\bif\b', code))
        
        # Check for recursion indicators
        if functions > 0:
            # Very basic recursion detection using regex
            # Extract function names
            function_names = re.findall(r'def\s+(\w+)\s*\(', code)
            
            # Check if any function calls itself
            has_recursion = 0
            for func_name in function_names:
                pattern = r'\b' + re.escape(func_name) + r'\s*\('
                # Exclude the definition itself
                rest_of_code = re.sub(r'def\s+' + re.escape(func_name) + r'\s*\(', '', code)
                if re.search(pattern, rest_of_code):
                    has_recursion = 1
                    break
        else:
            has_recursion = 0
        
        # Estimate algorithm pattern
        if for_loops > 1 or while_loops > 1:
            # Check for nested loops
            nested_loops = 0
            lines = code.split('\n')
            indentation_levels = {}
            
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                if stripped.startswith(('for ', 'while ')):
                    indent = len(line) - len(stripped)
                    indentation_levels[i] = indent
            
            # Check for increasing indentation levels
            for i in range(len(lines) - 1):
                if i in indentation_levels and i+1 in indentation_levels:
                    if indentation_levels[i+1] > indentation_levels[i]:
                        nested_loops = 1
                        break
            
            if nested_loops:
                algorithm_pattern = 'iterative_nested'
            else:
                algorithm_pattern = 'iterative_simple'
        elif has_recursion:
            algorithm_pattern = 'recursive'
        elif for_loops > 0 or while_loops > 0:
            algorithm_pattern = 'iterative_simple'
        else:
            algorithm_pattern = 'constant'
        
        # Use utility function to detect data structures
        data_structures = utils_identify_data_structures(code)
        
        # Count code elements using utility function
        code_metrics = count_code_elements(code)
        
        # Return extracted features
        features = {
            'loop_count': for_loops + while_loops,
            'for_loop_count': for_loops,
            'while_loop_count': while_loops,
            'function_count': functions,
            'class_count': classes,
            'if_count': if_statements,
            'has_recursion': has_recursion,
            'algorithm_pattern': algorithm_pattern,
            'complexity_class': self.complexity_patterns.get(algorithm_pattern, 'Unknown'),
            'code_lines': code_metrics['lines'],
            'code_chars': code_metrics['chars'],
            'has_nested_loops': nested_loops,
            'data_structures': ','.join(data_structures),
            'token_count': 0,  # Default values for token features
            'unique_token_count': 0,
            'avg_token_length': 0,
            'parse_error': True
        }
        
        # Add one-hot encoded data structure features
        for ds in ['list', 'dict', 'set', 'tuple', 'queue/stack', 'heap']:
            features[f'uses_{ds}'] = 1 if ds in data_structures else 0
        
        return features
    
    def _get_default_features(self) -> Dict[str, Any]:
        """
        Return default features for invalid code
        
        Returns:
            Dictionary of default feature values
        """
        return {
            'loop_count': 0,
            'for_loop_count': 0, 
            'while_loop_count': 0,
            'function_count': 0,
            'class_count': 0,
            'if_count': 0,
            'loop_nesting_depth': 0,
            'has_recursion': 0,
            'algorithm_pattern': 'unknown',
            'complexity_class': 'Unknown',
            'code_lines': 0,
            'code_chars': 0,
            'token_count': 0,
            'unique_token_count': 0,
            'avg_token_length': 0,
            'has_nested_loops': 0,
            'data_structures': '',
            'uses_list': 0,
            'uses_dict': 0,
            'uses_set': 0,
            'uses_tuple': 0,
            'uses_queue/stack': 0,
            'uses_heap': 0,
            'parse_error': True
        }
    
    def extract_batch_features(self, codes: List[str]) -> pd.DataFrame:
        """
        Extract features from a batch of code snippets
        
        Args:
            codes: List of code strings
            
        Returns:
            DataFrame with extracted features
        """
        features_list = []
        
        total = len(codes)
        for i, code in enumerate(codes):
            features = self.extract_code_features(code)
            features_list.append(features)
            
            # Log progress
            if (i + 1) % 100 == 0 or i == total - 1:
                logger.info(f"Processed {i+1}/{total} code samples")
        
        # Convert to DataFrame
        df = pd.DataFrame(features_list)
        
        # Log statistics
        error_rate = (self.parse_errors / max(1, self.processed_samples)) * 100
        logger.info(f"Feature extraction complete: {self.processed_samples} samples, "
                  f"{self.parse_errors} parse errors ({error_rate:.1f}%)")
        
        return df
    
    def extract_df_features(self, df: pd.DataFrame, code_column: str = 'code') -> pd.DataFrame:
        """
        Extract features from code in a DataFrame column
        
        Args:
            df: DataFrame containing code
            code_column: Name of the column containing code
            
        Returns:
            DataFrame with extracted features
        """
        if code_column not in df.columns:
            alt_columns = ['clean_code', 'Code', 'input_code']
            for col in alt_columns:
                if col in df.columns:
                    code_column = col
                    logger.info(f"Using alternative code column: {col}")
                    break
            else:
                raise ValueError(f"No code column found. Available columns: {df.columns.tolist()}")
        
        # Extract features for each code snippet
        features_list = []
        
        total = len(df)
        for i, row in df.iterrows():
            code = row[code_column]
            features = self.extract_code_features(code)
            
            # Add original index
            features['original_index'] = i
            
            features_list.append(features)
            
            # Log progress
            if (i + 1) % 100 == 0 or i == total - 1:
                logger.info(f"Processed {i+1}/{total} code samples")
        
        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)
        
        # Log statistics
        error_rate = (self.parse_errors / max(1, self.processed_samples)) * 100
        logger.info(f"Feature extraction complete: {self.processed_samples} samples, "
                  f"{self.parse_errors} parse errors ({error_rate:.1f}%)")
        
        return features_df

# Functions for direct use without instantiating the class

def extract_code_features(code: str) -> Dict[str, Any]:
    """
    Extract features from a code snippet
    
    Args:
        code: Python code string
        
    Returns:
        Dictionary of code features
    """
    extractor = FeatureExtractor()
    return extractor.extract_code_features(code)

def count_loops(code: str) -> int:
    """
    Count the number of loops in code
    
    Args:
        code: Python code string
        
    Returns:
        Number of loops
    """
    try:
        tree = parse_python_code(code)
        if tree:
            for_loops = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.For))
            while_loops = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.While))
            return for_loops + while_loops
        else:
            # Fallback to regex if parsing fails
            for_count = len(re.findall(r'\bfor\b', code))
            while_count = len(re.findall(r'\bwhile\b', code))
            return for_count + while_count
    except:
        # Fallback to regex if anything fails
        for_count = len(re.findall(r'\bfor\b', code))
        while_count = len(re.findall(r'\bwhile\b', code))
        return for_count + while_count

def measure_nesting_depth(code: str) -> int:
    """
    Measure the maximum nesting depth of loops
    
    Args:
        code: Python code string
        
    Returns:
        Maximum nesting depth
    """
    try:
        tree = parse_python_code(code)
        if tree:
            extractor = FeatureExtractor()
            return extractor._measure_loop_nesting(tree)
        else:
            # Fallback to regex-based estimation
            lines = code.split('\n')
            max_indent = 0
            in_loop = False
            indent_level = 0
            
            for line in lines:
                stripped = line.lstrip()
                indent = len(line) - len(stripped)
                
                if stripped.startswith(('for ', 'while ')):
                    in_loop = True
                    indent_level = indent
                elif in_loop and indent > indent_level:
                    if stripped.startswith(('for ', 'while ')):
                        max_indent = max(max_indent, 2)
                
            return max_indent or (1 if in_loop else 0)
    except:
        return 0

def detect_recursion(code: str) -> bool:
    """
    Detect if code uses recursion
    
    Args:
        code: Python code string
        
    Returns:
        True if recursion is detected, False otherwise
    """
    return is_recursive(code)

def identify_data_structures_wrapper(code: str) -> List[str]:
    """
    Identify data structures used in code
    
    Args:
        code: Python code string
        
    Returns:
        List of data structure names
    """
    return utils_identify_data_structures(code)

def get_algorithm_complexity(code: str) -> str:
    """
    Estimate the algorithmic complexity class
    
    Args:
        code: Python code string
        
    Returns:
        Complexity class as a string
    """
    features = extract_code_features(code)
    return features['complexity_class']

if __name__ == "__main__":
    # Simple demonstration
    import sys
    
    if len(sys.argv) > 1:
        # Extract features from a file
        with open(sys.argv[1], 'r') as f:
            code = f.read()
        
        features = extract_code_features(code)
        print("Extracted Features:")
        for k, v in sorted(features.items()):
            print(f"{k}: {v}")
    else:
        # Simple test
        test_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
        """
        
        features = extract_code_features(test_code)
        print("Extracted Features for Bubble Sort:")
        for k, v in sorted(features.items()):
            print(f"{k}: {v}")