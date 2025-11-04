#!/usr/bin/env python3
"""
Production-Ready API for EFFICODE-ACRR
Includes authentication, rate limiting, caching, and monitoring
"""

from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import redis
import hashlib
import time
import logging
from functools import wraps
import jwt
import os
from complete_ml_optimizer import CompleteMlOptimizer
from ast_code_transformer import ASTCodeTransformer
from explainability_engine import OptimizationExplainer
from feedback_system import FeedbackSystem

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize components
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})
except:
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ML components
ml_optimizer = CompleteMlOptimizer()
ast_transformer = ASTCodeTransformer()
explainer = OptimizationExplainer()
feedback_system = FeedbackSystem()

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

def generate_cache_key(code: str) -> str:
    """Generate cache key for code optimization"""
    return f"optimization:{hashlib.md5(code.encode()).hexdigest()}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })

@app.route('/api/auth/token', methods=['POST'])
def get_token():
    """Get authentication token"""
    data = request.get_json()
    api_key = data.get('api_key')
    
    # In production, validate against database
    if api_key == 'demo-api-key':
        token = jwt.encode({
            'user_id': 'demo_user',
            'exp': time.time() + 3600  # 1 hour
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token})
    
    return jsonify({'error': 'Invalid API key'}), 401

@app.route('/api/optimize', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
def optimize_code():
    """Main optimization endpoint with caching"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        if len(code) > 10000:  # Limit code size
            return jsonify({'error': 'Code too large (max 10KB)'}), 400
        
        # Check cache
        cache_key = generate_cache_key(code)
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for optimization request")
            return jsonify(cached_result)
        
        # Process optimization
        start_time = time.time()
        
        # ML optimization
        ml_result = ml_optimizer.optimize_code(code)
        
        # AST transformation
        ast_pattern = ast_transformer.detect_optimization_pattern(code)
        if ast_pattern:
            optimized_code = ast_transformer.transform_code(code, ml_result['ml_analysis']['predicted_technique'])
        else:
            optimized_code = ml_result['optimized_code']
        
        # Generate explanation
        explanation = explainer.explain_optimization_decision(
            code,
            ml_result['ml_analysis'].get('features_used', []),
            ml_result['ml_analysis']['predicted_technique'],
            ml_result['ml_analysis']['confidence']
        )
        
        processing_time = time.time() - start_time
        
        # Prepare response
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
            'explanation': {
                'rationale': explanation['optimization_rationale'],
                'key_features': explanation['feature_importance'][:3],
                'alternatives': explanation['alternative_approaches']
            },
            'processing_time': f"{processing_time:.3f}s",
            'cached': False
        }
        
        # Cache result for 1 hour
        cache.set(cache_key, response, timeout=3600)
        
        logger.info(f"Optimization completed in {processing_time:.3f}s")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/feedback', methods=['POST'])
@limiter.limit("20 per minute")
@require_auth
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        
        optimization_result = data.get('optimization_result', {})
        user_feedback = data.get('feedback', {})
        
        feedback_id = feedback_system.collect_feedback(optimization_result, user_feedback)
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback collected successfully'
        })
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({'error': 'Failed to collect feedback'}), 500

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_statistics():
    """Get system statistics"""
    try:
        feedback_stats = feedback_system.get_statistics()
        
        # Add system stats
        stats = {
            'feedback': feedback_stats,
            'system': {
                'uptime': time.time(),
                'cache_hits': 0,  # TODO: Implement cache hit tracking
                'total_optimizations': feedback_stats['total_feedback']
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get code examples (no auth required)"""
    examples = {
        'two_sum': {
            'title': 'Two Sum Problem',
            'code': '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []''',
            'description': 'Find two numbers that add up to target',
            'expected_optimization': 'hash_map'
        },
        'contains_duplicate': {
            'title': 'Contains Duplicate',
            'code': '''def containsDuplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False''',
            'description': 'Check if array contains duplicates',
            'expected_optimization': 'hash_set'
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
            'description': 'Find maximum sum of contiguous subarray',
            'expected_optimization': 'dynamic_programming'
        }
    }
    
    return jsonify(examples)

@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit error handler"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description)
    }), 429

@app.errorhandler(500)
def internal_error(e):
    """Internal error handler"""
    logger.error(f"Internal error: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please try again later'
    }), 500

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )