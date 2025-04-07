"""
Data Processing Module for EFFICODE-ACRR

This module handles loading and preprocessing of algorithm datasets:
- Loading CSV data into pandas DataFrames
- Cleaning and standardizing code
- Extracting features from code
- Normalizing complexity labels
- Splitting data for training, validation, and testing
- Saving processed data

"""

import os
import pandas as pd
import numpy as np
import re
import ast
import json
import logging
from typing import Dict, List, Tuple, Union, Optional, Any
import sys
from sklearn.model_selection import train_test_split
import warnings

# Local imports
from utils import count_code_elements, detect_algorithm_type, is_recursive, identify_data_structures, parse_python_code

# Configure warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_processing.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data processing tasks for code optimization
    """
    
    def __init__(self):
        """Initialize the data processor"""
        logger.info("DataProcessor initialized")
        
    def clean_code(self, code: str) -> str:
        """
        Clean and normalize the code
        
        Args:
            code: The Python code to clean
            
        Returns:
            Cleaned code
        """
        if not code:
            return ""
            
        # Remove excessive blank lines (more than 2 consecutive)
        lines = code.split('\n')
        cleaned_lines = []
        blank_count = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
                if blank_count <= 2:  # Allow up to 2 consecutive blank lines
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines)
        
    def parse_code(self, code: str) -> Optional[ast.AST]:
        """
        Parse code into AST
        
        Args:
            code: The Python code to parse
            
        Returns:
            AST or None if parsing fails
        """
        try:
            return ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Syntax error in code: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing code: {e}")
            return None
            
    def extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract functions from code
        
        Args:
            code: The Python code to analyze
            
        Returns:
            List of function metadata
        """
        functions = []
        
        try:
            tree = self.parse_code(code)
            if not tree:
                return functions
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'line_start': node.lineno,
                        'line_end': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node))
                    })
        except Exception as e:
            logger.error(f"Error extracting functions: {e}")
            
        return functions

def main():
    """Main function to run the data processing pipeline"""
    try:
        # Get paths relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_dir = os.path.join(project_root, 'data', 'raw')
        processed_dir = os.path.join(project_root, 'data', 'processed')
        
        # Initialize processor
        processor = DataProcessor()
        
        # Run pipeline
        df = processor.process_pipeline()
        
        print(f"Processing complete. Dataset shape: {df.shape}")
        return 0
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())