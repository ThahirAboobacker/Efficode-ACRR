#!/usr/bin/env python3
"""
Web Interface for EFFICODE-ACRR Code Optimizer
Simple HTML/CSS/JS interface for code optimization
"""

from flask import Flask, render_template, request, jsonify
from complete_ml_optimizer import CompleteMlOptimizer
from ast_code_transformer import ASTCodeTransformer
import json
import time

app = Flask(__name__)

# Initialize optimizers
ml_optimizer = CompleteMlOptimizer()
ast_transformer = ASTCodeTransformer()

@app.route('/')
def index():
    """Main page"""
    return render_template('optimizer.html')

@app.route('/api/optimize', methods=['POST'])
def optimize_code():
    """API endpoint for code optimization"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({'error': 'No code provided'}), 400
        
        start_time = time.time()
        
        # Use ML optimizer for analysis
        ml_result = ml_optimizer.optimize_code(code)
        
        # Use AST transformer for better code generation
        ast_pattern = ast_transformer.detect_optimization_pattern(code)
        if ast_pattern:
            optimized_code = ast_transformer.transform_code(code, ml_result['ml_analysis']['predicted_technique'])
        else:
            optimized_code = ml_result['optimized_code']
        
        processing_time = time.time() - start_time
        
        response = {
            'success': True,
            'original_code': code,
            'optimized_code': optimized_code,
            'analysis': {
                'technique': ml_result['ml_analysis']['predicted_technique'],
                'confidence': f"{ml_result['ml_analysis']['confidence']:.1%}",
                'pattern_detected': ast_pattern,
                'original_complexity': ml_result['complexity_analysis']['original']['time'],
                'optimized_complexity': ml_result['complexity_analysis']['optimized']['time'],
                'data_structure': ml_result['optimization_details']['data_structure'],
                'speedup': ml_result['performance_improvement']['speedup_description']
            },
            'processing_time': f"{processing_time:.3f}s"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/examples')
def get_examples():
    """Get sample code examples"""
    examples = {
        'two_sum': {
            'title': 'Two Sum Problem',
            'code': '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []''',
            'description': 'Find two numbers that add up to target'
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
        },
        'longest_substring': {
            'title': 'Longest Substring Without Repeating Characters',
            'code': '''def lengthOfLongestSubstring(s):
    max_len = 0
    for i in range(len(s)):
        seen = set()
        for j in range(i, len(s)):
            if s[j] in seen:
                break
            seen.add(s[j])
            max_len = max(max_len, j - i + 1)
    return max_len''',
            'description': 'Find length of longest substring without repeating characters'
        }
    }
    
    return jsonify(examples)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)