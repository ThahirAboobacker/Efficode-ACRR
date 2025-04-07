import os
import sys
import time
import json
import logging
import traceback
from typing import Dict, List, Any

print("Starting app.py...")

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
print(f"Added parent directory to path: {parent_dir}")

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import logging
    import time
    from typing import Dict, Any
    from waitress import serve
    print("Successfully imported all required modules")
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Ensure log directory exists
log_dir = os.path.join(parent_dir, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'efficode.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import config, or create a minimal version if it fails
try:
    # First try to import from backend/src/config.py
    try:
        from config import Config
        logger.info("Imported Config from src/config.py")
    except ImportError:
        # Next try to import from backend/config.py
        sys.path.insert(0, parent_dir)
        from config import Config
        logger.info("Imported Config from backend/config.py")
except ImportError:
    # Create minimal config if neither exists
    logger.warning("Config not found, using minimal default configuration")
    class Config:
        """Minimal configuration"""
        API_VERSION = "1.0.0"
        MAX_CODE_LENGTH = 10000
        DEFAULT_OPTIMIZATION_LEVEL = "medium"
        LOG_FILE = os.path.join(log_dir, "efficode.log")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize models with fallbacks
try:
    # Import rule-based optimizer
    from rule_based import RuleBasedOptimizer
    rule_based_optimizer = RuleBasedOptimizer()
    logger.info("Initialized RuleBasedOptimizer successfully")
except Exception as e:
    logger.error(f"Failed to initialize RuleBasedOptimizer: {e}")
    rule_based_optimizer = None

try:
    # Import CodeBERT optimizer
    from codebert_optimizer import CodeBERTOptimizer
    codebert_optimizer = CodeBERTOptimizer()
    logger.info("Initialized CodeBERTOptimizer successfully")
except Exception as e:
    logger.error(f"Failed to initialize CodeBERTOptimizer: {e}")
    codebert_optimizer = None

# Initialize complexity analyzer
try:
    from complexity_analyzer import ComplexityAnalyzer
    complexity_analyzer = ComplexityAnalyzer()
    logger.info("Initialized ComplexityAnalyzer successfully")
except Exception as e:
    logger.error(f"Failed to initialize ComplexityAnalyzer: {e}")
    complexity_analyzer = None

# Define CORS handler decorator
def handle_cors(f):
    """Decorator to handle CORS for API endpoints"""
    def wrapped(*args, **kwargs):
        # Get the response from the original function
        response = f(*args, **kwargs)
        
        # Add CORS headers to the response
        if isinstance(response, tuple):
            resp, status = response
            headers = resp.headers
            headers['Access-Control-Allow-Origin'] = '*'
            headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return resp, status
        else:
            headers = response.headers
            headers['Access-Control-Allow-Origin'] = '*'
            headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
    
    # Preserve the original function's metadata
    wrapped.__name__ = f.__name__
    wrapped.__doc__ = f.__doc__
    
    return wrapped

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "timestamp": time.time()
    })

@app.route('/api/optimize', methods=['POST'])
@handle_cors
def optimize_code():
    """Optimize the provided code using available optimizers."""
    try:
        start_time = time.time()
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
            
        code = data['code']
        optimization_level = data.get('optimization_level', 'medium')
        
        # Validate code size
        if len(code) > Config.MAX_CODE_LENGTH:
            return jsonify({
                'error': f'Code exceeds maximum length of {Config.MAX_CODE_LENGTH} characters'
            }), 400
            
        # Analyze original complexity
        original_complexity = "Unknown"
        if complexity_analyzer:
            try:
                original_complexity = complexity_analyzer.analyze(code)
            except Exception as e:
                logger.error(f"Error analyzing original complexity: {e}")
        
        # Initialize optimization variables
        optimized_code = code
        applied_rules = []
        
        # Apply rule-based optimization
        if rule_based_optimizer:
            try:
                result = rule_based_optimizer.optimize(code, optimization_level)
                if isinstance(result, dict):
                    optimized_code = result.get('optimized_code', code)
                    applied_rules = result.get('applied_rules', [])
                else:
                    optimized_code = result.optimized_code or code
                    applied_rules = [{
                        'name': change.description,
                        'description': f"Lines {change.line_start}-{change.line_end}: {change.description}"
                    } for change in result.detailed_changes]
                logger.info(f"Applied {len(applied_rules)} rule-based optimizations")
            except Exception as e:
                logger.error(f"Error in rule-based optimization: {e}")
        
        # Apply CodeBERT optimization
        if codebert_optimizer:
            try:
                codebert_result, codebert_improvements, codebert_errors = codebert_optimizer.optimize(optimized_code, optimization_level)
                if codebert_errors:
                    logger.warning(f"CodeBERT optimization warnings: {codebert_errors}")
                if codebert_improvements:
                    optimized_code = codebert_result
                    logger.info(f"Applied {len(codebert_improvements)} CodeBERT improvements")
                else:
                    logger.info("CodeBERT optimization made no changes")
            except Exception as e:
                logger.error(f"Error in CodeBERT optimization: {e}")
        
        # Analyze optimized complexity
        optimized_complexity = "Unknown"
        if complexity_analyzer:
            try:
                optimized_complexity = complexity_analyzer.analyze(optimized_code)
            except Exception as e:
                logger.error(f"Error analyzing optimized complexity: {e}")
        
        # Generate explanation
        explanation = "Code optimization completed successfully."
        if applied_rules:
            explanation = "Applied optimizations:\n" + "\n".join(
                f"- {rule['name']}: {rule['description']}"
                for rule in applied_rules
            )
        
        return jsonify({
            'original_code': code,
            'optimized_code': optimized_code,
            'original_complexity': original_complexity,
            'optimized_complexity': optimized_complexity,
            'explanation': explanation,
            'processing_time': time.time() - start_time,
            'timestamp': int(time.time() * 1000)
        })
        
    except Exception as e:
        logger.error(f"Error during optimization: {e}")
        return jsonify({'error': str(e)}), 500

# Add a root route to provide basic information
@app.route('/', methods=['GET'])
def index():
    """API root - provides basic information"""
    return jsonify({
        "name": "EFFICODE-ACRR API",
        "version": Config.API_VERSION,
        "status": "operational",
        "endpoints": [
            {"path": "/api/optimize", "method": "POST", "description": "Optimize code"},
            {"path": "/health", "method": "GET", "description": "Health check"}
        ],
        "documentation": "See README.md for API usage details"
    })

# Add a handler for method not allowed errors
@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors with helpful message"""
    return jsonify({
        "error": "Method not allowed",
        "message": "This endpoint doesn't support this HTTP method",
        "allowed_methods": error.valid_methods
    }), 405

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Print starting message
    print("Starting Efficode server on http://0.0.0.0:5000")
    print("Press CTRL+C to stop the server")
    
    # Run the application with explicit settings
    app.run(debug=True, host='0.0.0.0', port=5000)