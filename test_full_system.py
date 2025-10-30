#!/usr/bin/env python
"""
Comprehensive test for the full EFFICODE-ACRR ML system
Tests all components: dataset generation, model training, optimization, and validation
"""

import sys
import os
import logging
import time
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('efficode.test')

def test_dataset_generation():
    """Test dataset generation and management"""
    logger.info("Testing dataset generation...")
    
    try:
        from dataset_manager import DatasetManager
        
        manager = DatasetManager()
        
        # Generate synthetic data
        examples = manager.generate_synthetic_data(100)
        logger.info(f"Generated {len(examples)} training examples")
        
        # Test dataset splitting
        train, val, test = manager.split_dataset(examples, 0.7, 0.2, 0.1)
        logger.info(f"Split dataset: {len(train)} train, {len(val)} val, {len(test)} test")
        
        # Test saving and loading
        test_file = backend_dir / 'datasets' / 'test_dataset.json'
        manager.save_dataset(examples[:10], str(test_file))
        loaded_examples = manager.load_dataset(str(test_file))
        logger.info(f"Saved and loaded {len(loaded_examples)} examples")
        
        # Get statistics
        stats = manager.get_dataset_statistics(examples)
        logger.info(f"Dataset statistics: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Dataset generation test failed: {e}")
        return False

def test_complexity_predictor():
    """Test complexity prediction model"""
    logger.info("Testing complexity predictor...")
    
    try:
        from ml.models.complexity_predictor import ComplexityPredictor
        from dataset_manager import DatasetManager
        
        # Generate training data
        manager = DatasetManager()
        examples = manager.generate_synthetic_data(50)  # Small dataset for testing
        
        # Initialize and train predictor
        predictor = ComplexityPredictor(model_type='random_forest')
        results = predictor.train_model(examples)
        logger.info(f"Training results: {results}")
        
        # Test prediction
        test_code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""
        
        prediction = predictor.predict_complexity(test_code)
        logger.info(f"Complexity prediction: {prediction.symbolic_complexity} (confidence: {prediction.confidence:.2f})")
        
        # Test model saving/loading
        model_path = backend_dir / 'models' / 'test_complexity_model.pkl'
        predictor.save_model(str(model_path))
        
        new_predictor = ComplexityPredictor(model_type='random_forest')
        new_predictor.load_model(str(model_path))
        
        new_prediction = new_predictor.predict_complexity(test_code)
        logger.info(f"Loaded model prediction: {new_prediction.symbolic_complexity}")
        
        return True
        
    except Exception as e:
        logger.error(f"Complexity predictor test failed: {e}")
        return False

def test_validation_sandbox():
    """Test validation sandbox and performance profiling"""
    logger.info("Testing validation sandbox...")
    
    try:
        from validation_sandbox import ValidationSandbox
        
        sandbox = ValidationSandbox()
        
        # Test basic code execution
        test_code = """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
"""
        
        result = sandbox.execute_code_safely(test_code)
        logger.info(f"Execution result: success={result.success}, time={result.execution_time:.4f}s")
        
        # Test performance measurement
        fibonacci_code = """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b

result = fibonacci(20)
"""
        
        perf_metrics = sandbox.measure_performance(fibonacci_code, num_runs=3)
        logger.info(f"Performance metrics: avg_time={perf_metrics.avg_execution_time:.4f}s")
        
        # Test security validation
        malicious_code = "import os; os.system('echo hello')"
        security_issues = sandbox.detect_security_issues(malicious_code)
        logger.info(f"Security issues detected: {len(security_issues)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Validation sandbox test failed: {e}")
        return False

