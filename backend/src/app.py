import os
import sys
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
from typing import Dict, Any
from waitress import serve

# Now imports will work
from models.codebert_model import CodeBERTOptimizer
from models.flan_t5 import FlanT5ExplanationGenerator
from complexity_analyzer import ComplexityAnalyzer
from code_transformation import CodeTransformer
from config import Config

# Make sure the log directory exists before configuring logging
log_dir = os.path.dirname(Config.LOG_FILE)
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# Now configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize models
try:
    optimizer = CodeBERTOptimizer()
    explanation_generator = FlanT5ExplanationGenerator()
    complexity_analyzer = ComplexityAnalyzer()
    code_transformer = CodeTransformer()
    logger.info("Models initialized successfully")
except Exception as e:
    logger.error(f"Error initializing models: {e}")
    raise

@app.route('/health', methods=['GET'])
def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": Config.API_VERSION
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_code() -> Dict[str, Any]:
    """Main optimization endpoint"""
    try:
        # Get and validate input
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON in request"}), 400
            
        code = data.get('code')
        if not code:
            return jsonify({"error": "No code provided"}), 400
            
        optimization_level = data.get('optimization_level', Config.DEFAULT_OPTIMIZATION_LEVEL)
        if optimization_level not in ['low', 'medium', 'high']:
            return jsonify({"error": "Invalid optimization level"}), 400
            
        # Check code length
        if len(code) > Config.MAX_CODE_LENGTH:
            return jsonify({"error": f"Code exceeds maximum length of {Config.MAX_CODE_LENGTH} characters"}), 400

        # Validate code format
        try:
            if not code_transformer.transform(code):
                return jsonify({"error": "Invalid code format"}), 400
        except Exception as e:
            logger.error(f"Code validation error: {e}")
            return jsonify({"error": "Code validation failed"}), 400

        # Start timing
        start_time = time.time()

        # Analyze original complexity
        try:
            original_complexity = complexity_analyzer.analyze(code)
        except Exception as e:
            logger.error(f"Complexity analysis error: {e}")
            return jsonify({"error": "Failed to analyze code complexity"}), 500

        # Optimize code
        try:
            optimized_code = optimizer.optimize(code, level=optimization_level)
        except Exception as e:
            logger.error(f"Code optimization error: {e}")
            return jsonify({
                "error": "Code optimization failed",
                "original_code": code,
                "original_complexity": original_complexity
            }), 500

        # Analyze optimized complexity
        try:
            optimized_complexity = complexity_analyzer.analyze(optimized_code)
        except Exception as e:
            logger.error(f"Optimized complexity analysis error: {e}")
            optimized_complexity = "Unknown"

        # Generate explanation
        try:
            explanation = explanation_generator.generate_explanation(
                original_code=code,
                optimized_code=optimized_code,
                complexity_before=original_complexity,
                complexity_after=optimized_complexity,
                applied_rules=optimizer.get_applied_rules()
            )
        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            explanation = "Explanation generation failed."

        # Calculate processing time
        processing_time = time.time() - start_time

        # Prepare response
        response = {
            "original_code": code,
            "optimized_code": optimized_code,
            "original_complexity": original_complexity,
            "optimized_complexity": optimized_complexity,
            "explanation": explanation,
            "processing_time": processing_time,
            "timestamp": time.time(),
            "optimization_level": optimization_level
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Unexpected error in code optimization: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

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
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('waitress')
    logger.info('Starting production server...')

    serve(app, host='0.0.0.0', port=5000)