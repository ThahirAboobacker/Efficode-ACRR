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
# Configure CORS to allow requests from all origins
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})

# Initialize models with fallbacks
try:
    # Attempt to import the required modules
    try:
        # Try importing from models directory first
        try:
            from models.codebert_model import CodeBERTOptimizer
            logger.info("Initialized CodeBERTOptimizer from models directory")
        except ImportError:
            # Try current directory
            try:
                from codebert_optimizer import CodeBERTOptimizer
                logger.info("Initialized CodeBERTOptimizer from current directory")
            except ImportError:
                # Try src directory
                try:
                    from src.codebert_optimizer import CodeBERTOptimizer
                    logger.info("Initialized CodeBERTOptimizer from src directory")
                except ImportError:
                    raise ImportError("CodeBERTOptimizer not found in any expected location")
        
        optimizer = CodeBERTOptimizer()
        logger.info("Initialized CodeBERTOptimizer successfully")
    except (ImportError, Exception) as e:
        logger.warning(f"Failed to initialize CodeBERTOptimizer: {e}")
        # Simple fallback implementation for CodeBERTOptimizer
        class SimpleOptimizer:
            def optimize(self, code, level="medium"):
                return code
            def get_applied_rules(self):
                return []
        optimizer = SimpleOptimizer()
        logger.info("Using SimpleOptimizer as fallback")
    
    try:
        from models.flan_t5 import FlanT5ExplanationGenerator
        explanation_generator = FlanT5ExplanationGenerator()
        logger.info("Initialized FlanT5ExplanationGenerator")
    except (ImportError, Exception) as e:
        logger.warning(f"Failed to initialize FlanT5ExplanationGenerator: {e}")
        # Simple fallback implementation
        class SimpleExplanationGenerator:
            def generate_explanation(self, original_code, optimized_code, complexity_before, complexity_after, applied_rules):
                return f"Code optimized from {complexity_before} to {complexity_after}."
        explanation_generator = SimpleExplanationGenerator()
        logger.info("Using SimpleExplanationGenerator as fallback")
    
    # Import rule-based optimizer and RuleBasedOptimizer class
    try:
        # Try to import from src directory first
        try:
            from src.rule_based import apply_optimization_rules, RuleBasedOptimizer
        except ImportError:
            from rule_based import apply_optimization_rules, RuleBasedOptimizer
        logger.info("Imported rule-based optimizer")
    except (ImportError, Exception) as e:
        logger.warning(f"Failed to import rule-based optimizer: {e}")
        # Create fallback functions
        def apply_optimization_rules(code, level="medium"):
            return code
            
        class RuleBasedOptimizer:
            def optimize(self, code, level="medium"):
                return code
            def get_applied_rules(self):
                return []
        logger.info("Using fallback rule-based optimizer")
    
    # Import the complexity analyzer
    try:
        # Try to import from src directory first
        try:
            from src.complexity_analyzer import analyze_complexity, ComplexityAnalyzer
        except ImportError:
            from complexity_analyzer import analyze_complexity, ComplexityAnalyzer
        complexity_analyzer = ComplexityAnalyzer()
        logger.info("Initialized ComplexityAnalyzer")
    except (ImportError, Exception) as e:
        logger.warning(f"Failed to initialize ComplexityAnalyzer: {e}")
        # Simple fallback implementation
        class SimpleComplexityAnalyzer:
            def analyze(self, code):
                return {
                    "time_complexity": "O(n)",
                    "space_complexity": "O(n)",
                    "explanation": "Basic complexity analysis."
                }
        complexity_analyzer = SimpleComplexityAnalyzer()
        
        # Fallback for analyze_complexity
        def analyze_complexity(code):
            return "O(n)"
            
        logger.info("Using SimpleComplexityAnalyzer as fallback")
    
    try:
        # Try to import from src directory first
        try:
            from src.code_transformation import CodeTransformer
        except ImportError:
            from code_transformation import CodeTransformer
        code_transformer = CodeTransformer()
        logger.info("Initialized CodeTransformer")
    except (ImportError, Exception) as e:
        logger.warning(f"Failed to initialize CodeTransformer: {e}")
        # Simple fallback implementation
        class SimpleCodeTransformer:
            def transform(self, code):
                return True  # Always succeed for compatibility
            def parse_code(self, code):
                return code
        code_transformer = SimpleCodeTransformer()
        logger.info("Using SimpleCodeTransformer as fallback")
    
    logger.info("Models initialized successfully")
