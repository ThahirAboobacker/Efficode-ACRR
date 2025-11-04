#!/usr/bin/env python3
"""
Fixed Web App for EFFICODE-ACRR with Working Code Generation
"""

from flask import Flask, render_template, request, jsonify
from quick_optimizer_fix import ImprovedOptimizer
import time

app = Flask(__name__)

# Initialize improved optimizer
optimizer = ImprovedOptimizer()

@app.route('/')
def index():
    """Main page"""
    return render_template('optimizer.html')

@app.route('/api/optimize', methods=['POST'])
def optimize_code():
    """API endpoint for code optimization with working code generation"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({'error': 'No code provided'}), 400
        
        start_time = time.time()
        
        # Use improved optimizer
        result = optimizer.optimize_code_with_fix(code)
        
        processing_time = time.time() - start_time
        
        response = {
            'success': True,
            'original_code': code,
            'optimized_code': result['optimized_code'],
            'analysis': {
                'technique': result['ml_analysis']['predicted_technique'],
                'confidence': f"{result['ml_analysis']['confidence']:.1%}",
                'original_complexity': result['complexity_analysis']['original']['time'],
                'optimized_complexity': result['complexity_analysis']['optimized']['time'],
                'data_structure': result['optimization_details']['data_structure'],
                'speedup': result['performance_improvement']['speedup_description']
            },
            'processing_time': f"{processing_time:.3f}s",
            'note': result.get('note', '')
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/examples')
def get_examples():
    """Get sample code examples"""
    examples = {
        'pairs_sum': {
            'title': 'Find Pairs with Sum',
            'code': '''def findPairsWithSum(nums, target):
    pairs = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                pairs.append((nums[i], nums[j]))
    return pairs''',
            'description': 'Find all pairs that sum to target value'
        },
        'two_sum': {
            'title': 'Two Sum Problem',
            'code': '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []''',
            'description': 'Find indices of two numbers that add up to target'
        },
        'contains_duplicate': {
            'title': 'Contains Duplicate',
            'code': '''def containsDuplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False''',
            'description': 'Check if array contains duplicates'
        },
        'max_subarray': {
            'title': 'Maximum Subarray',
            'code': '''def maxSubArray(nums):
    max_sum = float('-inf')
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            current_sum = sum(nums[i:j+1])
            max_sum = max(max_sum, current_sum)
    return max_sum''',
            'description': 'Find maximum sum of contiguous subarray'
        }
    }
    
    return jsonify(examples)

if __name__ == '__main__':
    print("🚀 Starting EFFICODE-ACRR with Fixed Code Generation")
    print("🌐 Access at: http://localhost:5000")
    print("✅ Now generates WORKING optimized code!")
    app.run(debug=True, host='0.0.0.0', port=5000)