def test_rule_based_optimizer():
    """Test rule-based optimizer"""
    logger.info("Testing rule-based optimizer...")
    
    try:
        from rule_based import RuleBasedOptimizer
        
        optimizer = RuleBasedOptimizer()
        
        # Test Fibonacci optimization
        fibonacci_code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""
        
        optimized, orig_complexity, opt_complexity, explanation = optimizer.optimize(fibonacci_code)
        logger.info(f"Rule-based optimization: {orig_complexity} -> {opt_complexity}")
        logger.info(f"Code changed: {optimized != fibonacci_code}")
        
        # Test constant folding
        constant_code = """
def calculate():
    x = 2 * 3 + 4
    y = 10 / 2
    return x + y
"""
        
        opt_const, _, _, _ = optimizer.optimize(constant_code)
        logger.info(f"Constant folding applied: {opt_const != constant_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"Rule-based optimizer test failed: {e}")
        return False

def test_model_trainer():
    """Test model training pipeline"""
    logger.info("Testing model trainer...")
    
    try:
        from ml.training.model_trainer import ModelTrainer
        
        trainer = ModelTrainer()
        
        # Test complexity predictor training
        from dataset_manager import DatasetManager
        manager = DatasetManager()
        examples = manager.generate_synthetic_data(30)  # Very small for testing
        
        train_data, val_data, test_data = manager.split_dataset(examples, 0.6, 0.2, 0.2)
        
        results = trainer.train_complexity_predictor(train_data, val_data, test_data)
        logger.info(f"Model training results: {list(results.keys())}")
        
        # Test model loading
        loaded_models = trainer.load_trained_models()
        logger.info(f"Loaded models: {list(loaded_models.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Model trainer test failed: {e}")
        return False

def test_enhanced_api():
    """Test the enhanced API functionality"""
    logger.info("Testing enhanced API...")
    
    try:
        # Import and initialize components
        from enhanced_api import initialize_components, hybrid_optimizer
        from data_models import OptimizationRequest, OptimizationLevel
        
        # Test optimization request
        request = OptimizationRequest(
            code="""
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
""",
            optimization_level=OptimizationLevel.HIGH,
            use_ml=False,  # Disable ML for this test
            use_rule_based=True,
            enable_explainability=False
        )
        
        # Perform optimization
        result = hybrid_optimizer.optimize(request)
        
        logger.info(f"Hybrid optimization completed:")
        logger.info(f"  - Applied techniques: {result.applied_techniques}")
        logger.info(f"  - Complexity: {result.complexity_before} -> {result.complexity_after}")
        logger.info(f"  - Validation status: {result.validation_status}")
        logger.info(f"  - Processing time: {result.processing_time:.3f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"Enhanced API test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    logger.info("Starting comprehensive EFFICODE-ACRR system test...")
    
    tests = [
        ("Dataset Generation", test_dataset_generation),
        ("Complexity Predictor", test_complexity_predictor),
        ("Validation Sandbox", test_validation_sandbox),
        ("Rule-based Optimizer", test_rule_based_optimizer),
        ("Model Trainer", test_model_trainer),
        ("Enhanced API", test_enhanced_api)
    ]
    
    results = {}
    total_start_time = time.time()
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running test: {test_name}")
        logger.info('='*60)
        
        start_time = time.time()
        try:
            success = test_func()
            end_time = time.time()
            
            results[test_name] = {
                'success': success,
                'duration': end_time - start_time,
                'error': None
            }
            
            status = "✅ PASSED" if success else "❌ FAILED"
            logger.info(f"{status} - {test_name} ({end_time - start_time:.2f}s)")
            
        except Exception as e:
            end_time = time.time()
            results[test_name] = {
                'success': False,
                'duration': end_time - start_time,
                'error': str(e)
            }
            logger.error(f"❌ FAILED - {test_name}: {e}")
    
    # Summary
    total_time = time.time() - total_start_time
    passed_tests = sum(1 for r in results.values() if r['success'])
    total_tests = len(results)
    
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info('='*60)
    logger.info(f"Total tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    logger.info(f"Total time: {total_time:.2f}s")
    
    logger.info(f"\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅" if result['success'] else "❌"
        error_info = f" - {result['error']}" if result['error'] else ""
        logger.info(f"  {status} {test_name}: {result['duration']:.2f}s{error_info}")
    
    if passed_tests == total_tests:
        logger.info(f"\n🎉 ALL TESTS PASSED! EFFICODE-ACRR system is fully functional!")
    else:
        logger.info(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the logs above for details.")
    
    return results

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    # Run comprehensive test
    test_results = run_comprehensive_test()
    
    # Exit with appropriate code
    all_passed = all(r['success'] for r in test_results.values())
    sys.exit(0 if all_passed else 1)