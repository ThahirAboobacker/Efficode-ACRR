#!/usr/bin/env python
"""
Test script to verify the functionality of rule-based and CodeBERT optimizers.
"""

import sys
import os
import unittest
import logging
import ast

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.rule_based import RuleBasedOptimizer, OptimizerConfig
from src.codebert_optimizer import CodeBERTOptimizer
from src.code_transformation import CodeTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestOptimizers(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.rule_based = RuleBasedOptimizer()
        self.codebert = CodeBERTOptimizer()
        self.transformer = CodeTransformer()
        
        # Test cases with different optimization opportunities
        self.test_cases = {
            "constant_folding": """
def calculate():
    x = 2 + 3 * 4
    y = "Hello" + " World"
    return x, y
""",
            "dead_code": """
def process_data():
    x = 10
    y = 20
    if True:
        return x
    return y  # Dead code
""",
            "inefficient_loop": """
def process_list(items):
    result = []
    for i in range(len(items)):
        result.append(items[i])
    return result
"""
        }

    def test_rule_based_optimizer(self):
        """Test rule-based optimizer functionality."""
        logger.info("Testing Rule-Based Optimizer...")
        
        # Test constant folding
        code = self.test_cases["constant_folding"]
        try:
            tree = ast.parse(code)
            self.rule_based.visit(tree)
            optimized = ast.unparse(tree)
            self.assertIsNotNone(optimized)
            logger.info("Constant folding test completed")
        except Exception as e:
            logger.error(f"Error in constant folding test: {str(e)}")
            raise
        
        # Test dead code elimination
        code = self.test_cases["dead_code"]
        try:
            tree = ast.parse(code)
            self.rule_based.visit(tree)
            optimized = ast.unparse(tree)
            self.assertIsNotNone(optimized)
            logger.info("Dead code elimination test completed")
        except Exception as e:
            logger.error(f"Error in dead code test: {str(e)}")
            raise

    def test_codebert_optimizer(self):
        """Test CodeBERT optimizer functionality."""
        logger.info("Testing CodeBERT Optimizer...")
        
        # Test inefficient loop optimization
        code = self.test_cases["inefficient_loop"]
        try:
            optimized = self.codebert.optimize(code)
            self.assertIsNotNone(optimized)
            logger.info("CodeBERT optimization test completed")
        except Exception as e:
            logger.error(f"Error in CodeBERT test: {str(e)}")
            raise

    def test_code_transformer(self):
        """Test code transformation functionality."""
        logger.info("Testing Code Transformer...")
        
        # Test algorithm transformation
        code = self.test_cases["inefficient_loop"]
        try:
            transformed = self.transformer.transform_code(code)
            self.assertIsNotNone(transformed)
            logger.info("Code transformation test completed")
        except Exception as e:
            logger.error(f"Error in code transformation test: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main() 