except Exception as e:
    logger.error(f"Error initializing models: {e}")
    raise

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
    """
    API endpoint to optimize code based on the provided level
    
    Expected JSON payload:
    {
        "code": "Python code as string",
        "level": "low|medium|high"
    }
    
    Returns:
    {
        "original_code": "Original code",
        "optimized_code": "Optimized code",
        "original_complexity": "O(n²)",
        "optimized_complexity": "O(n log n)",
        "optimization_method": "rule_based|codebert|none",
        "explanation": "Detailed explanation of optimizations",
        "processing_time": 0.25,
        "applied_rules": []
    }
    """
    # Set a maximum execution time for this request
    MAX_PROCESSING_TIME = 15  # seconds
    
    try:
        logger.info("Starting optimize_code endpoint processing")
        start_time = time.time()
        
        # Get the request data
        request_data = request.get_json()
        
        # Validate request data
        if not request_data or 'code' not in request_data:
            logger.error("Invalid request: missing 'code' field")
            return jsonify({'error': "Missing 'code' field"}), 400
        
        code = request_data.get('code', '')
        optimization_level = request_data.get('level', 'medium')
        
        # Check code length to avoid excessive processing
        if len(code) > 20000:  # Set a reasonable limit
            logger.warning(f"Code too large: {len(code)} characters. Limiting to first 20000.")
            code = code[:20000]
        
        # Log the request
        logger.info(f"Received optimization request: level={optimization_level}, code_length={len(code)}")
        logger.debug(f"Code snippet: {code[:100]}..." if len(code) > 100 else code)
            
        # Validate the code
        if not code or not code.strip():
            return jsonify({
                'original_code': code,
                'optimized_code': code,
                'original_complexity': 'O(1)',
                'optimized_complexity': 'O(1)',
                'optimization_method': 'none',
                'explanation': 'No code provided or code is empty.',
                'processing_time': 0,
                'applied_rules': []
            })
            
        # Analyze original code complexity
        try:
            logger.info("Analyzing original code complexity...")
            original_complexity = analyze_complexity(code)
            logger.info(f"Original complexity: {original_complexity}")
        except Exception as e:
            logger.error(f"Error analyzing complexity: {str(e)}")
            original_complexity = "O(?)"
        
        # Default response values
        optimized_code = code
        optimization_method = "none"
        applied_rules = []
        rule_based_applied_rules = []
        codebert_improvements = []
        explanation = "No applicable optimizations were found for this code."
        
        # Step 1: Apply rule-based optimization with timeout
        try:
            logger.info("Applying rule-based optimization...")
            
            # Check if we're already taking too long
            if time.time() - start_time > MAX_PROCESSING_TIME / 3:
                logger.warning("Skipping rule-based optimization due to time constraints")
            else:
                # Initialize the rule-based optimizer
                rule_optimizer = RuleBasedOptimizer()
                
                # Apply the optimizations with a timeout guard
                rule_start_time = time.time()
                
                # Apply rule-based optimization with a timeout check
                try:
                    rule_based_result = rule_optimizer.optimize(code, optimization_level)
                    
                    # Get applied rules
                    rule_based_applied_rules = rule_optimizer.get_applied_rules()
                    
                    # Always capture rule-based results, even if no changes
                    intermediate_code = rule_based_result
                    applied_rules.extend(rule_based_applied_rules)
                    
                    if rule_based_applied_rules and rule_based_result != code:
                        optimization_method = "rule_based"
                        logger.info(f"Rule-based optimization applied {len(rule_based_applied_rules)} rules in {time.time() - rule_start_time:.2f}s")
                    else:
                        logger.info("Rule-based optimization made no changes")
                        intermediate_code = code
                except Exception as e:
                    logger.error(f"Error during rule-based optimization: {str(e)}")
                    logger.error(traceback.format_exc())
                    intermediate_code = code
        except Exception as e:
            logger.error(f"Error applying rule-based optimizations: {str(e)}")
            logger.error(traceback.format_exc())
            # Continue with original code if rule-based fails
            intermediate_code = code
            
        # Check for timeout before proceeding to next step
        if time.time() - start_time > (MAX_PROCESSING_TIME * 2/3):
            logger.warning("Skipping CodeBERT optimization due to time constraints")
            optimized_code = intermediate_code
        else:
            # Step 2: Apply CodeBERT on top of rule-based results
            try:
                logger.info("Applying CodeBERT optimization...")
                # Initialize CodeBERT optimizer
                codebert_start_time = time.time()
                
                # Apply CodeBERT optimization with timeout monitoring
                try:
                    codebert_optimizer = CodeBERTOptimizer()
                    codebert_result, codebert_improvements, errors = codebert_optimizer.optimize(intermediate_code, optimization_level)
                    
                    if errors:
                        for error in errors:
                            logger.warning(f"CodeBERT optimizer error: {error}")
                    
                    if codebert_improvements and codebert_result != intermediate_code:
                        # CodeBERT made additional improvements
                        optimized_code = codebert_result
                        
                        # Update optimization method to indicate both were used
                        if optimization_method == "rule_based":
                            optimization_method = "rule_based+codebert"
                        else:
                            optimization_method = "codebert"
                        
                        logger.info(f"CodeBERT optimization applied {len(codebert_improvements)} improvements in {time.time() - codebert_start_time:.2f}s")
                    else:
                        # If CodeBERT made no changes, use the intermediate code
                        optimized_code = intermediate_code
                        logger.info("CodeBERT optimization made no additional changes")
                except Exception as e:
                    logger.error(f"Error in CodeBERT processing: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Use intermediate code if an error occurs
                    optimized_code = intermediate_code
            except Exception as e:
                logger.error(f"Error applying CodeBERT optimizations: {str(e)}")
                logger.error(traceback.format_exc())
                # Use the intermediate code if CodeBERT fails
                optimized_code = intermediate_code
        
        # Analyze optimized code complexity
        try:
            logger.info("Analyzing optimized code complexity...")
            optimized_complexity = analyze_complexity(optimized_code)
            logger.info(f"Optimized complexity: {optimized_complexity}")
        except Exception as e:
            logger.error(f"Error analyzing optimized complexity: {str(e)}")
            optimized_complexity = original_complexity
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logger.info(f"Completed optimization in {processing_time:.2f}s using method: {optimization_method}")
        
        # Ensure we are within the maximum processing time
        if processing_time > MAX_PROCESSING_TIME:
            logger.warning(f"Optimization took longer than expected: {processing_time:.2f}s")
        
        # Prepare explanation
        if optimization_method != "none":
            explanation = f"Code optimized from {original_complexity} to {optimized_complexity} complexity."
            if rule_based_applied_rules:
                explanation += f" Applied {len(rule_based_applied_rules)} optimization rules."
            if codebert_improvements:
                explanation += f" Applied {len(codebert_improvements)} CodeBERT improvements."
        
        return jsonify({
            'original_code': code,
            'optimized_code': optimized_code,
            'original_complexity': original_complexity,
            'optimized_complexity': optimized_complexity,
            'optimization_method': optimization_method,
            'explanation': explanation,
            'processing_time': processing_time,
            'applied_rules': applied_rules
        })
    except Exception as e:
        # Catch any unexpected exceptions and return a proper response
        elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
        logger.error(f"Unhandled error in optimize_code after {elapsed_time:.2f}s: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Ensure we return a proper response
        return jsonify({
            'status': 'error',
            'error': f"Optimization failed: {str(e)}",
            'original_code': code if 'code' in locals() else "",
            'optimized_code': code if 'code' in locals() else "",
            'optimization_method': 'none',
            'explanation': f"An error occurred during optimization: {str(e)}",
            'processing_time': elapsed_time
        }), 500

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
    port = int(os.environ.get('PORT', 5500))
    print(f"Starting server on port {port}...")
    
    try:
        # Always run in development mode for testing
        print("Starting in development mode...")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        logger.error(f"Error starting server: {e}", exc_info=True)