#!/usr/bin/env python
"""
Test script for EFFICODE-ACRR main functionality.
This script tests various aspects of the code optimization system.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

from main import (
    optimize_code,
    OptimizationConfig,
    validate_python_code,
    load_code_from_file
)
from data_processing import DataProcessor

class TestEfficodeACRR(unittest.TestCase):
    """Test cases for EFFICODE-ACRR functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create a temporary directory for test files
        cls.test_dir = tempfile.mkdtemp()
        cls.test_files = {}
        
        # Initialize data processor
        cls.data_processor = DataProcessor(
            raw_dir=os.path.join(cls.test_dir, 'raw'),
            processed_dir=os.path.join(cls.test_dir, 'processed')
        )
        
        # Create test code files
        cls.test_files['bubble_sort'] = os.path.join(cls.test_dir, 'bubble_sort.py')
        with open(cls.test_files['bubble_sort'], 'w') as f:
            f.write('''def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

if __name__ == "__main__":
    test_array = [64, 34, 25, 12, 22, 11, 90]
    sorted_array = bubble_sort(test_array)
    print(f"Sorted array: {sorted_array}")''')
        
        cls.test_files['invalid_syntax'] = os.path.join(cls.test_dir, 'invalid_syntax.py')
        with open(cls.test_files['invalid_syntax'], 'w') as f:
            f.write('''def invalid_function(
    print("Missing closing parenthesis"''')
        
        cls.test_files['complex_code'] = os.path.join(cls.test_dir, 'complex_code.py')
        with open(cls.test_files['complex_code'], 'w') as f:
            f.write('''def complex_function(data):
    result = []
    for item in data:
        if isinstance(item, (list, tuple)):
            for subitem in item:
                if subitem > 0:
                    result.append(subitem * 2)
        elif item > 0:
            result.append(item)
    return sum(result) / len(result) if result else 0

def process_data(data):
    processed = []
    for item in data:
        if isinstance(item, dict):
            processed.extend(item.values())
        else:
            processed.append(item)
    return complex_function(processed)''')
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.test_dir)
    
    def test_basic_optimization(self):
        """Test basic code optimization functionality."""
        # Load test code
        code = load_code_from_file(self.test_files['bubble_sort'])
        
        # Create configuration
        config = OptimizationConfig(
            use_ml=True,
            use_fine_tuned=True,
            use_rule_based=True,
            verbose=True
        )
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertNotEqual(result.original_code, result.optimized_code)
        self.assertIsNotNone(result.explanation)
        self.assertIsNotNone(result.complexity_comparison)
        self.assertGreater(len(result.applied_rules), 0)
    
    def test_invalid_code(self):
        """Test handling of invalid Python code."""
        # Load invalid code
        code = load_code_from_file(self.test_files['invalid_syntax'])
        
        # Create configuration
        config = OptimizationConfig(verbose=True)
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Verify error handling
        self.assertIsNotNone(result)
        self.assertEqual(result.original_code, result.optimized_code)
        self.assertIn('error', result.complexity_comparison)
    
    def test_complex_code(self):
        """Test optimization of complex code."""
        # Load complex code
        code = load_code_from_file(self.test_files['complex_code'])
        
        # Create configuration
        config = OptimizationConfig(
            use_ml=True,
            use_fine_tuned=True,
            use_rule_based=True,
            verbose=True
        )
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertNotEqual(result.original_code, result.optimized_code)
        self.assertIsNotNone(result.explanation)
        self.assertIsNotNone(result.complexity_comparison)
    
    def test_dry_run(self):
        """Test dry run mode."""
        # Load test code
        code = load_code_from_file(self.test_files['bubble_sort'])
        
        # Create configuration with dry run
        config = OptimizationConfig(dry_run=True, verbose=True)
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Verify dry run behavior
        self.assertIsNotNone(result)
        self.assertEqual(result.original_code, result.optimized_code)
        self.assertEqual(result.explanation, "DRY RUN - Explanation generation skipped")
    
    def test_rule_based_only(self):
        """Test rule-based optimization only."""
        # Load test code
        code = load_code_from_file(self.test_files['bubble_sort'])
        
        # Create configuration with only rule-based optimization
        config = OptimizationConfig(
            use_ml=False,
            use_fine_tuned=False,
            use_rule_based=True,
            verbose=True
        )
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertNotEqual(result.original_code, result.optimized_code)
        self.assertIsNotNone(result.explanation)
    
    def test_code_validation(self):
        """Test code validation functionality."""
        # Test valid code
        valid_code = "def test(): return True"
        is_valid, error = validate_python_code(valid_code)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test invalid code
        invalid_code = "def test( return True"
        is_valid, error = validate_python_code(invalid_code)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_output_formats(self):
        """Test different output formats."""
        # Load test code
        code = load_code_from_file(self.test_files['bubble_sort'])
        
        # Create configuration
        config = OptimizationConfig(verbose=True)
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Test JSON output
        json_output = result.to_json()
        self.assertIsInstance(json_output, str)
        self.assertTrue(json_output.startswith('{'))
        
        # Test text output
        text_output = result.to_text()
        self.assertIsInstance(text_output, str)
        self.assertTrue("=== Code Optimization Results ===" in text_output)
    
    def test_file_loading(self):
        """Test code loading from file."""
        # Test loading existing file
        code = load_code_from_file(self.test_files['bubble_sort'])
        self.assertIsInstance(code, str)
        self.assertTrue(len(code) > 0)
        
        # Test loading non-existent file
        with self.assertRaises(Exception):
            load_code_from_file('nonexistent.py')
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        # Load test code
        code = load_code_from_file(self.test_files['bubble_sort'])
        
        # Create configuration with profiling
        config = OptimizationConfig(profile=True, verbose=True)
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Verify metrics
        self.assertIn('steps', result.metrics)
        self.assertIn('total_execution_time', result.metrics)
        self.assertGreater(result.metrics['total_execution_time'], 0)
    
    def test_error_handling(self):
        """Test error handling in optimization process."""
        # Load test code
        code = load_code_from_file(self.test_files['bubble_sort'])
        
        # Create configuration that will trigger errors
        config = OptimizationConfig(
            use_ml=True,
            use_fine_tuned=True,
            use_rule_based=True,
            verbose=True,
            timeout=0  # This will cause model loading to fail
        )
        
        # Run optimization
        result = optimize_code(code, config)
        
        # Verify error handling
        self.assertIsNotNone(result)
        self.assertIn('errors', result.metrics)
        self.assertGreater(len(result.metrics['errors']), 0)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEfficodeACRR)
    
    # Run tests
    print("\nRunning EFFICODE-ACRR Tests...")
    print("=" * 50)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Print summary
    print("\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed. Check the output above for details.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
