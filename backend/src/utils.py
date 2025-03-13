import ast
import logging
import os
import tempfile
import time
import traceback
import subprocess
import random
import numpy as np
import re
import pandas as pd
from typing import Tuple, Optional, List, Dict, Any

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configure logging for the application.
    
    Args:
        log_level: The logging level (default: INFO)
        log_file: Optional file path to write logs to
    
    Returns:
        Logger object
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler()  # Log to console
        ]
    )
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    
    logger = logging.getLogger('efficode')
    return logger

def parse_python_code(code: str) -> Optional[ast.AST]:
    """
    Safely parse Python code into an AST.
    
    Args:
        code: Python code as string
    
    Returns:
        AST object or None if parsing fails
    """
    try:
        parsed_ast = ast.parse(code)
        return parsed_ast
    except SyntaxError as e:
        logging.error(f"Syntax error while parsing code: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error parsing code: {str(e)}")
        return None

def extract_function_name(code: str) -> str:
    """
    Extract the main function name from code.
    
    Args:
        code: Python code as string
    
    Returns:
        Function name as string, or 'main' if not found
    """
    try:
        parsed = ast.parse(code)
        for node in ast.walk(parsed):
            if isinstance(node, ast.FunctionDef):
                return node.name
        return "main"  # Default function name if none found
    except:
        return "main"  # Default on error

def validate_code_equivalence(original: str, optimized: str, test_cases=None) -> Tuple[bool, str]:
    """
    Verify that the optimized code maintains the same functionality as the original.
    
    Args:
        original: Original code as string
        optimized: Optimized code as string
        test_cases: Optional list of test cases to evaluate
    
    Returns:
        Tuple of (is_equivalent, error_message)
    """
    # If no test cases provided, generate some random ones
    if test_cases is None:
        # Simple test case generation - can be improved based on code analysis
        test_cases = [
            [random.randint(0, 100) for _ in range(10)],  # Random integers
            list(range(20)),                             # Sequential
            list(range(20, 0, -1)),                      # Reverse order
            [random.randint(0, 1000) for _ in range(50)]  # Larger random
        ]
    
    # Create temporary Python files
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f_orig:
        f_orig.write(original)
        orig_path = f_orig.name
    
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f_opt:
        f_opt.write(optimized)
        opt_path = f_opt.name
    
    try:
        # Extract function name or use "main" as default
        func_name = extract_function_name(original)
        
        # Execute both functions with the same inputs and compare outputs
        for i, test_case in enumerate(test_cases):
            # Convert test case to string representation
            test_str = str(test_case)
            
            # Run original code
            cmd_orig = f'python -c "import sys; sys.path.append(\'.\'); from {os.path.basename(orig_path)[:-3]} import *; print(repr({func_name}({test_str})))"'
            result_orig = subprocess.run(cmd_orig, shell=True, capture_output=True, text=True, timeout=5)
            
            # Run optimized code
            cmd_opt = f'python -c "import sys; sys.path.append(\'.\'); from {os.path.basename(opt_path)[:-3]} import *; print(repr({func_name}({test_str})))"'
            result_opt = subprocess.run(cmd_opt, shell=True, capture_output=True, text=True, timeout=5)
            
            # Compare outputs
            if result_orig.stdout.strip() != result_opt.stdout.strip():
                return False, f"Different outputs for test case {i+1}:\nOriginal: {result_orig.stdout}\nOptimized: {result_opt.stdout}"
            
            # Check for errors
            if result_orig.returncode != 0 or result_opt.returncode != 0:
                return False, f"Error in execution for test case {i+1}:\nOriginal: {result_orig.stderr}\nOptimized: {result_opt.stderr}"
        
        # All tests passed
        return True, "Code functionality equivalent"
    
    except subprocess.TimeoutExpired:
        return False, "Execution timed out - possible infinite loop"
    except Exception as e:
        return False, f"Error validating code: {str(e)}"
    
    finally:
        # Clean up temporary files
        try:
            os.unlink(orig_path)
            os.unlink(opt_path)
        except:
            pass

