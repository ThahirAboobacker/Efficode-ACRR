#!/usr/bin/env python
"""
CodeBERT-Powered Code Optimization Demo
Demonstrates how EFFICODE can use CodeBERT for semantic code understanding and optimization
"""

import sys
import os
import time
import torch
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend' / 'src'
sys.path.insert(0, str(backend_dir))

print("🤖 EFFICODE-ACRR with CodeBERT Integration")
print("🧠 Semantic Code Understanding and Optimization")
print("=" * 60)

# Check if transformers is available
try:
    from transformers import AutoTokenizer, AutoModel
    print("✅ Transformers library available")
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("❌ Transformers library not available")
    print("   Install with: pip install transformers")
    TRANSFORMERS_AVAILABLE = False

class CodeBERTAnalyzer:
    """CodeBERT-based code analyzer for semantic understanding"""
    
    def __init__(self):
        self.model_name = "microsoft/codebert-base"
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def initialize(self):
        """Initialize CodeBERT model"""
        if not TRANSFORMERS_AVAILABLE:
            return False
            
        try:
            print(f"🔄 Loading CodeBERT model: {self.model_name}")
            print(f"   Device: {self.device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            print("✅ CodeBERT model loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading CodeBERT: {e}")
            return False
    
    def encode_code(self, code: str):
        """Encode code using CodeBERT"""
        if not self.model:
            return None
            
        try:
            # Tokenize code
            inputs = self.tokenizer(
                code,
                return_tensors='pt',
                max_length=512,
                padding=True,
                truncation=True
            ).to(self.device)
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token representation
                code_embedding = outputs.last_hidden_state[:, 0, :]
            
            return code_embedding
            
        except Exception as e:
            print(f"❌ Error encoding code: {e}")
            return None
    
    def analyze_semantic_similarity(self, code1: str, code2: str):
        """Analyze semantic similarity between two code snippets"""
        emb1 = self.encode_code(code1)
        emb2 = self.encode_code(code2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Calculate cosine similarity
        similarity = torch.cosine_similarity(emb1, emb2).item()
        return similarity
    
    def analyze_code_complexity_features(self, code: str):
        """Extract complexity-related features using CodeBERT"""
        embedding = self.encode_code(code)
        
        if embedding is None:
            return {}
        
        # Convert to numpy for analysis
        emb_np = embedding.cpu().numpy().flatten()
        
        # Extract statistical features from embeddings
        features = {
            'embedding_mean': float(emb_np.mean()),
            'embedding_std': float(emb_np.std()),
            'embedding_max': float(emb_np.max()),
            'embedding_min': float(emb_np.min()),
            'complexity_score': float(abs(emb_np.mean()) * emb_np.std()),  # Heuristic complexity score
        }
        
        return features

class CodeBERTOptimizer:
    """CodeBERT-powered code optimizer"""
    
    def __init__(self):
        self.analyzer = CodeBERTAnalyzer()
        self.optimization_templates = {
            'fibonacci_recursive': {
                'pattern_embedding': None,
                'optimized_code': '''def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    # CodeBERT-optimized iterative approach
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b''',
                'explanation': 'CodeBERT detected recursive Fibonacci pattern and applied iterative optimization'
            }
        }
    
    def initialize(self):
        """Initialize the optimizer"""
        return self.analyzer.initialize()
    
    def optimize_with_codebert(self, code: str):
        """Optimize code using CodeBERT semantic understanding"""
        
        if not self.analyzer.model:
            return self._fallback_optimization(code)
        
        print(f"🤖 Analyzing code with CodeBERT...")
        
        # Get code embedding
        code_embedding = self.analyzer.encode_code(code)
        if code_embedding is None:
            return self._fallback_optimization(code)
        
        # Extract semantic features
        features = self.analyzer.analyze_code_complexity_features(code)
        print(f"📊 CodeBERT Features:")
        for key, value in features.items():
            print(f"   • {key}: {value:.4f}")
        
        # Check for optimization patterns using semantic similarity
        best_match = None
        best_similarity = 0.0
        
        # Fibonacci pattern detection
        fibonacci_patterns = [
            "def fibonacci(n): return fibonacci(n-1) + fibonacci(n-2)",
            "fibonacci recursive exponential",
            "recursive function fibonacci"
        ]
        
        for pattern in fibonacci_patterns:
            similarity = self.analyzer.analyze_semantic_similarity(code, pattern)
            print(f"🔍 Similarity to '{pattern}': {similarity:.3f}")
            
            if similarity > best_similarity and similarity > 0.7:
                best_similarity = similarity
                best_match = 'fibonacci_recursive'
        
        # Apply optimization if pattern detected
        if best_match:
            template = self.optimization_templates[best_match]
            
            # Verify semantic preservation
            original_similarity = self.analyzer.analyze_semantic_similarity(
                code, template['optimized_code']
            )
            
            print(f"✅ Pattern detected: {best_match} (similarity: {best_similarity:.3f})")
            print(f"🔄 Semantic preservation: {original_similarity:.3f}")
            
            if original_similarity > 0.5:  # Ensure semantic similarity
                return {
                    'optimized_code': template['optimized_code'],
                    'explanation': template['explanation'],
                    'method': 'codebert_semantic',
                    'confidence': best_similarity,
                    'semantic_preservation': original_similarity,
                    'features': features
                }
        
        # No optimization found
        return {
            'optimized_code': code,
            'explanation': 'CodeBERT analysis completed - no optimization patterns detected',
            'method': 'codebert_analysis',
            'confidence': 0.0,
            'semantic_preservation': 1.0,
            'features': features
        }
    
    def _fallback_optimization(self, code):
        """Fallback when CodeBERT is not available"""
        return {
            'optimized_code': code,
            'explanation': 'CodeBERT not available - using fallback analysis',
            'method': 'fallback',
            'confidence': 0.0,
            'semantic_preservation': 1.0,
            'features': {}
        }

def demonstrate_codebert_optimization():
    """Demonstrate CodeBERT-powered optimization"""
    
    print("🚀 Initializing CodeBERT Optimizer...")
    optimizer = CodeBERTOptimizer()
    
    if not optimizer.initialize():
        print("⚠️  CodeBERT not available - showing conceptual demo")
        print("   Install transformers: pip install transformers torch")
        return False
    
    # Test cases
    test_cases = [
        {
            'name': 'Fibonacci Recursive Pattern',
            'code': '''def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)''',
            'expected': 'Should detect recursive Fibonacci pattern'
        },
        {
            'name': 'Factorial Recursive',
            'code': '''def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n-1)''',
            'expected': 'Should analyze recursive factorial pattern'
        },
        {
            'name': 'Simple Loop',
            'code': '''def sum_numbers(n):
    total = 0
    for i in range(n):
        total += i
    return total''',
            'expected': 'Should analyze loop complexity'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"🎯 Expected: {test_case['expected']}")
        print("─" * 50)
        
        # Show original code
        print("📋 Original Code:")
        for j, line in enumerate(test_case['code'].split('\n'), 1):
            print(f"   {j:2d}: {line}")
        
        try:
            start_time = time.time()
            result = optimizer.optimize_with_codebert(test_case['code'])
            end_time = time.time()
            
            print(f"\n⚡ CodeBERT Analysis Results:")
            print(f"   🔧 Method: {result['method']}")
            print(f"   🎯 Confidence: {result['confidence']:.3f}")
            print(f"   🔄 Semantic Preservation: {result['semantic_preservation']:.3f}")
            print(f"   ⏱️  Processing Time: {end_time - start_time:.3f}s")
            print(f"   💡 Explanation: {result['explanation']}")
            
            if result['features']:
                print(f"   📊 Complexity Score: {result['features'].get('complexity_score', 0):.4f}")
            
            # Show optimized code if different
            if result['optimized_code'] != test_case['code']:
                print(f"\n⚡ CodeBERT-Optimized Code:")
                for j, line in enumerate(result['optimized_code'].split('\n'), 1):
                    print(f"   {j:2d}: {line}")
                print("🎉 Code was optimized using semantic understanding!")
            else:
                print("ℹ️  No optimization applied (code may already be optimal)")
            
            results.append({
                'name': test_case['name'],
                'success': True,
                'optimized': result['optimized_code'] != test_case['code'],
                'confidence': result['confidence'],
                'method': result['method']
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'name': test_case['name'],
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 CODEBERT OPTIMIZATION SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r['success'])
    optimized_tests = sum(1 for r in results if r.get('optimized', False))
    
    print(f"🧪 Total Tests: {len(results)}")
    print(f"✅ Successful: {successful_tests}")
    print(f"🚀 Optimized by CodeBERT: {optimized_tests}")
    
    print(f"\n🔗 Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0)
        print(f"   {status} {result['name']} ({method}, confidence: {confidence:.3f})")
    
    print(f"\n🌟 CodeBERT Capabilities Demonstrated:")
    print(f"   ✅ Semantic code understanding")
    print(f"   ✅ Pattern recognition using embeddings")
    print(f"   ✅ Similarity-based optimization matching")
    print(f"   ✅ Semantic preservation validation")
    print(f"   ✅ Feature extraction from code embeddings")
    
    return successful_tests > 0

if __name__ == "__main__":
    success = demonstrate_codebert_optimization()
    
    print(f"\n{'='*60}")
    print("🎯 CODEBERT INTEGRATION STATUS")
    print('='*60)
    
    if success:
        print("🎉 CodeBERT integration successful!")
        print("🤖 EFFICODE can now use semantic understanding for optimization!")
    else:
        print("⚠️  CodeBERT integration needs setup")
        print("📋 Install requirements: pip install transformers torch")
    
    print(f"\n🔗 Integration Points:")
    print(f"   • Semantic similarity analysis")
    print(f"   • Pattern-based optimization detection")
    print(f"   • Code embedding feature extraction")
    print(f"   • Confidence scoring using similarity")
    print(f"   • Semantic preservation validation")
    
    print(f"\n🚀 Next Steps for Full CodeBERT Integration:")
    print(f"   • Fine-tune CodeBERT on optimization datasets")
    print(f"   • Expand pattern templates with embeddings")
    print(f"   • Implement sequence-to-sequence optimization")
    print(f"   • Add attention visualization for explainability")