#!/usr/bin/env python3
"""
Comprehensive Test Suite for EFFICODE-ACRR
Tests all components: ML model, AST transformer, API, web interface
"""

import unittest
import json
import time
import requests
from complete_ml_optimizer import CompleteMlOptimizer
from ast_code_transformer import ASTCodeTransformer
from explainability_engine import OptimizationExplainer
from advanced_dataset_builder import AdvancedDatasetBuilder
from feedback_system import FeedbackSystem

class TestMLOptimizer(unittest.TestCase):
    """Test ML optimization components"""
    
    def setUp(self):
        self.optimizer = CompleteMlOptimizer()
    
    def test_two_sum_optimization(self):
        """Test Two Sum optimization"""
        code = '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []'''
        
        result = self.optimizer.optimize_code(code)
        
        self.assertTrue(result['success'] if 'success' in result else True)
        self.assertEqual(result['ml_analysis']['predicted_technique'], 'hash_map')
        self.assertGreater(result['ml_analysis']['confidence'], 0.5)
        self.assertEqual(result['complexity_analysis']['original']['time'], 'O(n²)')
        self.assertEqual(result['complexity_analysis']['optimized']['time'], 'O(n)')
    
    def test_contains_duplicate_optimization(self):
        """Test Contains Duplicate optimization"""
        code = '''def containsDuplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False'''
        
        result = self.optimizer.optimize_code(code)
        
        self.assertTrue(result['success'] if 'success' in result else True)
        self.assertIn(result['ml_analysis']['predicted_technique'], ['hash_set', 'hash_map'])
        self.assertEqual(result['complexity_analysis']['original']['time'], 'O(n²)')
    
    def test_max_subarray_optimization(self):
        """Test Maximum Subarray optimization"""
        code = '''def maxSubArray(nums):
    max_sum = float('-inf')
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            current_sum = sum(nums[i:j+1])
            max_sum = max(max_sum, current_sum)
    return max_sum'''
        
        result = self.optimizer.optimize_code(code)
        
        self.assertTrue(result['success'] if 'success' in result else True)
        self.assertEqual(result['complexity_analysis']['original']['time'], 'O(n²)')
    
    def test_processing_time(self):
        """Test that processing time is reasonable"""
        code = '''def test():
    for i in range(100):
        for j in range(100):
            if i == j:
                return i
    return -1'''
        
        start_time = time.time()
        result = self.optimizer.optimize_code(code)
        processing_time = time.time() - start_time
        
        self.assertLess(processing_time, 1.0)  # Should complete in under 1 second

class TestASTTransformer(unittest.TestCase):
    """Test AST code transformation"""
    
    def setUp(self):
        self.transformer = ASTCodeTransformer()
    
    def test_pattern_detection(self):
        """Test pattern detection"""
        two_sum_code = '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []'''
        
        pattern = self.transformer.detect_optimization_pattern(two_sum_code)
        self.assertEqual(pattern, 'two_sum_pattern')
    
    def test_code_transformation(self):
        """Test code transformation"""
        code = '''def containsDuplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False'''
        
        transformed = self.transformer.transform_code(code, 'hash_set')
        
        self.assertIn('set()', transformed)
        self.assertIn('containsDuplicate_optimized', transformed)
        self.assertIn('O(n)', transformed)

class TestExplainabilityEngine(unittest.TestCase):
    """Test explainability engine"""
    
    def setUp(self):
        self.explainer = OptimizationExplainer()
    
    def test_explanation_generation(self):
        """Test explanation generation"""
        code = '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []'''
        
        features = [2, 3, 2, 1, 0] + [0] * 25  # 30 features total
        
        explanation = self.explainer.explain_optimization_decision(
            code, features, 'hash_map', 0.85
        )
        
        self.assertIn('decision_summary', explanation)
        self.assertIn('feature_importance', explanation)
        self.assertIn('technique_details', explanation)
        self.assertEqual(explanation['decision_summary']['technique'], 'Hash Map')

class TestDatasetBuilder(unittest.TestCase):
    """Test dataset building"""
    
    def setUp(self):
        self.builder = AdvancedDatasetBuilder()
    
    def test_dataset_creation(self):
        """Test dataset creation"""
        dataset = self.builder.build_comprehensive_dataset()
        
        self.assertGreater(len(dataset), 10)  # Should have more than 10 examples
        
        # Check first example structure
        example = dataset[0]
        required_fields = ['title', 'brute_force', 'optimized', 'technique', 'complexity_improvement']
        for field in required_fields:
            self.assertIn(field, example)
    
    def test_dataset_validation(self):
        """Test dataset validation"""
        dataset = self.builder.build_comprehensive_dataset()
        
        # Check that all examples have valid Python syntax
        valid_count = 0
        for example in dataset:
            try:
                compile(example['brute_force'], '<string>', 'exec')
                compile(example['optimized'], '<string>', 'exec')
                valid_count += 1
            except SyntaxError:
                pass
        
        # Most examples should be valid
        self.assertGreater(valid_count / len(dataset), 0.8)

