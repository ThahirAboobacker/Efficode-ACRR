import os
import sys
import unittest
import pandas as pd
import logging
import time
from typing import List, Dict, Optional
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path to import flan_t5
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)  # Also add current dir to handle direct imports

try:
    # Try direct import first (if in the same directory)
    from flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
    logger.info("Successfully imported FlanT5ExplanationGenerator from current directory")
except ImportError:
    try:
        # Try importing from models package if direct import fails
        from models.flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
        logger.info("Successfully imported FlanT5ExplanationGenerator from models package")
    except ImportError as e:
        logger.error(f"Error importing FlanT5ExplanationGenerator: {e}")
        logger.error("Make sure flan_t5_explanation.py is in the correct location")
        sys.exit(1)

# Test cases with different algorithm optimizations
TEST_CASES = [
    {
        "name": "Bubble Sort Optimization",
        "original_code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
        """,
        "optimized_code": """
def optimized_bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
        """,
        "complexity_before": "O(n²)",
        "complexity_after": "O(n²) worst case, O(n) best case",
        "applied_rules": ["Early termination with swapped flag", "Loop optimization"]
    },
    {
        "name": "Linear Search to Binary Search",
        "original_code": """
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
        """,
        "optimized_code": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
        """,
        "complexity_before": "O(n)",
        "complexity_after": "O(log n)",
        "applied_rules": ["Algorithm replacement (linear → binary search)", "Divide and conquer strategy"]
    },
    {
        "name": "Fibonacci with Memoization",
        "original_code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
        """,
        "optimized_code": """
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]
        """,
        "complexity_before": "O(2^n)",
        "complexity_after": "O(n)",
        "applied_rules": ["Dynamic programming with memoization", "Overlapping subproblems optimization"]
    },
    {
        "name": "Dictionary Optimization",
        "original_code": """
def count_frequencies(words):
    frequencies = {}
    for word in words:
        count = 0
        for w in words:
            if w == word:
                count += 1
        frequencies[word] = count
    return frequencies
        """,
        "optimized_code": """
def count_frequencies_optimized(words):
    frequencies = {}
    for word in words:
        if word in frequencies:
            frequencies[word] += 1
        else:
            frequencies[word] = 1
    return frequencies
        """,
        "complexity_before": "O(n²)",
        "complexity_after": "O(n)",
        "applied_rules": ["Hashtable/Dictionary for O(1) lookups", "Single-pass algorithm"]
    }
]

class TestFlanT5(unittest.TestCase):
    """Test suite for the FlanT5ExplanationGenerator"""
    
    @classmethod
    def setUpClass(cls):
        """Set up for all tests - create the explanation generator"""
        logger.info("Setting up FlanT5 test environment")
        
        # Set environment variables for control
        offline_mode = os.environ.get("FLANT5_OFFLINE_MODE", "").lower() in ("true", "1", "yes")
        try_reuse_model = os.environ.get("FLANT5_REUSE_MODEL", "").lower() in ("true", "1", "yes")
        timeout = int(os.environ.get("FLANT5_TEST_TIMEOUT", "180"))  # Default 3 minutes
        
        # Check for custom model path
        custom_model_path = os.environ.get("FLANT5_MODEL_PATH", None)
        
        # Set default cache directory for model
        if try_reuse_model:
            # Try to use the default HuggingFace cache or a custom path
            cache_dir = os.environ.get("FLANT5_CACHE_DIR", None)
            logger.info(f"Attempting to reuse existing model with cache_dir: {cache_dir}")
        else:
            # Create a temporary directory for isolated testing
            cls.temp_dir = tempfile.mkdtemp()
            cache_dir = os.path.join(cls.temp_dir, "flan_t5_cache")
            logger.info(f"Created temporary cache directory at {cache_dir}")
            
        # Create offline explainer for rule-based testing
        cls.offline_explainer = FlanT5ExplanationGenerator(
            offline_mode=True,
            cache_dir=cache_dir
        )
        
        # Only attempt to load model if not in forced offline mode
        if offline_mode:
            logger.info("Forced offline mode - skipping model loading")
            cls.online_explainer = None
            cls.model_loaded = False
        else:
            # Try to load model (either from custom path or default)
            logger.info(f"Attempting to load model (timeout: {timeout}s)")
            cls.online_explainer = FlanT5ExplanationGenerator(
                model_name="google/flan-t5-base",  # Using base model as default
                cache_dir=cache_dir
            )
            
            try:
                # Load model from custom path if specified
                if custom_model_path and os.path.exists(custom_model_path):
                    logger.info(f"Loading model from custom path: {custom_model_path}")
                    cls.model_loaded = cls.online_explainer.load_model(
                        model_path=custom_model_path, 
                        timeout=timeout
                    )
                else:
                    # Try to load from HuggingFace or cache
                    cls.model_loaded = cls.online_explainer.load_model(timeout=timeout)
                    
                logger.info(f"Model loading result: {'Success' if cls.model_loaded else 'Failed'}")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                cls.model_loaded = False
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        logger.info("Cleaning up FlanT5 test environment")
        
        # Check if we need to remove a temp directory
        if not os.environ.get("FLANT5_REUSE_MODEL", "").lower() in ("true", "1", "yes"):
            if hasattr(cls, 'temp_dir'):
                try:
                    shutil.rmtree(cls.temp_dir)
                    logger.info(f"Removed temporary directory {cls.temp_dir}")
                except Exception as e:
                    logger.error(f"Error removing temporary directory: {e}")
    
    def test_rule_based_generation(self):
        """Test rule-based explanation generation"""
        logger.info("Testing rule-based explanation generation")
        
        for test_case in TEST_CASES:
            with self.subTest(test_case=test_case["name"]):
                start_time = time.time()
                explanation = self.offline_explainer.generate_explanation(
                    test_case["original_code"],
                    test_case["optimized_code"],
                    test_case["complexity_before"],
                    test_case["complexity_after"],
                    test_case.get("applied_rules", []),
                    force_rule_based=True
                )
                generation_time = time.time() - start_time
                
                # Format the explanation
                formatted_explanation = self.offline_explainer.format_explanation(explanation)
                
                # Basic validation of the explanation
                self.assertIsNotNone(explanation, "Explanation should not be None")
                self.assertTrue(len(explanation) > 100, "Explanation should have reasonable length")
                self.assertIn("Optimization", explanation, "Explanation should mention optimization")
                self.assertIn(test_case["complexity_before"], explanation, "Explanation should include original complexity")
                self.assertIn(test_case["complexity_after"].split()[0], explanation, "Explanation should include optimized complexity")
                
                # Print the explanation for manual inspection
                print(f"\nRule-based explanation for {test_case['name']} (generated in {generation_time:.2f}s):")
                print("-" * 80)
                print(formatted_explanation)
                print("-" * 80)
    
    def test_model_based_generation(self):
        """Test model-based explanation generation"""
        if not hasattr(self, 'model_loaded') or not self.model_loaded:
            self.skipTest("Model not loaded, skipping model-based generation test")
            
        logger.info("Testing model-based explanation generation")
        
        for test_case in TEST_CASES:
            with self.subTest(test_case=test_case["name"]):
                try:
                    start_time = time.time()
                    explanation = self.online_explainer.generate_explanation(
                        test_case["original_code"],
                        test_case["optimized_code"],
                        test_case["complexity_before"],
                        test_case["complexity_after"],
                        test_case.get("applied_rules", [])
                    )
                    generation_time = time.time() - start_time
                    
                    # Format the explanation
                    formatted_explanation = self.online_explainer.format_explanation(explanation)
                    
                    # Basic validation of the explanation
                    self.assertIsNotNone(explanation, "Explanation should not be None")
                    self.assertTrue(len(explanation) > 100, "Explanation should have reasonable length")
                    
                    # Print the explanation for manual inspection
                    print(f"\nModel-based explanation for {test_case['name']} (generated in {generation_time:.2f}s):")
                    print("-" * 80)
                    print(formatted_explanation)
                    print("-" * 80)
                    
                    # Add a delay between tests to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    self.fail(f"Exception during model-based generation: {e}")
    
    def test_batch_generation(self):
        """Test batch explanation generation"""
        logger.info("Testing batch explanation generation")
        
        # Create batch input from test cases
        code_pairs = []
        for test_case in TEST_CASES:
            code_pairs.append({
                'original_code': test_case["original_code"],
                'optimized_code': test_case["optimized_code"],
                'complexity_before': test_case["complexity_before"],
                'complexity_after': test_case["complexity_after"],
                'applied_rules': test_case.get("applied_rules", [])
            })
        
        # Test rule-based batch generation
        start_time = time.time()
        rule_based_explanations = self.offline_explainer.batch_generate_explanations(
            code_pairs, 
            force_rule_based=True
        )
        batch_time = time.time() - start_time
        
        self.assertEqual(len(rule_based_explanations), len(TEST_CASES), 
                         "Should generate explanations for all test cases")
        print(f"\nBatch rule-based generation completed in {batch_time:.2f}s for {len(TEST_CASES)} examples")
        
        # Test model-based batch generation if model is loaded
        if hasattr(self, 'model_loaded') and self.model_loaded:
            try:
                start_time = time.time()
                model_based_explanations = self.online_explainer.batch_generate_explanations(
                    code_pairs[:2],  # Use only first 2 test cases to save time
                    batch_size=2
                )
                batch_time = time.time() - start_time
                
                self.assertEqual(len(model_based_explanations), 2, 
                                "Should generate explanations for the 2 test cases")
                print(f"\nBatch model-based generation completed in {batch_time:.2f}s for 2 examples")
            except Exception as e:
                self.fail(f"Exception during model-based batch generation: {e}")
    
    def test_factory_function(self):
        """Test the factory function for creating generator instances"""
        logger.info("Testing factory function")
        
        # Test with offline mode
        offline_gen = get_explanation_generator(offline_mode=True)
        self.assertTrue(offline_gen.offline_mode, "Factory function should create offline generator")
        
        # Test explanation generation with the factory-created generator
        explanation = offline_gen.generate_explanation(
            TEST_CASES[0]["original_code"],
            TEST_CASES[0]["optimized_code"],
            TEST_CASES[0]["complexity_before"],
            TEST_CASES[0]["complexity_after"]
        )
        
        self.assertIsNotNone(explanation, "Factory-created generator should produce explanations")
        
    def test_model_reuse(self):
        """Test that the system can reuse an existing model if available"""
        # Skip if we're in forced offline mode
        if os.environ.get("FLANT5_OFFLINE_MODE", "").lower() in ("true", "1", "yes"):
            self.skipTest("Skipping model reuse test in offline mode")
            
        # Skip if no model was loaded
        if not hasattr(self, 'model_loaded') or not self.model_loaded:
            self.skipTest("Model not loaded, skipping model reuse test")
        
        # Check if we can determine the model path
        model_path = None
        if hasattr(self.online_explainer, 'cache_dir'):
            model_path = self.online_explainer.cache_dir
            
        # Test that we can create a new generator that reuses the model
        try:
            logger.info(f"Testing model reuse from path: {model_path}")
            start_time = time.time()
            
            new_explainer = get_explanation_generator(
                model_path=model_path,
                timeout=60
            )
            
            load_time = time.time() - start_time
            logger.info(f"Model reloading took {load_time:.2f}s")
            
            # Verify it works
            explanation = new_explainer.generate_explanation(
                TEST_CASES[0]["original_code"],
                TEST_CASES[0]["optimized_code"],
                TEST_CASES[0]["complexity_before"],
                TEST_CASES[0]["complexity_after"],
                force_rule_based=False
            )
            
            self.assertIsNotNone(explanation, "Reused model should generate explanations")
            self.assertTrue(len(explanation) > 100, "Explanation should have reasonable length")
            
            print("\nSuccessfully reused model to generate explanation")
            
        except Exception as e:
            self.fail(f"Exception during model reuse test: {e}")


if __name__ == "__main__":
    # Control test behavior through environment variables
    
    # Set to "true" to force rule-based mode only (don't try to load model)
    # os.environ["FLANT5_OFFLINE_MODE"] = "false"
    
    # Set to "true" to try to reuse an existing model instead of downloading new
    os.environ["FLANT5_REUSE_MODEL"] = "true"
    
    # Specify custom paths (uncomment and set if needed)
    # os.environ["FLANT5_CACHE_DIR"] = "/path/to/your/cache"
    # os.environ["FLANT5_MODEL_PATH"] = "/path/to/specific/model"
    
    # Set timeout for model loading (adjust as needed)
    os.environ["FLANT5_TEST_TIMEOUT"] = "300"  # 5 minutes
    
    # Run all tests
    unittest.main()