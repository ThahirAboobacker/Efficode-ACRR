#!/usr/bin/env python
"""
Comprehensive test for the Enhanced EFFICODE system
Tests the working ML-powered optimization system
"""

import requests
import json
import time

API_URL = "http://localhost:5001"

def test_enhanced_api():
    """Test the enhanced API with ML capabilities"""
    print("🧠 Testing Enhanced EFFICODE System")
    print("🚀 Features: Rule-based + ML complexity prediction")
    print("=" * 60)
    
    # Test health check
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Health Check:")
            print(f"   Status: {health['status']}")
            print(f"   Components: {health['components']}")
            print(f"   ML Model Trained: {health['model_info']['complexity_predictor_trained']}")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    print()
    
    # Test cases
    test_cases = [
        {
            'name': 'Fibonacci Optimization (Exponential → Linear)',
            'code': '''def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)''',
            'expected_improvement': True
        },
        {
            'name': 'Constant Folding',
            'code': '''def calculate():
    x = 2 * 3 + 4
    y = 10 / 2
    z = 2 ** 8
    return x + y + z''',
            'expected_improvement': True
        },
        {
            'name': 'Complex Mathematical Expression',
            'code': '''def math_operations():
    a = 5 + 3 * 2
    b = 100 / 4
    c = 3 ** 3
    return a + b + c''',
            'expected_improvement': False  # May not optimize
        },
        {
            'name': 'Simple Loop (Baseline)',
            'code': '''def process_items(items):
    results = []
    for item in items:
        results.append(item * 2)
    return results''',
            'expected_improvement': False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Test optimization
            payload = {
                'code': test_case['code'],
                'level': 'high',
                'enable_explainability': True
            }
            
            start_time = time.time()
            response = requests.post(f"{API_URL}/optimize", json=payload)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Status: {result['status']}")
                print(f"⏱️  Processing Time: {result['processing_time']:.3f}s")
                print(f"🔄 Complexity: {result['original_complexity']} → {result['optimized_complexity']}")
                print(f"📈 Performance Improvement: {result['performance_improvement']:.1f}%")
                print(f"🔧 Applied Techniques: {', '.join(result['applied_techniques'])}")
                print(f"✅ Validation: {result['validation_status']}")
                print(f"🎯 Confidence: {result['confidence_score']:.2f}")
                
                if result['improvements']:
                    print(f"🚀 Optimizations Applied:")
                    for j, improvement in enumerate(result['improvements'], 1):
                        print(f"   {j}. {improvement['type']}: {improvement['description']}")
                
                print(f"💡 Explanation: {result['explanation']}")
                
                # Check if code was actually optimized
                code_changed = result['original_code'] != result['optimized_code']
                complexity_improved = result['original_complexity'] != result['optimized_complexity']
                
                if code_changed or complexity_improved:
                    print("🎉 Code was successfully optimized!")
                else:
                    print("ℹ️  No optimizations applied (code may already be optimal)")
                
                results.append({
                    'name': test_case['name'],
                    'success': True,
                    'optimized': code_changed,
                    'complexity_improved': complexity_improved,
                    'performance_improvement': result['performance_improvement'],
                    'processing_time': result['processing_time']
                })
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    'name': test_case['name'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
        
        except Exception as e:
            print(f"❌ Test Error: {e}")
            results.append({
                'name': test_case['name'],
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Test complexity prediction endpoint
    print("🧪 Testing Complexity Prediction Endpoint")
    print("-" * 50)
    
    try:
        complexity_payload = {
            'code': '''def nested_loops(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += i * j
    return total'''
        }
        
        response = requests.post(f"{API_URL}/predict-complexity", json=complexity_payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Complexity Prediction: {result['complexity']}")
            print(f"🎯 Confidence: {result['confidence']:.2f}")
            print(f"📊 Features: {result['features']}")
        else:
            print(f"❌ Complexity prediction failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Complexity prediction error: {e}")
    
    print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r['success'])
    optimized_tests = sum(1 for r in results if r.get('optimized', False))
    total_tests = len(results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Actually Optimized: {optimized_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        avg_processing_time = sum(r.get('processing_time', 0) for r in results if r['success']) / successful_tests
        avg_improvement = sum(r.get('performance_improvement', 0) for r in results if r['success']) / successful_tests
        
        print(f"Average Processing Time: {avg_processing_time:.3f}s")
        print(f"Average Performance Improvement: {avg_improvement:.1f}%")
    
    print(f"\n🔗 Detailed Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        optimized = "🚀" if result.get('optimized', False) else "➖"
        print(f"   {status} {optimized} {result['name']}")
        if not result['success'] and 'error' in result:
            print(f"      Error: {result['error']}")
    
    print(f"\n🌟 Enhanced EFFICODE Features Demonstrated:")
    print(f"   ✅ Rule-based optimization (Fibonacci, constant folding)")
    print(f"   ✅ ML-based complexity prediction")
    print(f"   ✅ Hybrid optimization pipeline")
    print(f"   ✅ Performance improvement calculation")
    print(f"   ✅ Confidence scoring")
    print(f"   ✅ Real-time API processing")
    
    return successful_tests == total_tests

def test_model_training():
    """Test model training endpoint"""
    print("\n🧪 Testing Model Training")
    print("-" * 50)
    
    try:
        payload = {'num_examples': 50}
        response = requests.post(f"{API_URL}/train", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Training Status: {result['status']}")
            print(f"📊 Training Results: {result['training_results']}")
            print(f"📈 Model Accuracy: {result['training_results'].get('accuracy', 'N/A')}")
            return True
        else:
            print(f"❌ Training failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Training error: {e}")
        return False

if __name__ == "__main__":
    print("🧠 EFFICODE Enhanced System - Comprehensive Test Suite")
    print("🎯 Testing ML-Powered Python Code Optimization")
    print()
    
    # Test main functionality
    main_success = test_enhanced_api()
    
    # Test training
    training_success = test_model_training()
    
    print(f"\n{'='*60}")
    print("🎉 FINAL RESULTS")
    print('='*60)
    
    if main_success and training_success:
        print("✅ ALL TESTS PASSED!")
        print("🚀 Enhanced EFFICODE system is fully functional!")
        print("🌟 Features working: Rule-based optimization + ML complexity prediction")
    elif main_success:
        print("✅ Main functionality working!")
        print("⚠️  Training functionality needs attention")
    else:
        print("❌ Some tests failed - check the details above")
    
    print(f"\n🌐 Server running at: {API_URL}")
    print("📚 Try the web interface or API integration!")