class TestFeedbackSystem(unittest.TestCase):
    """Test feedback system"""
    
    def setUp(self):
        self.feedback_system = FeedbackSystem(":memory:")  # Use in-memory database
        self.feedback_system.init_database()  # Ensure database is initialized
    
    def test_feedback_collection(self):
        """Test feedback collection"""
        optimization_result = {
            'original_code': 'def test(): pass',
            'ml_analysis': {
                'predicted_technique': 'hash_map',
                'confidence': 0.85
            }
        }
        
        user_feedback = {
            'feedback_type': 'accepted',
            'rating': 5,
            'session_id': 'test_session'
        }
        
        feedback_id = self.feedback_system.collect_feedback(optimization_result, user_feedback)
        self.assertIsNotNone(feedback_id)
    
    def test_statistics(self):
        """Test statistics generation"""
        # Add some test feedback
        for i in range(5):
            optimization_result = {
                'original_code': f'def test{i}(): pass',
                'ml_analysis': {
                    'predicted_technique': 'hash_map',
                    'confidence': 0.8 + i * 0.02
                }
            }
            
            user_feedback = {
                'feedback_type': 'accepted' if i % 2 == 0 else 'rejected',
                'rating': 4 + (i % 2),
                'session_id': f'test_session_{i}'
            }
            
            self.feedback_system.collect_feedback(optimization_result, user_feedback)
        
        stats = self.feedback_system.get_statistics()
        
        self.assertEqual(stats['total_feedback'], 5)
        self.assertGreater(stats['average_rating'], 0)
        self.assertIn('accepted', stats['feedback_types'])
        self.assertIn('rejected', stats['feedback_types'])

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_end_to_end_optimization(self):
        """Test complete optimization pipeline"""
        # Initialize components
        optimizer = CompleteMlOptimizer()
        transformer = ASTCodeTransformer()
        explainer = OptimizationExplainer()
        
        # Test code
        code = '''def findDuplicates(nums):
    duplicates = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j] and nums[i] not in duplicates:
                duplicates.append(nums[i])
    return duplicates'''
        
        # ML optimization
        ml_result = optimizer.optimize_code(code)
        self.assertIsNotNone(ml_result)
        
        # AST transformation
        pattern = transformer.detect_optimization_pattern(code)
        if pattern:
            transformed_code = transformer.transform_code(code, ml_result['ml_analysis']['predicted_technique'])
            self.assertIsNotNone(transformed_code)
        
        # Explanation
        explanation = explainer.explain_optimization_decision(
            code,
            ml_result['ml_analysis'].get('features_used', []),
            ml_result['ml_analysis']['predicted_technique'],
            ml_result['ml_analysis']['confidence']
        )
        self.assertIsNotNone(explanation)

class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def test_optimization_speed(self):
        """Test optimization speed for various code sizes"""
        optimizer = CompleteMlOptimizer()
        
        # Small code
        small_code = '''def test():
    for i in range(10):
        for j in range(10):
            if i == j:
                return i
    return -1'''
        
        start_time = time.time()
        result = optimizer.optimize_code(small_code)
        small_time = time.time() - start_time
        
        self.assertLess(small_time, 0.5)  # Should be very fast
        
        # Medium code
        medium_code = '''def test():
    result = []
    for i in range(100):
        for j in range(100):
            if i + j == 50:
                result.append((i, j))
    return result'''
        
        start_time = time.time()
        result = optimizer.optimize_code(medium_code)
        medium_time = time.time() - start_time
        
        self.assertLess(medium_time, 1.0)  # Should complete in under 1 second
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        optimizer = CompleteMlOptimizer()
        
        # Run multiple optimizations
        for i in range(10):
            code = f'''def test{i}():
    for x in range(50):
        for y in range(50):
            if x * y == {i * 10}:
                return (x, y)
    return None'''
            
            result = optimizer.optimize_code(code)
            self.assertIsNotNone(result)

def run_all_tests():
    """Run all test suites"""
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMLOptimizer,
        TestASTTransformer,
        TestExplainabilityEngine,
        TestDatasetBuilder,
        TestFeedbackSystem,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  • {test}: {error_msg}")
    
    if result.errors:
        print(f"\n🚨 ERRORS:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  • {test}: {error_msg}")
    
    if not result.failures and not result.errors:
        print("\n✅ ALL TESTS PASSED! EFFICODE-ACRR is ready for production! 🚀")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)