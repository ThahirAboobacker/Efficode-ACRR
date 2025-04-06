"""
EFFICODE-ACRR API Server for code optimization
"""
import os
import sys
import logging
import time
import json
import traceback
from flask import Flask, request, jsonify, Response, g
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('efficode.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import optimization components
try:
    # Try to use fixed rule-based optimizer first, fall back to original if not available
    try:
        from src.rule_based_fixed import RuleBasedOptimizer
        logger.info("Using fixed RuleBasedOptimizer")
    except ImportError:
        from src.rule_based import RuleBasedOptimizer
        logger.info("Using original RuleBasedOptimizer")
        
    from src.codebert_optimizer import CodeBERTOptimizer, apply_codebert_optimization
    from src.code_transformation import CodeTransformer
    logger.info("Successfully imported optimization components")
except ImportError as e:
    logger.error(f"Error importing optimization components: {e}")
    sys.exit(1)

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize optimizers
try:
    rule_optimizer = RuleBasedOptimizer()
    codebert_optimizer = CodeBERTOptimizer()
    code_transformer = CodeTransformer()
    logger.info("Successfully initialized all optimizers")
except Exception as e:
    logger.error(f"Error initializing optimizers: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Global debugging flag
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Load environment variables
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

@app.before_request
def before_request():
    g.start_time = time.time()
    logger.info(f"Request received: {request.endpoint}")

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        logger.info(f"Request processed in {elapsed:.2f}s")
    return response

# Direct routes
@app.route('/', methods=['GET'])
def root():
    """Root endpoint that confirms the API is working"""
    return jsonify({
        'status': 'ok',
        'message': 'EFFICODE-ACRR API is running. Use /health for health check and /optimize for optimization.'
    })

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    return jsonify({
        'status': 'ok',
        'optimizers': {
            'rule_based': bool(rule_optimizer),
            'codebert': bool(codebert_optimizer),
            'transformer': bool(code_transformer)
        }
    })

@app.route('/optimize', methods=['POST'])
@app.route('/api/optimize', methods=['POST'])
def optimize_code():
    """
    Endpoint to optimize code using available optimizers
    
    Request format:
    {
        "code": "Python code to optimize",
        "level": "low|medium|high",
        "debug": true|false,
        "mode": "auto|rule|codebert|ast",
        "optimizations": ["sorting", "search", "loop", ...]
    }
    
    Response format:
    {
        "original_code": "Original code",
        "optimized_code": "Optimized code",
        "improvements": [
            {
                "rule": "Rule name",
                "description": "Rule description",
                "category": "Category"
            }
        ],
        "performance": {
            "time_taken": 0.123,
            "optimization_count": 5
        },
        "errors": ["Error messages if any"]
    }
    """
    start_time = time.time()
    logger.info("Received optimization request")
    
    try:
        # Parse request
        try:
            request_data = request.get_json()
            logger.info(f"Parsed request data: {bool(request_data)}")
        except Exception as e:
            logger.error(f"Error parsing JSON request: {e}")
            return jsonify({
                'error': f'Invalid JSON in request: {str(e)}',
                'status': 'error',
                'original_code': '',
                'optimized_code': '',
                'explanation': f'Error parsing request: {str(e)}',
                'processing_time': time.time() - start_time
            }), 400
        
        if not request_data or 'code' not in request_data:
            logger.error("Missing required parameter: code")
            return jsonify({
                'error': 'Missing required parameter: code',
                'status': 'error',
                'original_code': '',
                'optimized_code': '',
                'explanation': 'No code was provided for optimization.',
                'processing_time': time.time() - start_time
            }), 400
        
        # Extract parameters with defaults
        code = request_data.get('code', '')
        level = request_data.get('level', 'medium')
        debug = request_data.get('debug', DEBUG)
        mode = request_data.get('mode', 'auto')
        optimizations = request_data.get('optimizations', ['all'])
        
        # Validate code
        if not code.strip():
            logger.error("Empty code provided")
            return jsonify({
                'error': 'Empty code provided',
                'status': 'error',
                'original_code': '',
                'optimized_code': '',
                'explanation': 'Empty code was provided. Please enter some Python code to optimize.',
                'processing_time': time.time() - start_time
            }), 400
        
        # Initialize result variables
        optimized_code = code
        improvements = []
        all_errors = []
        optimization_time = 0
        optimization_count = 0
        
        # Log request if debug is enabled
        if debug:
            logger.info(f"Optimization parameters: mode={mode}, level={level}")
            
        # Apply optimizations based on mode
        try:
            # Apply rule-based optimization first in auto or rule mode
            if mode in ['auto', 'rule']:
                if debug:
                    logger.info("Starting rule-based optimization")
                
                # Apply rule-based optimization
                rule_start = time.time()
                try:
                    optimized_code, original_complexity, optimized_complexity, rule_explanation = rule_optimizer.optimize(code, level=level)
                    logger.info("Rule-based optimization completed")
                except Exception as e:
                    error_msg = f"Error in rule-based optimization: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    all_errors.append(error_msg)
                    # Continue with original code
                    optimized_code = code
                    original_complexity = "O(?)"
                    optimized_complexity = "O(?)"
                    rule_explanation = f"Error in optimization: {str(e)}"
                
                rule_time = time.time() - rule_start
                
                # Get improvements from rule-based optimizer
                try:
                    rule_improvements = rule_optimizer.get_applied_rules()
                    improvements.extend(rule_improvements)
                    optimization_time += rule_time
                    optimization_count += len(rule_improvements)
                    
                    if debug:
                        logger.info(f"Rule-based optimization: {len(rule_improvements)} improvements in {rule_time:.3f}s")
                except Exception as e:
                    error_msg = f"Error getting rule-based improvements: {str(e)}"
                    logger.error(error_msg)
                    all_errors.append(error_msg)
                
                # If we already have optimizations and mode is not auto, return early
                if improvements and mode != 'auto':
                    logger.info("Early return after successful rule-based optimization")
                    code = optimized_code  # Update code for next optimization if needed
            
            # Apply CodeBERT optimization in auto or codebert mode
            if mode in ['auto', 'codebert']:
                if debug:
                    logger.info("Starting CodeBERT optimization")
                
                # Apply CodeBERT optimization
                codebert_start = time.time()
                codebert_improvements = []
                codebert_errors = []
                
                try:
                    optimized_code, codebert_improvements, codebert_errors = apply_codebert_optimization(
                        optimized_code, level
                    )
                    logger.info("CodeBERT optimization completed")
                except Exception as e:
                    error_msg = f"Error in CodeBERT optimization: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    all_errors.append(error_msg)
                
                codebert_time = time.time() - codebert_start
                
                # Add improvements and errors
                improvements.extend(codebert_improvements)
                all_errors.extend(codebert_errors)
                optimization_time += codebert_time
                optimization_count += len(codebert_improvements)
                
                if debug:
                    logger.info(f"CodeBERT optimization: {len(codebert_improvements)} improvements in {codebert_time:.3f}s")
                
                # If we already have optimizations and mode is not auto, return early
                if codebert_improvements and mode != 'auto':
                    logger.info("Early return after successful CodeBERT optimization")
                    code = optimized_code  # Update code for next optimization if needed
            
            # Apply AST transformation in auto or ast mode
            if mode in ['auto', 'ast']:
                if debug:
                    logger.info("Starting AST transformation")
                
                # Apply AST transformation
                ast_start = time.time()
                parse_errors = []
                transform_errors = []
                generate_errors = []
                
                # Parse code into AST
                try:
                    ast_tree, parse_errors = code_transformer.parse_code(optimized_code)
                    all_errors.extend(parse_errors)
                    
                    if ast_tree:
                        # Transform AST
                        transformed_ast, transform_errors = code_transformer.transform_code(
                            ast_tree, optimizations
                        )
                        all_errors.extend(transform_errors)
                        
                        if transformed_ast:
                            # Generate optimized code
                            optimized_code, generate_errors = code_transformer.generate_optimized_code(transformed_ast)
                            all_errors.extend(generate_errors)
                            logger.info("AST transformation completed")
                except Exception as e:
                    error_msg = f"Error in AST transformation: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    all_errors.append(error_msg)
                
                ast_time = time.time() - ast_start
                optimization_time += ast_time
                
                # Since the CodeTransformer doesn't track improvements directly,
                # we estimate based on changes in the code
                if optimized_code != code:
                    improvements.append({
                        'type': 'ast_transformation',
                        'description': 'Applied AST-based code transformations',
                        'category': 'structure'
                    })
                    optimization_count += 1
                
                if debug:
                    logger.info(f"AST transformation completed in {ast_time:.3f}s")
        
        except Exception as e:
            error_msg = f"Error during optimization process: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            all_errors.append(error_msg)
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Generate explanation from improvements
        explanation = ""
        if improvements:
            explanation_parts = []
            for i, imp in enumerate(improvements[:5]):  # First 5 improvements
                desc = imp.get('description', '')
                if desc:
                    explanation_parts.append(desc)
            
            if explanation_parts:
                explanation = "Optimizations applied: " + ", ".join(explanation_parts)
            else:
                explanation = "Code was optimized with multiple techniques."
        else:
            if all_errors:
                explanation = "Failed to optimize code. " + all_errors[0]
            else:
                explanation = "No optimizations were applicable to this code."
        
        # Determine complexity estimates
        original_complexity = "O(n)"
        optimized_complexity = "O(n)"
        
        # Apply simple heuristics for complexity
        if "fibonacci" in code and "return fibonacci(n-1) + fibonacci(n-2)" in code:
            original_complexity = "O(2^n)"
            if improvements:
                optimized_complexity = "O(n)"
        elif "sort" in code and any(s in code for s in ["bubble", "selection"]):
            original_complexity = "O(n²)"
            if improvements:
                optimized_complexity = "O(n log n)"
        elif "search" in code and "for" in code and "range" in code:
            original_complexity = "O(n)"
            if improvements and "binary" in optimized_code:
                optimized_complexity = "O(log n)"
        
        # Prepare response
        response = {
            'original_code': code,
            'optimized_code': optimized_code,
            'improvements': improvements,
            'performance': {
                'time_taken': total_time,
                'optimization_time': optimization_time,
                'optimization_count': optimization_count
            },
            'original_complexity': original_complexity,
            'optimized_complexity': optimized_complexity,
            'explanation': explanation,
            'processing_time': total_time,
            'errors': all_errors,
            'status': 'error' if (all_errors and not improvements) else 'success'
        }
        
        # Add debug information if requested
        if debug:
            response['debug'] = {
                'mode': mode,
                'level': level,
                'total_time': total_time,
                'has_errors': bool(all_errors)
            }
        
        logger.info(f"Optimization completed: {optimization_count} improvements, {len(all_errors)} errors, {total_time:.3f}s")
        return jsonify(response)
    
    except Exception as e:
        error_msg = f"Unexpected error in optimization endpoint: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Return a complete response even in case of errors
        return jsonify({
            'original_code': request.get_json().get('code', '') if request.get_json() else '',
            'optimized_code': request.get_json().get('code', '') if request.get_json() else '',
            'improvements': [],
            'performance': {
                'time_taken': time.time() - start_time,
                'optimization_time': 0,
                'optimization_count': 0
            },
            'original_complexity': 'O(?)',
            'optimized_complexity': 'O(?)',
            'explanation': f'Error processing request: {str(e)}',
            'processing_time': time.time() - start_time,
            'errors': [error_msg],
            'status': 'error'
        }), 500

# Main entry point with port configurable via environment
if __name__ == '__main__':
    logger.info(f"Starting EFFICODE-ACRR API on {HOST}:{PORT} (Debug: {DEBUG})")
    
    try:
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
        logger.error(traceback.format_exc()) 