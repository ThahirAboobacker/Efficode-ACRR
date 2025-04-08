"""
EFFICODE-ACRR API Server for code optimization
MAIN PRODUCTION SERVER - This is the primary application server
This is the main implementation that should be used for production deployments.
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

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, backend_dir)
sys.path.insert(0, src_dir)

# Import optimization components
try:
    # Use rule-based optimizer
    from src.rule_based import RuleBasedOptimizer
    logger.info("Using fixed RuleBasedOptimizer")
        
   # from src.codebert_optimizer import CodeBERTOptimizer, apply_codebert_optimization
    from src.code_transformation import CodeTransformer
    logger.info("Successfully imported optimization components")
except ImportError as e:
    logger.error(f"Error importing optimization components: {e}")
    sys.exit(1)

app = Flask(__name__)
# Enable CORS for all routes and origins with proper configuration
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Add a global OPTIONS handler
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

# Initialize optimizers
try:
    # Disable neural model by default
    #import src.codebert_optimizer
    #src.codebert_optimizer.NEURAL_MODEL_AVAILABLE = False
    
    # Configure optimizers
    rule_based_optimizer = RuleBasedOptimizer()
    #codebert_optimizer = CodeBERTOptimizer(use_neural_model=False)
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
            'rule_based': bool(rule_based_optimizer),
            'codebert': False,  # codebert is disabled
            'transformer': bool(code_transformer)
        }
    })

@app.route('/optimize', methods=['POST', 'OPTIONS'])
@app.route('/api/optimize', methods=['POST', 'OPTIONS'])
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
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
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
            # Force all optimizations to run in sequence
            # Apply rule-based optimization first
            if debug:
                logger.info("Starting rule-based optimization")
            
            # Apply rule-based optimization
            rule_start = time.time()
            try:
                # Enable all rule-based optimization features
                optimized_code, original_complexity, optimized_complexity, rule_explanation = rule_based_optimizer.optimize(code, level=level)
                
                # Add explicit optimization information
                logger.info(f"Applied rule-based optimization with level: {level}")
                logger.info(f"Original complexity: {original_complexity}, Optimized complexity: {optimized_complexity}")
                
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
                rule_improvements = rule_based_optimizer.get_applied_rules()
                
                # If no improvements detected but code was changed, add a generic improvement
                if not rule_improvements and optimized_code != code:
                    logger.info("Code was optimized but no improvements reported. Adding generic improvement.")
                    rule_improvements = [{
                        'type': 'rule_based_optimization',
                        'description': 'Code was optimized with rule-based techniques',
                        'category': 'performance'
                    }]
                    
                    # Extract information about what was optimized
                    if "# Optimized with Rule-based optimizer" in optimized_code:
                        # Check for common patterns
                        if original_complexity != optimized_complexity:
                            rule_improvements.append({
                                'type': 'complexity_improvement',
                                'description': f'Improved complexity from {original_complexity} to {optimized_complexity}',
                                'category': 'performance'
                            })
                        
                        # Check for specific optimizations
                        if len(optimized_code) < len(code):
                            rule_improvements.append({
                                'type': 'code_reduction',
                                'description': 'Reduced code size and improved readability',
                                'category': 'readability'
                            })
                
                improvements.extend(rule_improvements)
                optimization_time += rule_time
                optimization_count += len(rule_improvements)
                
                # Log detailed information about applied optimizations
                for improvement in rule_improvements:
                    improvement_type = improvement.get('type', 'unknown')
                    description = improvement.get('description', 'No description')
                    logger.info(f"Applied optimization: {improvement_type} - {description}")
                
                if debug:
                    logger.info(f"Rule-based optimization: {len(rule_improvements)} improvements in {rule_time:.3f}s")
            except Exception as e:
                error_msg = f"Error getting rule-based improvements: {str(e)}"
                logger.error(error_msg)
                all_errors.append(error_msg)
            
            # Skip all other optimizers - only use rule-based
            logger.info("Skipping CodeBERT and AST transformations as requested")
            
            # Add summary of applied optimizers
            improvements.append({
                'type': 'optimization_pipeline',
                'description': 'Code processed by rule-based optimizer only',
                'category': 'info'
            })
        
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
            
            # Categorize improvements for better explanation
            rule_based_imps = [imp for imp in improvements if 'algorithm_replacement' in imp.get('type', '')]
            codebert_imps = [imp for imp in improvements if 'codebert' in imp.get('type', '')]
            ast_imps = [imp for imp in improvements if 'ast' in imp.get('type', '')]
            performance_imps = [imp for imp in improvements if imp.get('category') == 'performance']
            
            # Add key improvements to explanation
            if rule_based_imps:
                explanation_parts.append(rule_based_imps[0]['description'])
                
            if codebert_imps:
                codebert_desc = next((imp['description'] for imp in codebert_imps if imp.get('type') != 'codebert_optimization'), 
                                    'Improved code quality with CodeBERT optimizations')
                explanation_parts.append(codebert_desc)
                
            if ast_imps:
                ast_desc = next((imp['description'] for imp in ast_imps if imp.get('type') != 'ast_transformation'), 
                                'Applied AST-based code transformations')
                # Only add AST explanation if different from above
                if ast_desc not in explanation_parts:
                    explanation_parts.append(ast_desc)
                    
            # Always add performance metrics
            performance_desc = next((imp['description'] for imp in improvements if imp.get('type') == 'performance_metrics'), 
                                  f"Processing time: {optimization_time:.2f}s")
            explanation_parts.append(performance_desc)
            
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