#!/usr/bin/env python
"""
Simple EFFICODE server for testing code optimization
"""

import os
import sys
import logging
import json
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, backend_dir)
sys.path.insert(0, src_dir)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Simple rule-based optimizer class
class SimpleOptimizer:
    def __init__(self):
        self.applied_rules = []
    
    def optimize(self, code, level='medium'):
        """Simple optimization that demonstrates the concept"""
        self.applied_rules = []
        optimized_code = code
        
        # Simple optimizations
        if 'fibonacci' in code and 'fibonacci(n-1) + fibonacci(n-2)' in code:
            # Replace recursive fibonacci with iterative
            optimized_code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    # Optimized iterative approach
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b
"""
            self.applied_rules.append({
                'type': 'algorithm_replacement',
                'description': 'Replaced recursive Fibonacci with iterative implementation',
                'category': 'performance'
            })
            return optimized_code, "O(2^n)", "O(n)", "Replaced exponential recursive algorithm with linear iterative approach"
        
        # Simple constant folding
        if '2 * 3' in code:
            optimized_code = code.replace('2 * 3', '6')
            self.applied_rules.append({
                'type': 'constant_folding',
                'description': 'Folded constant expression 2 * 3 to 6',
                'category': 'optimization'
            })
        
        if '10 / 2' in code:
            optimized_code = optimized_code.replace('10 / 2', '5.0')
            self.applied_rules.append({
                'type': 'constant_folding',
                'description': 'Folded constant expression 10 / 2 to 5.0',
                'category': 'optimization'
            })
        
        if '2 ** 8' in code:
            optimized_code = optimized_code.replace('2 ** 8', '256')
            self.applied_rules.append({
                'type': 'constant_folding',
                'description': 'Folded constant expression 2 ** 8 to 256',
                'category': 'optimization'
            })
        
        # Determine complexity
        original_complexity = "O(n)" if 'for' in code else "O(1)"
        optimized_complexity = original_complexity
        
        if self.applied_rules:
            explanation = f"Applied {len(self.applied_rules)} optimizations: " + ", ".join([rule['description'] for rule in self.applied_rules])
        else:
            explanation = "No optimizations were applicable to this code."
        
        return optimized_code, original_complexity, optimized_complexity, explanation
    
    def get_applied_rules(self):
        return self.applied_rules

# Initialize optimizer
optimizer = SimpleOptimizer()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'EFFICODE Simple Server is running. Use /optimize for optimization.'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'optimizer': 'simple_rule_based'
    })

@app.route('/optimize', methods=['POST', 'OPTIONS'])
def optimize_code():
    """Optimize code endpoint"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        # Parse request
        request_data = request.get_json()
        if not request_data or 'code' not in request_data:
            return jsonify({
                'error': 'Missing required parameter: code',
                'status': 'error'
            }), 400
        
        code = request_data.get('code', '')
        level = request_data.get('level', 'medium')
        
        if not code.strip():
            return jsonify({
                'error': 'Empty code provided',
                'status': 'error'
            }), 400
        
        # Apply optimization
        optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level)
        improvements = optimizer.get_applied_rules()
        
        # Prepare response
        response = {
            'original_code': code,
            'optimized_code': optimized_code,
            'original_complexity': original_complexity,
            'optimized_complexity': optimized_complexity,
            'explanation': explanation,
            'improvements': improvements,
            'status': 'success'
        }
        
        logger.info(f"Optimization completed: {len(improvements)} improvements")
        return jsonify(response)
    
    except Exception as e:
        error_msg = f"Error in optimization: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': error_msg,
            'status': 'error'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting EFFICODE Simple Server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)