def measure_execution_time(code: str, iterations=5) -> Tuple[float, float, str]:
    """
    Measure the execution time of a code snippet.
    
    Args:
        code: Python code as string
        iterations: Number of times to run the code for averaging
    
    Returns:
        Tuple of (avg_time, std_dev, error_message)
    """
    # Extract function name
    func_name = extract_function_name(code)
    
    # Create a temporary Python file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        # Wrap the code in a function for timing
        wrapper_code = f"""
import time
import random
import numpy as np
import sys

{code}

# Time measurement with random data
def measure():
    # Generate random test data (adjust based on algorithm type)
    data = [random.randint(0, 1000) for _ in range(1000)]
    
    start = time.time()
    {func_name}(data)
    end = time.time()
    return end - start

# Warmup
for _ in range(2):
    try:
        measure()
    except Exception as e:
        print(f"Error during warmup: {{str(e)}}")
        sys.exit(1)

# Actual measurements
times = []
for _ in range({iterations}):
    try:
        times.append(measure())
    except Exception as e:
        print(f"Error during measurement: {{str(e)}}")
        sys.exit(1)

if times:
    print(f"{{np.mean(times)}},{{np.std(times)}}")
else:
    print("0.0,0.0")
"""
        f.write(wrapper_code)
        temp_path = f.name
    
    try:
        # Execute the code with a timeout to prevent infinite loops
        result = subprocess.run(['python', temp_path], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return 0.0, 0.0, f"Error executing code: {result.stderr}"
        
        # Parse the output
        try:
            mean_time, std_dev = map(float, result.stdout.strip().split(','))
            return mean_time, std_dev, ""
        except ValueError:
            return 0.0, 0.0, f"Error parsing timing results: {result.stdout}"
    
    except subprocess.TimeoutExpired:
        return 0.0, 0.0, "Execution timed out - possible infinite loop"
    except Exception as e:
        return 0.0, 0.0, f"Error measuring execution time: {str(e)}"
    
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except:
            pass

def count_code_elements(code: str) -> Dict[str, int]:
    """
    Count various elements in the code for metrics.
    
    Args:
        code: Python code as string
    
    Returns:
        Dictionary with counts of various code elements
    """
    result = {
        'lines': len(code.strip().split('\n')),
        'chars': len(code),
        'loops': len(re.findall(r'\b(for|while)\b', code)),
        'conditionals': len(re.findall(r'\b(if|elif|else)\b', code)),
        'functions': len(re.findall(r'\bdef\s+\w+\s*\(', code)),
        'classes': len(re.findall(r'\bclass\s+\w+', code)),
        'imports': len(re.findall(r'\b(import|from)\b', code))
    }
    
    # Count nested loops
    code_without_strings = re.sub(r'["\'].*?["\']', '', code)
    indentation_pattern = re.compile(r'^(\s*)(for|while)', re.MULTILINE)
    matches = indentation_pattern.findall(code_without_strings)
    
    if matches:
        max_indent = max(len(m[0]) for m in matches)
        result['max_loop_depth'] = max_indent // 4 + 1  # Assuming 4 spaces per indent
    else:
        result['max_loop_depth'] = 0
    
    return result

def detect_algorithm_type(code: str) -> str:
    """
    Attempt to detect the type of algorithm in the code.
    
    Args:
        code: Python code as string
    
    Returns:
        Algorithm type as string (e.g., 'sorting', 'search', etc.)
    """
    code_lower = code.lower()
    
    # Look for keywords that might indicate algorithm type
    if any(word in code_lower for word in ['sort', 'bubble', 'quick', 'merge', 'heap']):
        return 'sorting'
    elif any(word in code_lower for word in ['search', 'find', 'locate']):
        return 'search'
    elif any(word in code_lower for word in ['graph', 'node', 'edge', 'vertex']):
        return 'graph'
    elif any(word in code_lower for word in ['tree', 'bst', 'binary search tree']):
        return 'tree'
    elif any(word in code_lower for word in ['dynamic', 'dp', 'memoize', 'fibonacci']):
        return 'dynamic_programming'
    else:
        return 'unknown'

def is_recursive(code: str) -> bool:
    """
    Check if the code uses recursion.
    
    Args:
        code: Python code as string
    
    Returns:
        True if recursive, False otherwise
    """
    try:
        # Extract function name
        func_name = extract_function_name(code)
        
        # Look for function calling itself
        parsed = ast.parse(code)
        for node in ast.walk(parsed):
            if isinstance(node, ast.Call) and hasattr(node, 'func') and hasattr(node.func, 'id'):
                if node.func.id == func_name:
                    return True
        return False
    except:
        # Default to False if parsing fails
        return False

def generate_test_cases(algorithm_type: str, size=20) -> List[Any]:
    """
    Generate appropriate test cases based on algorithm type.
    
    Args:
        algorithm_type: Type of algorithm (e.g., 'sorting', 'search')
        size: Size of test data
    
    Returns:
        List of test cases
    """
    test_cases = []
    
    if algorithm_type == 'sorting':
        # For sorting algorithms
        test_cases.append([random.randint(0, 100) for _ in range(size)])  # Random
        test_cases.append(list(range(size)))                              # Already sorted
        test_cases.append(list(range(size, 0, -1)))                       # Reverse sorted
        test_cases.append([random.randint(0, 5) for _ in range(size)])    # Few unique values
    
    elif algorithm_type == 'search':
        # For search algorithms
        data = [random.randint(0, 100) for _ in range(size)]
        test_cases.append((data, random.choice(data)))  # Existing element
        test_cases.append((data, -1))                   # Non-existing element
        
        sorted_data = sorted([random.randint(0, 100) for _ in range(size)])
        test_cases.append((sorted_data, random.choice(sorted_data)))  # For binary search
    
    elif algorithm_type == 'graph':
        # For graph algorithms (simple adjacency list)
        graph = {i: [j for j in range(size) if random.random() > 0.7] for i in range(size)}
        test_cases.append((graph, 0, size-1))  # Start, end nodes
    
    else:
        # Default test cases
        test_cases.append([random.randint(0, 100) for _ in range(size)])
        test_cases.append(list(range(size)))
    
    return test_cases

def identify_data_structures(code: str) -> List[str]:
    """
    Identify data structures used in the code.
    
    Args:
        code: Python code as string
    
    Returns:
        List of identified data structures
    """
    structures = []
    
    # Look for common data structure patterns
    if re.search(r'\[\s*\]|\blist\s*\(', code):
        structures.append('list')
    if re.search(r'\{\s*\}|\bdict\s*\(', code):
        structures.append('dict')
    if re.search(r'\(\s*\)|\btuple\s*\(', code):
        structures.append('tuple')
    if re.search(r'\bset\s*\(', code):
        structures.append('set')
    if re.search(r'\bdeque\s*\(|\bQueue\s*\(|\bStack\s*\(', code):
        structures.append('queue/stack')
    if re.search(r'\bheap\w+\s*\(|\bpriority_queue', code):
        structures.append('heap')
    if re.search(r'\bNode\b|\bTree\b|\bGraph\b', code):
        structures.append('custom_structure')
    
    return structures if structures else ['unknown']

def load_algorithm_dataset(dataset_path: str) -> pd.DataFrame:
    """
    Load and process an algorithm dataset from CSV.
    
    Args:
        dataset_path: Path to the CSV dataset file
    
    Returns:
        DataFrame containing the processed dataset
    """
    try:
        # Read the CSV file
        df = pd.read_csv(dataset_path)
        
        # Clean and process the data
        # Convert code columns to string type
        code_columns = ['Code', 'Alternative Code']
        for col in code_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
                # Remove markdown code block markers if present
                df[col] = df[col].apply(lambda x: x.replace('```python', '').replace('```', '').strip())
        
        # Convert boolean columns
        bool_columns = ['recursion_used', 'is_optimized']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        # Convert numeric columns
        numeric_columns = ['code_length', 'code_tokens', 'loop_count', 'loop_nesting_depth']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        logging.error(f"Error loading dataset {dataset_path}: {str(e)}")
        raise

def get_dataset_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate statistics for an algorithm dataset.
    
    Args:
        df: DataFrame containing the algorithm dataset
    
    Returns:
        Dictionary containing various statistics about the dataset
    """
    stats = {
        'total_samples': len(df),
        'algorithm_types': df['Code Type'].unique().tolist(),
        'optimization_stats': {
            'optimized': df['is_optimized'].sum(),
            'not_optimized': (~df['is_optimized']).sum()
        },
        'complexity_stats': {
            'time_complexity': df['Time Complexity'].value_counts().to_dict(),
            'space_complexity': df['Space Complexity'].value_counts().to_dict()
        },
        'code_metrics': {
            'avg_code_length': df['code_length'].mean(),
            'avg_tokens': df['code_tokens'].mean(),
            'avg_loop_count': df['loop_count'].mean(),
            'avg_nesting_depth': df['loop_nesting_depth'].mean()
        }
    }
    
    return stats